import json
import sys

dataset_type = sys.argv[1]

valid_count = 0
invalid_count = 0

with open(f"{dataset_type}_unique.jsonl", "r", encoding="utf-8") as f:
    with open(f"{dataset_type}_validated.jsonl", "x", encoding="utf-8") as out_f:
        for line in f:
            try:
                example = json.loads(line)
                if not isinstance(example, dict):
                    raise ValueError("Expected a JSON object")
                question = example.get("question")
                answer = example.get("answer")

                if not isinstance(question, str) or not question.strip():
                    raise ValueError("Missing question")
                    

                if not isinstance(answer, str) or not answer.strip():
                    raise ValueError("Missing answer")

                valid_count += 1
                out_f.write(json.dumps(example) + "\n")
            except (ValueError, TypeError, KeyError) as e:
                print(f"Invalid: {e}")
                invalid_count += 1

print(f"Valid examples: {valid_count}")
print(f"Invalid examples: {invalid_count}")
print(f"Total examples: {valid_count + invalid_count}")
