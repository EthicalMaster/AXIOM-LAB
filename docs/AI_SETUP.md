# Persistent AXIOM Guide configuration

AI is optional. Scientific computation is independent of any provider.

## Local development (PowerShell)

1. Stop the existing Uvicorn process. From the repository root install the backend dependencies (`.\.venv\Scripts\python.exe -m pip install -e ".\backend[dev]"`).
2. Create the private file only if it is absent:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

3. Set the three values below in `.env`, preserving any other settings. Replace the example model with a model your provider actually offers. Example Groq configuration (availability and quota depend on your authorized account):

```dotenv
AXIOM_AI_BASE_URL=https://api.groq.com/openai/v1
AXIOM_AI_MODEL=openai/gpt-oss-20b
AXIOM_AI_API_KEY=REPLACE_WITH_YOUR_PRIVATE_KEY
AXIOM_AI_RPM=10
AXIOM_AI_RPD=100
```

4. Save the file. Use a fresh terminal to avoid previously exported environment variables taking precedence. Start the server with:

```powershell
.\.venv\Scripts\python.exe scripts/start_backend.py
```

The launcher loads `.env` before any application imports, including import-time quota construction. Existing environment variables win. It binds to `127.0.0.1:8898`, reloads Python changes, and never prints credentials. Use `--no-reload` if needed. Restart completely after editing `.env`. Direct Uvicorn without `--env-file` still does not load the file; use the launcher. `--port` changes the backend port; update Vite's proxy to match if necessary.

Verify in a separate terminal: `Invoke-RestMethod http://127.0.0.1:8898/api/v1/ai/status` (local unprotected mode). The Method guide workspace also has a Check provider button. `enabled: true` confirms settings are present and the URL accepted, **not** that the remote key works. Open Ask AXIOM, opt in to external commentary, and ask a question. The optional AI advisory source confirms a successful external response. If built-in guidance appears, check the model ID, key and quotas. Reasoning models may exhaust the 250-token response budget; use a supported concise chat model if needed.

## Secret handling and deployment

`.env` is ignored by Git but remains plaintext on disk: protect it with your OS account permissions, never share it or upload it. `git check-ignore .env` should print `.env`. Never put secrets in `VITE_` variables, frontend code, localStorage, screenshots, or committed files. Docker Compose already reads `.env`; deployment platforms should inject values with their secret manager. Do not use the local launcher for public hosting. Keep HTTPS and authentication on the remote deployment.

## Quotas and privacy

Default local external allowance: 10 requests/minute and 100/day, distinct from provider limits. Provider calls send only the opted-in question and bounded context, not original file bytes; aggregates may still be sensitive. No live provider call was tested for this release. Local deterministic guidance remains available when a provider is disabled, fails, or reaches a quota.
