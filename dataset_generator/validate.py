import json
import sys
from pathlib import Path


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"general", "code"}:
        raise SystemExit("Usage: python -m dataset_generator.validate <general|code>")

    dataset_type = sys.argv[1]
    input_path = OUTPUT_DIR / f"{dataset_type}_unique.jsonl"
    output_path = OUTPUT_DIR / f"{dataset_type}_validated.jsonl"

    if not input_path.is_file():
        raise FileNotFoundError(
            f"Deduplicated input not found: {input_path}. "
            "Run the deduplication step first."
        )

    valid_count = 0
    invalid_count = 0

    with input_path.open("r", encoding="utf-8") as input_file, output_path.open(
        "w", encoding="utf-8"
    ) as output_file:
        for line_number, line in enumerate(input_file, start=1):
            try:
                example = json.loads(line)
                if not isinstance(example, dict):
                    raise ValueError("expected a JSON object")

                question = example.get("question")
                answer = example.get("answer")
                if not isinstance(question, str) or not question.strip():
                    raise ValueError("missing or empty question")
                if not isinstance(answer, str) or not answer.strip():
                    raise ValueError("missing or empty answer")

            except (json.JSONDecodeError, ValueError, TypeError) as error:
                print(f"Line {line_number}: {error}")
                invalid_count += 1
                continue

            output_file.write(
                json.dumps(
                    {"question": question.strip(), "answer": answer.strip()},
                    ensure_ascii=False,
                )
                + "\n"
            )
            valid_count += 1

    print(f"Valid records: {valid_count}")
    print(f"Invalid records: {invalid_count}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
