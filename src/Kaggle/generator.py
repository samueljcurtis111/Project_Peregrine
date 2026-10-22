import json
import time
from pathlib import Path
from openai import OpenAI
import prompt





client = OpenAI(
    base_url="url_here",
    api_key="ollama"
)

def generate_example():
    response = client.chat.completions.create(
        model="qwen3.6:35b",
        messages=[
            {"role": "user", "content": prompt.generate_prompt()}
        ]
    )

    content = response.choices[0].message.content



    example = json.loads(content)

    if isinstance(example, dict):      
        question = example.get("question")
        answer = example.get("answer")

        if not isinstance(question, str) or not question.strip():
            raise ValueError("Missing question")


        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("Missing answer")

        return {
            "question": question.strip(),
            "answer": answer.strip()
        }
    else:
        raise ValueError("Qwen did not return a JSON object")


def save_example(example):
    with open("output.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(example) + "\n")


def main():
    target = 100
    sucesses = 0
    attempts = 0

    while sucesses < target and attempts < 150:
        try:
            gen_example_result = generate_example()
            save_example(gen_example_result)
            print("Saved")
            sucesses += 1
            attempts += 1
        except Exception as e:
            print(f"Error occurred: {e}")
            attempts += 1

    print(f"Total successful examples: {sucesses}")

if __name__ == "__main__":
    main()