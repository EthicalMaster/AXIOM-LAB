# AXIOM LAB

**An Interactive Environment for Scientific Computing and Computational Discovery.**

> **Current build candidate: Phase 07D + research studio, interaction and release refinement.** This local-first scientific prototype offers validated data import, statistical and mathematical tools, bounded machine learning, append-only chart experiments with comparison/replay, evidence-only PDF/CSV/JSON exports, optional AI explanations and a loopback-bound Docker Compose release candidate. **It is NOT an independently verified public multi-user or high-concurrency platform.** Backend tests and Windows/browser/Docker acceptance are separate gates.

See [Production readiness](docs/PRODUCTION_READINESS.md) for request budgets, contextual guidance, capacity checks, and deployment acceptance gates.

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
.\.venv\Scripts\python.exe scripts/start_backend.py
```

For optional persistent AI settings, see [AI setup](docs/AI_SETUP.md). The launcher reads a private `.env` before starting FastAPI.

In a separate terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open <http://127.0.0.1:5173>; the backend health URL is <http://127.0.0.1:8898/api/v1/health>. The frontend Vite development proxy forwards `/api` traffic to port 8898. For a loopback-bound Compose release candidate see `docs/DEPLOYMENT.md`.

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

**Builder evidence:** The cumulative backend regression suite passed in the isolated builder environment. Exact current count appears in the bundled verification report; that is not a substitute for Windows, npm, browser, security or Docker runtime acceptance. The corresponding user checks are in the phase review files.

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
| 05A–05D | History, append-only chart-run revisions, guarded comparison and replay lineage | Replay limited to stored chart methods; not arbitrary ML experiments |
| 06A–06C | Replaceable optional AI adapter, rule-grounded methods and saved-run explanations | AI advisory only, does not compute numerical truth; external service optional |
| 07A | Evidence-based PDF, JSON and bounded chart CSV exports | Not a complete scientific manuscript or full-data CSV |
| 07B–07D | SQLite indexes, local load smoke, optional single-user access gate, Docker packaging | Not multi-tenant; external security, load, and Docker acceptance remain |

**Still not implemented:** Multi-user identity and authorization, distributed worker scheduling, production object storage, high-concurrency load certification, and fully automated public-cloud deployment. See `docs/DEPLOYMENT.md`.

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

**Public-release warning:** The optional access token is single-user only. There are no managed accounts, per-user dataset authorization, validated rate limits, isolated compute workers, shared storage, formal threat modeling or large-scale load testing. **Do not expose it as a public multi-user scientific service yet.**

**License:** No license file has been supplied. Select an explicit license and data-handling policy before inviting external contributions.

## Final release gate

Before any hosted deployment, follow [R01–R03 release gates](docs/RELEASE_GATE.md). Do not publish this single-user app as a multi-tenant service.
