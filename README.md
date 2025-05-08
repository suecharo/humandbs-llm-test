# humandbs-llm-test

## Models

- "huggingface lightweight llm chat cpu" みたいな感じで検索してみた
- token 数など現時点では何もわからん
- model 候補:
  - TinyLlama
    - <https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0>
    - <https://github.com/jzhang38/TinyLlama>
  - phi2

## Test Data

- [`./humandbs_llm_test/filtering_and_qc_values.json`](./humandbs_llm_test/filtering_and_qc_values.json)
  - Joomla! HTML を parse して、mol data のうち、以下の key に該当するもの

```json
[
  "Filtering",
  "QC/Filtering Methods",
  "フィルタリング",
  "Filtering Methods",
  "Filtering Methods (normalization, QC)",
  "QC",
  "QC Methods",
  "QC methods",
]
```

## Quick Start

```bash
docker compose up -d --build
docker compose exec app bash
python3 ./humandbs_llm_test/<something_script_file>.py

# e.g.,
python3 ./humandbs_llm_test/local_llm.py
```

## Memo

- phi2, llama は、あまりうまくいかなかった
