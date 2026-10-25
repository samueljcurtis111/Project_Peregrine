
import json
from pathlib import Path
from datasets import load_dataset

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "datasets" / "code"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LANGUAGES = LANGUAGES = ["python", "cpp", "rust", "java", "javascript"]
BYTES_PER_LANGUAGE = 20_000_000  # 20 MB each


def clean_code(text):
    if not isinstance(text, str):
        return None

    # Don't strip indentation or remove newlines.
    if len(text) < 100:
        return None

    if len(text) > 500_000:
        return None

    if "\x00" in text:
        return None

    return text


def save_language(language):
    print(f"\nCollecting {language}...")

    dataset = load_dataset(
        "bigcode/the-stack-dedup",
        data_dir=f"data/{language}",
        split="train",
        streaming=True
    )

    output_file = OUTPUT_DIR / f"{language.replace('+', 'p')}.jsonl"

    saved_bytes = 0
    accepted = 0

    with open(output_file, "w", encoding="utf-8") as f:
        for row in dataset:
            code = clean_code(row.get("content"))

            if code is None:
                continue

            size = len(code.encode("utf-8"))

            f.write(json.dumps({
                "text": code,
                "language": language
            }, ensure_ascii=False) + "\n")

            saved_bytes += size
            accepted += 1

            if accepted % 500 == 0:
                print(
                    f"{language}: {saved_bytes / 1_000_000:.1f} MB "
                    f"| {accepted:,} files",
                    flush=True
                )

            if saved_bytes >= BYTES_PER_LANGUAGE:
                break

    print(f"Finished {language}: {saved_bytes / 1_000_000:.1f} MB")


for language in LANGUAGES:
    save_language(language)

print("\nCoding dataset collection complete!")
