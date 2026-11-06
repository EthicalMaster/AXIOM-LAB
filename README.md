# AXIOM LAB

**An Interactive Environment for Scientific Computing and Computational Discovery.**

> Status: **Phase 0 — foundation only.** No data import, statistics, mathematical computation, machine learning, AI, or reporting is implemented yet. The frontend and backend provide a minimal connection check so that the development environment can be verified honestly.

AXIOM LAB is a planned, local-first scientific environment for data exploration, mathematical computation, hypothesis testing, predictive modelling, interactive visualization, persistent experiments, and reproducible reporting.

## Non-negotiable rules

1. Computation comes from verified scientific code, never invented LLM numerical outputs.
2. Original datasets are preserved; transformations create versioned derivatives.
3. Every scientific execution eventually creates a traceable run record.
4. Explain the concepts, run the feature, test it, document it, then commit.
5. Do not advertise features as implemented until evidence supports them.

## Phase 0 quick start (Windows PowerShell)

**Prerequisites:** Git; Python 3.11+ (3.12 recommended); Node.js 22.12+ or 24+; npm. You need internet access for the first dependency installation. The initial ZIP does not contain `package-lock.json` because package registry access was unavailable during packaging; your first successful `npm install` creates it, and you should commit it for reproducible later installs.

### 1. Start the backend (PowerShell terminal A)

```powershell
cd "$HOME\Downloads\axiom-lab"
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".\backend[dev]"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

**Expected:** API is running. Open <http://127.0.0.1:8000/api/v1/health> and expect a JSON object containing `status: "ok"`, `phase: "0"`, `scientific_engine: "not_implemented"`.

### 2. Start the frontend (PowerShell terminal B)

```powershell
cd "$HOME\Downloads\axiom-lab\frontend"
npm install
# This creates package-lock.json. Keep and commit it in the first verified Git commit.
npm run dev
```

**Expected:** Browser opens <http://127.0.0.1:5173> and shows **AXIOM LAB**, **Phase 0**, and **API connected** when the backend is running.

### 3. Run the tests (PowerShell terminal C)

```powershell
cd "$HOME\Downloads\axiom-lab"
.\.venv\Scripts\python.exe -m pytest backend/tests -q
.\.venv\Scripts\python.exe -m compileall -q backend/app
cd frontend
npm run test
npm run typecheck
npm run build
```

**Expected:** Commands return exit code 0; backend and frontend tests pass; TypeScript typecheck and production build finish without errors. Record actual test output in `docs/testing/TEST_LOG.md`. No run has been claimed until you perform it.

### 4. First Git commit (only after verifying)

```powershell
cd "$HOME\Downloads\axiom-lab"
git init -b main
git add .
git status
git commit -m "chore(phase-00): establish scientific platform foundation"
```

Create an **empty** GitHub repository named `AXIOM-LAB` (no generated README, .gitignore, or license). Then connect it using your own GitHub repository URL:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/AXIOM-LAB.git
git push -u origin main
```

Do **not** type the example URL literally; replace `YOUR_USERNAME` with your actual GitHub username. A GitHub sign-in may be required.

## Repository map

- `frontend/`: React + TypeScript + Vite; minimal Phase 0 connection screen.
- `backend/`: FastAPI with a versioned health endpoint; no scientific engine yet.
- `docs/`: Phase 0 architecture, scientific safeguards, learning and decisions.
- `docs/reference/`: original master specification (source of truth for product intent).
- `examples/`: will contain small, redistributable validation examples in later bundles.

## Working process

Future bundles are applied with Git on a clean repository (see `docs/BUNDLE_PROTOCOL.md`). For every bundle: inspect scope, `git apply --check`, apply, install any new requirements, run tests, inspect behavior, explain the concepts, then commit and push. Report failures **before** committing.

## Quality and scientific status

| Capability | Status |
|---|---|
| Frontend + backend foundation | Scaffolded; verify locally |
| Backend health check | Implemented; verify locally |
| First scientific experiment | Planned (Phase 1) |
| Dataset analysis and statistics | Planned (Phases 1–2) |
| Mathematical workbench | Planned (Phase 3) |
| Machine learning | Planned (Phase 4) |
| Advanced experiment engine | Planned (Phase 5) |
| Optional AI explanations | Planned (Phase 6) |
| Scientific reporting and release | Planned (Phase 7) |

See `docs/PHASE_00_REVIEW.md` for acceptance criteria and learning questions, and `docs/ROADMAP.md` for milestones.

**License:** Not selected. This repository should remain private until its license is explicitly decided. No license rights are granted by this README.
