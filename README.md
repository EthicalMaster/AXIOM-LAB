# AXIOM LAB

**An Interactive Environment for Scientific Computing and Computational Discovery.**

> **Current build candidate: Phase 05A.** The local-first prototype includes validated dataset import, profiling, descriptive statistics, one-sample inference, normality diagnostics, bounded mathematical operations, small supervised/unsupervised ML experiments, and saved chart-run history. **These are bounded prototypes, not a finished scientific suite or a public multi-user service.** The user must run the Windows/frontend/browser checks in each phase's review file before accepting and pushing it.

## Design principles

1. Numerical results come from tested algorithms, not LLM calculations.
2. Original uploaded bytes remain unchanged; dataset IDs and SHA-256 fingerprints preserve provenance.
3. Explain every selected method, assumption, limitation, alternative and failure case.
4. Develop one verified vertical slice at a time, with Git checkpoints and learning reviews.
5. Do not advertise planned or untested functionality as complete.

## Setup (Windows / PowerShell)

Requires Python 3.11+, Node 22+, Git, and network access for initial dependencies. From the project root:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".\backend[dev]"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8898
```

In a separate terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open <http://127.0.0.1:5173>; the backend health URL is <http://127.0.0.1:8898/api/v1/health>. The frontend Vite development proxy forwards `/api` traffic to port 8898.

## Verification

From the root:

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests -q
.\.venv\Scripts\python.exe -m compileall -q backend/app
cd frontend
npm run test
npm run typecheck
npm run build
```

**Builder evidence:** After applying all 12 candidate bundles to the matching Phase 02B starter and running the Python regression suite, 95 backend tests passed. The builder cannot certify the user's browser or a production frontend build; **those checks must run on the developer's actual machine**. The method-specific user checks are in `docs/PHASE_XX_REVIEW.md`.

## Current bounded capabilities

| Phase | Implemented candidate | Limitations |
|---|---|---|
| 01A–02B | CSV/Excel import, column profiling, statistics, charts, persisted runs, quality audits, histograms | Original files immutable; no cleaning or user access control |
| 02C | Two-sided one-sample Student t-test, confidence interval and effect size | Independence and sampling design cannot be verified automatically |
| 02D | Shapiro–Wilk diagnostic | Only sample sizes 3–5000; p-value not proof of normality |
| 03A | Whitelisted arithmetic expression evaluator | No arbitrary Python execution or comprehensive CAS |
| 03B | Polynomial differentiation, integration, approximate roots | Degree ≤6; numerical root approximation limits |
| 03C | Matrix determinant, eigenvalues, rank, inverse, solve | Real square matrices 1–8; ill-conditioned operations withheld |
| 03D | Bracketed roots and polynomial quadrature | Limited intervals; estimated numerical error |
| 04A | Train-only fitted preprocessing with deterministic split | 16–2000 labelled rows; numeric features; no time series |
| 04B | Linear regression holdout evaluation | Baseline only; does not imply causation |
| 04C | Stratified logistic classification | Categorical targets, bounded classes, classification assumptions |
| 04D | K-means clustering | Internal metrics, no ground-truth labels |
| 04E | 3-fold training-only CV comparison | Two models per task, one holdout, not automated model discovery |
| 05A | Read-only paginated experiment history and stored runs | Local single-user; new multi-run execution comes later |

**Planned, not implemented:** Experiment revisions/comparison/reproducibility packages (05B–05D), AI provider and grounded explanations (06A–06C), scientific PDF reporting, load testing, production authentication, public deployment and scaling (07A–07D).

## Architecture map

- `frontend/src/`: React panels and typed API helpers, driven by real backend results.
- `backend/app/api/`: FastAPI routes and input validation.
- `backend/app/services/`: independently testable statistical, mathematical and ML methods.
- `backend/app/persistence/`: SQLite experiment/dataset metadata plus local original-file storage.
- `backend/tests/`: reference tests, negative cases and API integration checks.
- `docs/`: requirements, ADRs, known limits, scientific theory, review checklists and test evidence.
- `runtime/`: Git-ignored local working data. Never commit real uploads or credentials.

## Development protocol

Apply **one patch per phase**, from a clean, committed parent state, with `git apply --check` before `git apply`. Install updated Python dependencies, run all automated checks, complete the matching review checklist, document errors, and **only then** commit/push. Never force a conflicting patch or silently drop failing tests. See `docs/BUNDLE_PROTOCOL.md`.

**Public-release warning:** The application lacks accounts/authorization, rate limits, isolated compute workers, shared storage, formal threat modeling and multi-user load testing. **Do not expose it as a public scientific service yet.**

**License:** Undecided. Keep private until license and data-handling policies are approved.
