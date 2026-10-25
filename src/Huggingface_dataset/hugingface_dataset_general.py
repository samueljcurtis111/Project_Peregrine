import json
import os
from datasets import load_dataset


fineweb = load_dataset(
    "HuggingFaceFW/fineweb-edu",
    name="sample-100BT",
    split="train",
    streaming=True
)

wikipedia = load_dataset(
    "wikimedia/wikipedia",
    "20231101.en",
    split="train",
    streaming=True
)

def clean_general(text):
    if not isinstance(text, str):
        return None

    text = text.strip()

    if len(text) < 500:
        return None

    if len(set(text)) < 20:
        return None

    if "\x00" in text:
        return None

    return text


def filter_fineweb(row):
    if row.get("score", 0) < 4:
        return None

    return clean_general(row["text"])


def filter_wikipedia(row):
    if "(disambiguation)" in row.get("title", "").lower():
        return None

    return clean_general(row["text"])


def save_stream(dataset, filter_func, output_file, max_documents=10000):
    accepted = 0
    scanned = 0

    with open(output_file, "w", encoding="utf-8") as f:
        for row in dataset:
            scanned += 1

            text = filter_func(row)

            if text is None:
                continue

            f.write(json.dumps(
                {"text": text},
                ensure_ascii=False
            ) + "\n")

            accepted += 1

            if accepted % 1000 == 0:
                print(
                    f"Accepted: {accepted:,} | "
                    f"Scanned: {scanned:,}",
                    flush=True
                )

            if accepted >= max_documents:
                break

    print(f"Finished: {output_file}")

os.makedirs("datasets/general", exist_ok=True)

save_stream(
    fineweb,
    filter_fineweb,
    "datasets/general/fineweb.jsonl",
    max_documents=25000
)

save_stream(
    wikipedia,
    filter_wikipedia,
    "datasets/general/wikipedia.jsonl",
    max_documents=5000
)