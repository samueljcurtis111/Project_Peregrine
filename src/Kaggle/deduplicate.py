import json

examples = set()

total = 0
duplicate_count = 0

with open("output.jsonl", "r", encoding="utf-8") as f:
    with open("output_unique.jsonl", "w", encoding="utf-8") as out_f:
        for line in f:
            total += 1
            example = json.loads(line)
            question = example["question"].strip().lower()
            if question in examples:
                duplicate_count += 1
                continue
            examples.add(question)
            out_f.write(json.dumps(example) + "\n")
print(f"Total examples: {total}")
print(f"Duplicate examples: {duplicate_count}")
print(f"Unique examples: {total - duplicate_count}")
