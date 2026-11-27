# Configure AXIOM Guide

The engine reads provider settings from the **backend process environment**. It does not read `.env` automatically when launched directly with Uvicorn. Docker Compose reads `.env` through its own environment configuration. No provider key belongs in Vite, a VITE_ variable, source control, browser storage or screenshots.

## Direct local development (Windows PowerShell)

1. Open the provider console using an account you are authorized to use. For Groq, use https://console.groq.com/keys and confirm the model in https://console.groq.com/docs/models. The provider's free allowance varies by account, model and date.
2. From the repository root in a NEW backend terminal, set the following session environment variables. Enter the key when prompted (masked). Replace the model ID if your provider lists a different compatible model.

```powershell
$env:AXIOM_AI_BASE_URL = 'https://api.groq.com/openai/v1'
$env:AXIOM_AI_MODEL = 'openai/gpt-oss-20b'
$env:AXIOM_AI_API_KEY = [System.Net.NetworkCredential]::new('', (Read-Host 'Provider key' -AsSecureString)).Password
$env:AXIOM_AI_RPM = '10'
$env:AXIOM_AI_RPD = '100'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --port 8898
```

Stop an existing backend before starting this one. In a separate terminal run `Invoke-RestMethod http://127.0.0.1:8898/api/v1/ai/status` (local unprotected mode). `enabled: true` means the configuration is present and URL accepted, not that the key is valid. Open Ask AXIOM, opt in to external commentary and ask a question. A successful response must show the optional AI advisory source. Built-in fallback means the remote call was not used or failed. Reasoning models may exhaust the current 250-token output allowance before producing text; choose another supported chat model if this happens.

The session variables disappear when the terminal closes; repeat the setup for a new terminal. To remove the key in the current terminal after stopping the server, use `Remove-Item Env:AXIOM_AI_API_KEY`.

## Docker / deployed backend

Use the existing `.env.example` as a template for local Docker Compose; place the key in an ignored `.env` file or the hosting provider's secret manager, never in a committed file. The backend service must receive `AXIOM_AI_BASE_URL`, `AXIOM_AI_MODEL` and `AXIOM_AI_API_KEY`. Restart after changes. Keep HTTPS and authentication for remote use.

## Quotas, privacy and failure

The application has local defaults of 10 remote requests/minute and 100/day; provider quotas are separate. Keys are used on the server only. Opt-in sends a question and limited summary, not raw dataset rows, but names/aggregates can still be confidential. For unknown inputs, provider outages, and quota exhaustion, the built-in guide remains available. Scientific computation never depends on AI. No live provider call was tested during this patch build.
