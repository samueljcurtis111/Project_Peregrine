import json
import os
import time
from pathlib import Path

import httpx
from openai import OpenAI

from . import prompt


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
DEFAULT_MODEL = "qwen3.6:35b"


client = OpenAI(
    base_url=os.environ["OLLAMA_API_URL"],
    api_key="ollama",
    http_client=httpx.Client(
        auth=httpx.BasicAuth(
            "peregrine",
            os.environ["OLLAMA_TUNNEL_PASSWORD"],
        )
    ),
)


def generate_example():
    dataset_type, prompt_text = prompt.generate_prompt()

    response = client.chat.completions.create(
        response_format={"type": "json_object"},
        model=os.getenv("OLLAMA_MODEL", DEFAULT_MODEL),
        messages=[{"role": "user", "content": prompt_text}],
    )

    content = response.choices[0].message.content
    example = json.loads(content or "")

    if not isinstance(example, dict):
        raise ValueError("The model did not return a JSON object")

    question = example.get("question")
    answer = example.get("answer")

    if not isinstance(question, str) or not question.strip():
        raise ValueError("Missing or empty question")

    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("Missing or empty answer")

    if dataset_type not in {"general", "code"}:
        raise ValueError(f"Unsupported dataset type: {dataset_type}")

    return dataset_type, {
        "question": question.strip(),
        "answer": answer.strip(),
    }


def save_example(example, dataset_type):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{dataset_type}.jsonl"

    with output_path.open("a", encoding="utf-8") as output_file:
        output_file.write(json.dumps(example, ensure_ascii=False) + "\n")


def main():
    target = int(os.getenv("TARGET_EXAMPLES", "10000"))
    max_attempts = int(os.getenv("MAX_ATTEMPTS", "12000"))
    successes = 0
    attempts = 0

    if target < 1:
        raise ValueError("TARGET_EXAMPLES must be at least 1")
    if max_attempts < target:
        raise ValueError("MAX_ATTEMPTS must be greater than or equal to TARGET_EXAMPLES")

    while successes < target and attempts < max_attempts:
        attempts += 1

        try:
            dataset_type, example = generate_example()
            save_example(example, dataset_type)
            successes += 1
            print(
                f"Saved {successes}/{target} "
                f"({dataset_type}; attempt {attempts}/{max_attempts})",
                flush=True,
            )
        except Exception as error:
            print(f"Attempt {attempts} failed: {error}", flush=True)
            if attempts < max_attempts:
                time.sleep(5)

    print(f"Successful examples: {successes}")
    print(f"Total attempts: {attempts}")


if __name__ == "__main__":
    main()
