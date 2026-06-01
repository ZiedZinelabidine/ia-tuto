import json
import argparse
import hashlib
from pathlib import Path
from datasets import load_dataset


SYSTEM_PROMPT = (
    "Je suis Expert Kubernetes, "
    "je vais vous aider à ressoudre vos probleme de kubernetes"
)


def clean_text(value):
    if value is None:
        return ""

    value = str(value).strip()

    prefixes = [
        "###Instruction:",
        "### Instruction:",
        "Instruction:",
        "###Response:",
        "### Response:",
        "Response:"
    ]

    for prefix in prefixes:
        if value.startswith(prefix):
            value = value[len(prefix):].strip()

    return value


def make_id(instruction, output):
    raw = f"{instruction}|{output}"
    return "k8s-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def convert_dataset(
    dataset_name,
    split,
    output_path,
    clean_json_path=None,
    max_rows=None,
    min_instruction_len=20,
    min_output_len=20,
):
    dataset = load_dataset(dataset_name, split=split)

    output_path = Path(output_path)

    if clean_json_path:
        clean_json_path = Path(clean_json_path)

    seen = set()
    clean_items = []
    written = 0
    skipped = 0
    duplicates = 0

    with output_path.open("w", encoding="utf-8") as jsonl_file:
        for index, item in enumerate(dataset):
            if max_rows is not None and index >= max_rows:
                break

            instruction = clean_text(item.get("instruction", ""))
            input_text = clean_text(item.get("input", ""))
            output = clean_text(item.get("output", ""))

            if input_text:
                user_content = f"{instruction}\n\nContexte :\n{input_text}"
            else:
                user_content = instruction

            if len(user_content) < min_instruction_len or len(output) < min_output_len:
                skipped += 1
                continue

            key = (user_content, output)

            if key in seen:
                duplicates += 1
                continue

            seen.add(key)

            clean_item = {
                "id": make_id(user_content, output),
                "category": "kubernetes",
                "source": dataset_name,
                "instruction": user_content,
                "answer": output,
                "tags": ["kubernetes", "stackoverflow"]
            }

            clean_items.append(clean_item)

            qwen_sample = {
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": user_content
                    },
                    {
                        "role": "assistant",
                        "content": output
                    }
                ]
            }

            jsonl_file.write(json.dumps(qwen_sample, ensure_ascii=False) + "\n")
            written += 1

    if clean_json_path:
        with clean_json_path.open("w", encoding="utf-8") as f:
            json.dump(clean_items, f, ensure_ascii=False, indent=2)

    print(f"Dataset source : {dataset_name}")
    print(f"Split : {split}")
    print(f"Exemples Qwen2 écrits : {written}")
    print(f"Doublons supprimés : {duplicates}")
    print(f"Exemples ignorés : {skipped}")
    print(f"Fichier Qwen2 : {output_path}")

    if clean_json_path:
        print(f"Dataset propre JSON : {clean_json_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convertit un dataset Kubernetes Hugging Face vers le format Qwen2 JSONL."
    )

    parser.add_argument(
        "--dataset",
        default="dh02391735/stackoverflow-kubernetes-questions",
        help="Nom du dataset Hugging Face"
    )

    parser.add_argument(
        "--split",
        default="train",
        help="Split du dataset, ex: train"
    )

    parser.add_argument(
        "--output",
        default="qwen2_kubernetes_train.jsonl",
        help="Fichier JSONL de sortie pour Qwen2"
    )

    parser.add_argument(
        "--clean-json",
        default="k8s_dataset_clean.json",
        help="Optionnel : sauvegarde aussi une version JSON propre"
    )

    parser.add_argument(
        "--max-rows",
        type=int,
        default=None,
        help="Nombre maximum de lignes à traiter, utile pour tester"
    )

    args = parser.parse_args()

    convert_dataset(
        dataset_name=args.dataset,
        split=args.split,
        output_path=args.output,
        clean_json_path=args.clean_json,
        max_rows=args.max_rows
    )