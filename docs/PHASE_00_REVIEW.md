# Phase 00 — manual acceptance and learning review

**Do not commit/push until the required tests pass or their failures are explained and resolved.**

## Installation checks

- [ ] `git --version`, `py --version`, `node --version`, and `npm --version` run.
- [ ] Node meets Vite requirement (`22.12+` or `24+` recommended), Python is `3.11+`.
- [ ] Python venv created and editable backend installed.
- [ ] Frontend `npm install` completes without errors; generated `frontend/package-lock.json` is included in the first commit.

## Functionality checks

- [ ] Backend starts on `127.0.0.1:8000`.
- [ ] `http://127.0.0.1:8000/api/v1/health` returns `status=ok`, `phase=0`, `scientific_engine=not_implemented`.
- [ ] `http://127.0.0.1:8000/docs` displays FastAPI API docs.
- [ ] Frontend starts on `127.0.0.1:5173` and displays AXIOM LAB, Phase 0.
- [ ] Frontend displays `API connected` with backend running.
- [ ] Frontend displays `API unavailable` after backend stops and the browser refreshes.
- [ ] No interface claims to perform real science yet.

## Automated checks

- [ ] `.\.venv\Scripts\python.exe -m pytest backend/tests -q` passes (from project root).
- [ ] `npm run test` passes (from `frontend`).
- [ ] `npm run typecheck` passes.
- [ ] `npm run build` passes.
- [ ] `git status` shows no generated dependencies, secret files, or runtime data staged.

## Learning review: answer in your own words

1. Why does React render the interface while FastAPI owns scientific computation?
2. What is an HTTP endpoint, and what does the version path `/api/v1` mean?
3. Why is API health different from scientific correctness?
4. What is a virtual environment and why are dependencies separated?
5. What is the difference between a Git commit and pushing to GitHub?
6. Why should raw datasets be immutable in future phases?
7. What is the difference between `planned`, `implemented`, and `verified`?

## Report failures in this format

```text
AXIOM LAB / PHASE 00
Step attempted:
Command or URL:
Expected:
Actual:
Full terminal error / screenshot:
Python version:
Node version:
Git status (if relevant):
```

Do not delete failure details. Record significant problems in `problems-and-solutions/PROBLEM_REGISTER.md`.
