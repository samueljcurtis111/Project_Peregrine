import json

input_path = r"C:\Users\stuar\OneDrive\Documents\Project_Peregrine\datasets\code\cpp.jsonl"
output_path = r"C:\Users\stuar\OneDrive\Documents\Project_Peregrine\src\tokenizer\extracted_texts.txt"

with open(input_path, "r", encoding="utf-8") as infile, open(
    output_path, "w", encoding="utf-8"
) as outfile:
  for line in infile:
    line = line.strip()
    if not line:
      continue
    data = json.loads(line)

    text_content = data.get("text")

    if text_content:
      outfile.write(text_content)
