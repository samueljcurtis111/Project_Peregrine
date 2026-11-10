# Peregrine Synthetic Dataset Generator

This repository contains the synthetic question-and-answer dataset generator and the Kaggle notebook used to host its Ollama model.

The original generator, prompt templates, deduplication script, validation script, and Kaggle notebook have been moved without changing their contents.

## 1. Start the model server on Kaggle

Open `kaggle/peregrine-dataset-generator.ipynb` in Kaggle.

In the notebook settings:
- Enable internet access.
- Select a GPU accelerator. The notebook sets `CUDA_VISIBLE_DEVICES=0,1`, so use a dual-GPU option such as 2x T4 when available.

Add these Kaggle secrets before running the notebook:
- `NGROK_AUTH_TOKEN`: your ngrok authentication token.
- `OLLAMA_TUNNEL_PASSWORD`: a password for the authenticated tunnel.

Run the notebook cells in order. It installs Ollama, starts the server, pulls `qwen3.6:35b`, and prints an HTTPS API URL ending in `/v1`.

Keep the printed URL and password private. The Kaggle session must remain running while you generate data.

## 2. Install the local Python dependency

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The requirements file retains the original `openai` dependency.

## 3. Run the original generator

In PowerShell, set the URL printed by the Kaggle notebook and the same tunnel password:

```powershell
$env:OLLAMA_API_URL = "https://your-ngrok-host/v1"
$env:OLLAMA_TUNNEL_PASSWORD = "your-tunnel-password"
cd .\dataset_generator
python .\generator.py
```

Run `generator.py` from inside `dataset_generator/`. This preserves the original script's `import prompt` behavior and places its output files beside the scripts.

The original generator uses the `qwen3.6:35b` model, requests 10,000 successful examples, and allows up to 12,000 attempts. It appends to the output files if they already exist.

Generated files:
- `general.jsonl`
- `code.jsonl`

The prompt generator chooses general prompts about 60% of the time and coding prompts about 40% of the time.

## 4. Deduplicate and validate

Keep the working directory set to `dataset_generator/` and run:

```powershell
python .\deduplicate.py general
python .\validate.py general

python .\deduplicate.py code
python .\validate.py code
```

This creates:
- `general_unique.jsonl` and `code_unique.jsonl`
- `general_validated.jsonl` and `code_validated.jsonl`

The original cleanup scripts create derived files only when they do not already exist. Before rerunning deduplication or validation, remove the corresponding existing `*_unique.jsonl` and `*_validated.jsonl` files. To start generation from scratch, also remove or move the existing `general.jsonl` and `code.jsonl` files.

## Repository layout

```text
.
├── dataset_generator/
│   ├── generator.py
│   ├── prompt.py
│   ├── deduplicate.py
│   └── validate.py
├── kaggle/
│   └── peregrine-dataset-generator.ipynb
├── docs/
│   └── generation-journal.md
├── requirements.txt
├── LICENSE
└── README.md
```

The JSONL files produced by the scripts are local outputs and are ignored by Git. Generated examples are synthetic; review them before using them for training. Structural validation and question deduplication do not verify factual accuracy or code correctness.
