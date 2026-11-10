import json
import sys
from pathlib import Path


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"general", "code"}:
        raise SystemExit("Usage: python -m dataset_generator.deduplicate <general|code>")

    dataset_type = sys.argv[1]
    input_path = OUTPUT_DIR / f"{dataset_type}.jsonl"
    output_path = OUTPUT_DIR / f"{dataset_type}_unique.jsonl"

    if not input_path.is_file():
        raise FileNotFoundError(f"Input dataset not found: {input_path}")

    seen_questions = set()
    total = 0
    duplicate_count = 0
    invalid_count = 0

    with input_path.open("r", encoding="utf-8") as input_file, output_path.open(
        "w", encoding="utf-8"
    ) as output_file:
        for line in input_file:
            total += 1

            try:
                example = json.loads(line)
            except json.JSONDecodeError:
                invalid_count += 1
                continue

            if not isinstance(example, dict):
                invalid_count += 1
                continue

            question = example.get("question")
            answer = example.get("answer")
            if (
                not isinstance(question, str)
                or not question.strip()
                or not isinstance(answer, str)
                or not answer.strip()
            ):
                invalid_count += 1
                continue

            normalized_question = question.strip().casefold()
            if normalized_question in seen_questions:
                duplicate_count += 1
                continue

            seen_questions.add(normalized_question)
            output_file.write(
                json.dumps(
                    {"question": question.strip(), "answer": answer.strip()},
                    ensure_ascii=False,
                )
                + "\n"
            )

    print(f"Total records: {total}")
    print(f"Invalid records: {invalid_count}")
    print(f"Duplicate questions: {duplicate_count}")
    print(f"Unique records: {len(seen_questions)}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
