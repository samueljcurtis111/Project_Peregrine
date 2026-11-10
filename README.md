# Peregrine Synthetic Dataset Generator

Peregrine is a small project for generating synthetic question-and-answer data for instruction tuning. It uses randomized prompt templates and an Ollama model exposed through an OpenAI-compatible API.

The project currently generates two dataset types:

- **General:** everyday questions, explanations, reasoning, and other assistant tasks.
- **Code:** programming tasks across a range of languages, topics, and difficulty levels.

The prompt generator currently samples general tasks 60% of the time and coding tasks 40% of the time. Generated records use JSONL with exactly two fields: `question` and `answer`.

## How it fits together

1. **Kaggle hosts Ollama.** Run [`kaggle/ollama_server.ipynb`](kaggle/ollama_server.ipynb) with internet access and a GPU accelerator. The notebook installs Ollama, pulls the configured model, and exposes its API through an authenticated ngrok tunnel.
2. **The generator creates examples.** `dataset_generator/prompt.py` builds a randomized general or coding prompt. `dataset_generator/generator.py` sends it to the Ollama endpoint using the OpenAI Python client and saves the returned JSON object.
3. **The cleanup scripts prepare the JSONL.** Run the deduplication script and then the validator on each dataset type.

This repository contains the generator and Kaggle setup—not foundation-model training code, tokenizer experiments, or a copy of the source corpora.

## Setup

Use Python 3.10 or newer on the machine where you want to run the generator.

```bash
python -m venv .venv
```

Activate the virtual environment, then install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## Start the Kaggle model server

1. Open `kaggle/ollama_server.ipynb` in Kaggle.
2. In notebook settings, enable internet and select a GPU accelerator. Select dual T4 GPUs when that option is available to your account.
3. Add these two Kaggle secrets:
   - `NGROK_AUTH_TOKEN`: your ngrok authentication token.
   - `OLLAMA_TUNNEL_PASSWORD`: a strong password used to protect the tunnel.
4. Run the notebook cells in order. It installs and starts Ollama, pulls `qwen3.6:35b`, and prints an HTTPS API URL ending in `/v1`.

Keep the tunnel URL and password private. Do not commit either value or put secrets directly in the notebook.

## Run the generator

On the machine running this repository, set the URL printed by Kaggle and the same tunnel password.

**macOS / Linux**

```bash
export OLLAMA_API_URL="https://your-ngrok-host/v1"
export OLLAMA_TUNNEL_PASSWORD="your-tunnel-password"
export OLLAMA_MODEL="qwen3.6:35b"
python -m dataset_generator.generator
```

**Windows PowerShell**

```powershell
$env:OLLAMA_API_URL = "https://your-ngrok-host/v1"
$env:OLLAMA_TUNNEL_PASSWORD = "your-tunnel-password"
$env:OLLAMA_MODEL = "qwen3.6:35b"
python -m dataset_generator.generator
```

The defaults are 10,000 successful examples and up to 12,000 attempts. Override them with `TARGET_EXAMPLES` and `MAX_ATTEMPTS` environment variables. The model can be changed with `OLLAMA_MODEL`.

Generated files are written under `output/`:

- `output/general.jsonl`
- `output/code.jsonl`

Each line is one JSON object containing a non-empty `question` and `answer`.

## Deduplicate and validate

Run these from the repository root after generation:

```bash
python -m dataset_generator.deduplicate general
python -m dataset_generator.validate general

python -m dataset_generator.deduplicate code
python -m dataset_generator.validate code
```

The scripts create:

- `output/<type>_unique.jsonl`
- `output/<type>_validated.jsonl`

They keep the original generated files intact. Re-running either step replaces its derived output file.

## Repository layout

```text
.
├── dataset_generator/
│   ├── generator.py
│   ├── prompt.py
│   ├── deduplicate.py
│   └── validate.py
├── kaggle/
│   └── ollama_server.ipynb
├── docs/
│   └── generation-journal.md
├── output/                 # generated locally; ignored by Git
├── requirements.txt
└── README.md
```

## Notes

- The generator expects an Ollama server that supports the OpenAI-compatible chat completions endpoint and JSON response format.
- A tunnel connection does not make the endpoint safe to publish. Use a unique password and stop the Kaggle session when generation is finished.
- Generated examples are synthetic and should be reviewed before they are used for training. JSON validation and deduplication do not verify factual accuracy, code correctness, licensing, or dataset suitability.
