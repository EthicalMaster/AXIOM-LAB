# AXIOM LAB

**An Interactive Environment for Scientific Computing and Computational Discovery.**

> Status: **Phase 01A — Dataset Import and Validation (implementation candidate).** CSV/XLSX/XLS structural validation, local preservation of original bytes, metadata lookup and a limited text preview are implemented. Statistical computation, cleaning, plotting, experiments and AI are **not** implemented yet. See `docs/PHASE_01A_REVIEW.md` before marking this milestone verified.

AXIOM LAB is a planned, local-first scientific environment for data exploration, mathematical computation, hypothesis testing, predictive modelling, interactive visualization, persistent experiments, and reproducible reporting.

## Non-negotiable rules

1. Computation comes from verified scientific code, never invented LLM numerical outputs.
2. Original datasets are preserved; transformations create versioned derivatives.
3. Every scientific execution eventually creates a traceable run record.
4. Explain the concepts, run the feature, test it, document it, then commit.
5. Do not advertise features as implemented until evidence supports them.

## Quick start (Windows PowerShell; Phase 01A)

**Prerequisites:** Git; Python 3.11+ (3.12 recommended); Node.js 22.12+ or 24+; npm. You need internet access for the first dependency installation. The original Phase 00 ZIP did not contain `package-lock.json`. Your Phase 00 Git commit should already contain this file after `npm install`; keep it tracked.

### 1. Start the backend (PowerShell terminal A)

```powershell
cd "$HOME\Downloads\axiom-lab"
py -3 -m venv .venv  # skip if created in Phase 00
.\.venv\Scripts\python.exe -m pip install -e ".\backend[dev]"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8898
```

**Expected:** API is running. Open <http://127.0.0.1:8898/api/v1/health> and expect a JSON object containing `status: "ok"`, `phase: "01A"`, `scientific_engine: "not_implemented"`.

### 2. Start the frontend (PowerShell terminal B)

```powershell
cd "$HOME\Downloads\axiom-lab\frontend"
npm install
# This creates package-lock.json. Keep and commit it in the first verified Git commit.
npm run dev
```

**Expected:** Browser opens <http://127.0.0.1:5173> and shows **AXIOM LAB**, **Phase 01A**, and **API connected** when the backend is running.

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

### 4. Phase 01A Git commit (only after verifying)

Apply the phase bundle on a clean Phase 00 repository as described in `docs/BUNDLE_PROTOCOL.md` and `docs/PHASE_01A_REVIEW.md`. Do **not** re-initialize Git or overwrite the existing remote. After successful review:

```powershell
git status
git diff --check
git add .
git commit -m "feat(phase-01a): add validated dataset import"
git push -u origin phase/01a-dataset-import
```

Merge into `main` **only after** the local checks pass and the learning review is completed.

## First dataset import

The React Data Lab now accepts a comma-delimited UTF-8 CSV or Excel XLSX/XLS up to 5 MiB. A successful import stores untouched raw bytes under `runtime/datasets/<id>/original.<extension>`, records metadata in `runtime/axiom.sqlite3`, returns a SHA-256 fingerprint and previews up to 8 data rows. Metadata can be reloaded at `GET /api/v1/datasets/{dataset_id}`. Runtime data is ignored by Git. **No statistics or dataset transformations are performed.**

## Repository map

- `frontend/`: React + TypeScript + Vite; Phase 01A import form and preview.
- `backend/`: FastAPI with health, dataset import and metadata endpoints; no numerical scientific engine yet.
- `docs/`: Phase 0 architecture, scientific safeguards, learning and decisions.
- `docs/reference/`: original master specification (source of truth for product intent).
- `examples/`: will contain small, redistributable validation examples in later bundles.

## Working process

Future bundles are applied with Git on a clean repository (see `docs/BUNDLE_PROTOCOL.md`). For every bundle: inspect scope, `git apply --check`, apply, install any new requirements, run tests, inspect behavior, explain the concepts, then commit and push. Report failures **before** committing.

## Quality and scientific status

| Capability | Status |
|---|---|
| Frontend + backend foundation | Implemented; verify locally |
| Backend health check | Implemented; verify locally |
| Dataset structure validation/import | Implemented in Phase 01A; requires local acceptance |
| First scientific experiment | Planned (Phase 1) |
| Dataset analysis and statistics | Planned (Phases 1–2) |
| Mathematical workbench | Planned (Phase 3) |
| Machine learning | Planned (Phase 4) |
| Advanced experiment engine | Planned (Phase 5) |
| Optional AI explanations | Planned (Phase 6) |
| Scientific reporting and release | Planned (Phase 7) |

See `docs/PHASE_01A_REVIEW.md` for current acceptance criteria (Phase 00 review remains in `docs/PHASE_00_REVIEW.md`) and learning questions, and `docs/ROADMAP.md` for milestones.

**License:** Not selected. This repository should remain private until its license is explicitly decided. No license rights are granted by this README.
