import json
import argparse
from pathlib import Path


def dedupe_dataset(input_path, output_path):
    input_path = Path(input_path)
    output_path = Path(output_path)

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    seen = set()
    deduped = []

    for item in data:
        instruction = item.get("instruction", "").strip()
        answer = item.get("answer", "").strip()

        # Ignore les lignes incomplètes
        if not instruction or not answer:
            continue

        # Un doublon = même instruction + même answer
        key = (instruction, answer)

        if key in seen:
            continue

        seen.add(key)

        deduped.append({
            "instruction": instruction,
            "answer": answer
        })

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(deduped, f, ensure_ascii=False, indent=2)

    print(f"Exemples avant nettoyage : {len(data)}")
    print(f"Exemples après nettoyage : {len(deduped)}")
    print(f"Doublons supprimés : {len(data) - len(deduped)}")
    print(f"Dataset nettoyé écrit dans : {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Supprime les doublons d'un dataset instruction/answer."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Fichier JSON source, ex: dataset.json"
    )

    parser.add_argument(
        "--output",
        default="dataset_clean.json",
        help="Fichier JSON nettoyé, ex: dataset_clean.json"
    )

    args = parser.parse_args()

    dedupe_dataset(args.input, args.output)