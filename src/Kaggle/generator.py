from openai import OpenAI
import prompt

client = OpenAI(
    base_url="url_here",
    api_key="ollama"
)

response = client.chat.completions.create(
    model="qwen3.6:35b",
    messages=[
        {"role": "user", "content": f"{prompt.prompt}"}
    ]
)

print(response.choices[0].message.content)
