import json
import argparse
from pathlib import Path


SYSTEM_PROMPT = (
    "Je suis Expert Kubernetes, "
    "je vais vous aider à ressoudre vos probleme de kubernetes"
)


def convert_to_qwen2_jsonl(input_path, output_path):
    input_path = Path(input_path)
    output_path = Path(output_path)

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    with output_path.open("w", encoding="utf-8") as f:
        for item in data:
            instruction = item.get("instruction", "").strip()
            answer = item.get("answer", "").strip()

            if not instruction or not answer:
                continue

            sample = {
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": instruction
                    },
                    {
                        "role": "assistant",
                        "content": answer
                    }
                ]
            }

            f.write(json.dumps(sample, ensure_ascii=False) + "\n")

    print(f"Conversion terminée : {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="qwen2_train.jsonl")

    args = parser.parse_args()

    convert_to_qwen2_jsonl(args.input, args.output)