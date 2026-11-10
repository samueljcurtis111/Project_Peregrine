# Kaggle Ollama server

This notebook provides the model endpoint used by the local Peregrine dataset generator.

## Kaggle setup

1. Open `ollama_server.ipynb`.
2. Enable internet access and choose a GPU accelerator. Select dual T4 GPUs when available.
3. Add these Kaggle secrets:
   - `NGROK_AUTH_TOKEN`
   - `OLLAMA_TUNNEL_PASSWORD`
4. Run the notebook from top to bottom.
5. Copy the printed HTTPS API URL (it ends in `/v1`) into the environment where you run the generator.

The notebook starts Ollama, pulls `qwen3.6:35b`, waits for the local API to become ready, and opens an authenticated ngrok tunnel.

Never commit ngrok tokens, tunnel passwords, or live tunnel URLs. Treat the URL as private even though the tunnel also requires HTTP Basic Authentication.
