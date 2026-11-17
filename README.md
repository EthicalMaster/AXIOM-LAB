# AXIOM LAB

**An Interactive Environment for Scientific Computing and Computational Discovery.**

> Status: **Phase 02B — Distribution Analysis (implementation candidate).** CSV/XLSX/XLS validation, immutable file storage, conservative column inspection, descriptive statistics, observation charts with saved runs, quality auditing, and empirical histograms are implemented as **local candidates**. Automated backend tests passed; browser acceptance remains yours to verify. No inference suite, cleaning, machine learning, authentication or AI is implemented. See `docs/PHASE_02B_REVIEW.md`.

AXIOM LAB is a planned, local-first scientific environment for data exploration, mathematical computation, hypothesis testing, predictive modelling, interactive visualization, persistent experiments, and reproducible reporting.

## Non-negotiable rules

1. Computation comes from verified scientific code, never invented LLM numerical outputs.
2. Original datasets are preserved; transformations create versioned derivatives.
3. Every scientific execution eventually creates a traceable run record.
4. Explain the concepts, run the feature, test it, document it, then commit.
5. Do not advertise features as implemented until evidence supports them.

## Quick start (Windows PowerShell; Phase 02B)

**Prerequisites:** Git; Python 3.11+ (3.12 recommended); Node.js 22.12+ or 24+; npm. You need internet access for the first dependency installation. The original Phase 00 ZIP did not contain `package-lock.json`. Your Phase 00 Git commit should already contain this file after `npm install`; keep it tracked.

### 1. Start the backend (PowerShell terminal A)

```powershell
cd "$HOME\Downloads\axiom-lab"
py -3 -m venv .venv  # skip if created in Phase 00
.\.venv\Scripts\python.exe -m pip install -e ".\backend[dev]"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8898
```

**Expected:** API is running. Open <http://127.0.0.1:8898/api/v1/health> and expect `status: "ok"`, `phase: "02B"`, `scientific_engine: "descriptive_statistics"`.

### 2. Start the frontend (PowerShell terminal B)

```powershell
cd "$HOME\Downloads\axiom-lab\frontend"
npm install
# This creates package-lock.json. Keep and commit it in the first verified Git commit.
npm run dev
```

**Expected:** Browser opens <http://127.0.0.1:5173> and shows **AXIOM LAB**, **Phase 02B**, and **API connected** when the backend is running.

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

### 4. Commit each bundle individually after verification

Apply and verify bundles 01C, 01D, 02A and 02B **sequentially**, using each ZIP’s `APPLY.md`. Start from a clean verified 01B `main` and do not re-initialize Git or overwrite the existing remote. Example commit for final bundle:

```powershell
git status
git diff --check
git add .
git commit -m "feat(phase-02b): empirical distribution analysis"
git push -u origin phase/02b-distributions
```

Merge into `main` **only after** the local checks pass and the learning review is completed.

## First dataset import

The React Data Lab now accepts a comma-delimited UTF-8 CSV or Excel XLSX/XLS up to 5 MiB. A successful import stores untouched raw bytes under `runtime/datasets/<id>/original.<extension>`, records metadata in `runtime/axiom.sqlite3`, returns a SHA-256 fingerprint and previews up to 8 data rows. Metadata can be reloaded at `GET /api/v1/datasets/{dataset_id}`. New endpoint `GET /api/v1/datasets/{dataset_id}/profile` checks the stored file fingerprint and computes provisional column types, present/missing counts, memory-bounded distinct counts and examples. Runtime data is ignored by Git. **No cleaning or type coercion modifies the original file.**

## Repository map

- `frontend/`: React + TypeScript + Vite; Data Lab upload, inspection, charts, saved runs, quality audit and distributions.
- `backend/`: FastAPI with import, numerical summaries, experiment and run storage, quality and distribution endpoints; no model training or inference tests yet.
- `docs/`: Phase 0 architecture, scientific safeguards, learning and decisions.
- `docs/reference/`: original master specification (source of truth for product intent).
- `examples/`: contains small, redistributable validation examples.

## Working process

Future bundles are applied with Git on a clean repository (see `docs/BUNDLE_PROTOCOL.md`). For every bundle: inspect scope, `git apply --check`, apply, install any new requirements, run tests, inspect behavior, explain the concepts, then commit and push. Report failures **before** committing.

## Quality and scientific status

| Capability | Status |
|---|---|
| Frontend + backend foundation | Implemented; verify locally |
| Backend health check | Implemented; verify locally |
| Dataset structure validation/import | Implemented in Phase 01A; user verified CSV flow |
| First scientific experiment | Implemented in Phase 01D, pending local acceptance |
| Column profiling | Implemented in Phase 01B; requires local acceptance |
| Descriptive statistics, quality and histograms | Implemented in 01C/02A/02B, pending local acceptance |
| Mathematical workbench | Planned (Phase 3) |
| Machine learning | Planned (Phase 4) |
| Advanced experiment engine | Planned (Phase 5) |
| Optional AI explanations | Planned (Phase 6) |
| Scientific reporting and release | Planned (Phase 7) |

See `docs/PHASE_02B_REVIEW.md` for current acceptance criteria (Phase 00 review remains in `docs/PHASE_00_REVIEW.md`) and learning questions, and `docs/ROADMAP.md` for milestones.

**License:** Not selected. This repository should remain private until its license is explicitly decided. No license rights are granted by this README.

### Phase 01C candidate

`GET /api/v1/datasets/{dataset_id}/statistics` computes descriptive results only for consistently numeric columns. See `docs/PHASE_01C_REVIEW.md`. No inferential analysis is implemented.

### Phase 01D candidate

`POST /api/v1/experiments` and `GET /api/v1/experiments/{id}` save and reload an immutable observation chart and run. The chart is not a time series. Single-user and local-only; see `docs/PHASE_01D_REVIEW.md`.

### Phase 02A candidate

`GET /api/v1/datasets/{dataset_id}/quality` audits missing cells, completeness and duplicate source rows with an explicit memory cap. It does not clean datasets. See `docs/PHASE_02A_REVIEW.md`.

### Phase 02B candidate

`GET /api/v1/datasets/{dataset_id}/distribution?column=...` returns an empirical histogram and cautious Tukey-fence outlier indicators, with full interval-frequency table. No probability density or hypothesis testing is claimed. See `docs/PHASE_02B_REVIEW.md`.
