import json
import time
from pathlib import Path
from openai import OpenAI
import prompt
import os
import httpx


client = OpenAI(
    base_url=os.environ["OLLAMA_API_URL"],
    api_key="ollama",
    http_client=httpx.Client(
        auth=httpx.BasicAuth(
            "peregrine",
            os.environ["OLLAMA_TUNNEL_PASSWORD"]
        )
    )
)


def generate_example():
    dataset_type, prompt_text = prompt.generate_prompt()
    response = client.chat.completions.create(
        response_format={"type": "json_object"},
        model="qwen3.6:35b",
        messages=[
            {"role": "user", "content": prompt_text}
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

        return dataset_type, {
            "question": question.strip(),
            "answer": answer.strip()
        }
    else:
        raise ValueError("Qwen did not return a JSON object")


def save_example(example, dataset_type):
    with open(f"{dataset_type}.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(example) + "\n")


def main():
    target = 10000
    sucesses = 0
    attempts = 0

    while sucesses < target and attempts < 12000:
        try:
            dataset_type, gen_example_result = generate_example()
            save_example(gen_example_result, dataset_type)
            print("Saved")
            sucesses += 1
            attempts += 1
        except Exception as e:
            print(f"Error occurred: {e}")
            attempts += 1
            time.sleep(5)

    print(f"Total successful examples: {sucesses}")

if __name__ == "__main__":
    main()