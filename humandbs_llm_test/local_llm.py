import json
from datetime import datetime
from pathlib import Path
from typing import Set

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

HERE = Path(__file__).parent.resolve()
TEST_JSON_PATH = HERE.joinpath("filtering_and_qc_values.json")
OUTPUT_DIR_PATH = HERE.joinpath("output")


def main() -> None:
    # model_id = "microsoft/phi-2"
    model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, device_map="cpu")

    # テキスト生成パイプライン
    generator = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=256,
        do_sample=False,
    )

    prompt_template = """
    Analyze the following NGS filtering or QC description and convert it to a JSON object.
    The output must:
    - Be valid JSON, parsable by json.loads()
    - Use double quotes for all keys and strings
    - Be flat(no nested structures)
    - Contain only the JSON object — no explanation, no markdown, no extra text

    Text: "{raw_text}"

    Optional merged keys seen so far:
    {merged_keys}

    Respond ONLY with a flat JSON object, starting with '{{' and ending with '}}'.
    """.strip()

    test_data = json.loads(TEST_JSON_PATH.read_text(encoding="utf-8"))
    test_data = test_data[:10]

    merged_keys: Set[str] = set()
    results = []
    count = 0

    for item in test_data:
        try:
            hum_version_id = item["humVersionId"]
            count += 1
            print(f"[{datetime.now().isoformat()}] Processing {hum_version_id} ({count}/{len(test_data)})")
            raw_text = item["value"]
            prompt = prompt_template.format(raw_text=raw_text, merged_keys=json.dumps(list(merged_keys)))
            result = generator(prompt)[0]["generated_text"]
            result_json = json.loads(result.strip())
            for key in result_json.keys():
                merged_keys.add(key)
            results.append({
                hum_version_id: {
                    "raw_text": raw_text,
                    "result": result_json
                }
            })
        except Exception as e:
            print(f"Error processing item {item}: {e}")
            print(f"Result: {result}")
            continue

    with OUTPUT_DIR_PATH.joinpath("phi2_results.json").open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
