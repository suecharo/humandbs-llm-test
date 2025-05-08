import json
import os
from pathlib import Path

import openai

HERE = Path(__file__).parent.resolve()
TEST_JSON_PATH = HERE.joinpath("filtering_and_qc_values.json")
OUTPUT_DIR_PATH = HERE.joinpath("output")


def main() -> None:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # models = client.models.list()
    # for m in models.data:
    #     print(m.id)

    system_prompt = """
    You will receive a list of free-form texts describing filtering or quality control (QC) methods in NGS data analysis.

    Your task is to analyze the meaning of each entry and output a list of flat JSON objects (one per entry).
    Each object should contain structured information based on the input text, using appropriate field names such as `platform`, `method`, `tool`, `threshold`, etc.

    You MUST follow these constraints:
    - Each object must include the key `"humVersionId"` (passed from input)
    - Each object must include `"raw_text"` (original input text)
    - Use consistent key names across entries
    - The structure must be flat (depth = 1)
    - Output must be valid JSON parsable by `json.loads()`
    - DO NOT include any explanation, comment, or non-JSON content

    The goal is to eventually normalize all entries under a **unified JSON schema**, so please ensure consistency in field naming and structure across all outputs.
    """.strip()

    test_data = json.loads(TEST_JSON_PATH.read_text(encoding="utf-8"))
    # test_data = test_data[:50]
    results = []

    for i in range(0, len(test_data), 50):
        try:
            batch = test_data[i:i + 50]

            raw_text_map = {item["humVersionId"]: item["value"] for item in batch}

            user_prompt = f"""
            Here is the input data (a list of items with humVersionId and value):

            {json.dumps(batch, ensure_ascii=False, indent=2)}

            Respond with a list of flat JSON objects, one per item.
            """

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                max_tokens=4096,
            )

            output = response.choices[0].message.content
            if not output:
                print(f"Empty response for batch {i}-{i + 50}")
                continue

            result_json = json.loads(output)

            for item in result_json:
                hum_id = item.get("humVersionId")
                if "raw_text" not in item and hum_id in raw_text_map:
                    item["raw_text"] = raw_text_map[hum_id]

            results.extend(result_json)

        except Exception as e:
            print(f"Error processing batch {i}-{i + 50}: {e}")
            if "response" in locals():
                print(f"response: {getattr(response, 'choices', '<no choices>')}")
            continue

    OUTPUT_DIR_PATH.mkdir(parents=True, exist_ok=True)
    with OUTPUT_DIR_PATH.joinpath("open_ai_results.json").open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
