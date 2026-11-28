<div align="center">

<sub>∴ &nbsp; A X I O M &nbsp; / &nbsp; L A B</sub>

# A research studio built for evidence.

**Explore data. Investigate relationships. Validate results. Keep the evidence.**

An independent scientific computing workspace bringing data exploration,
statistics, mathematics and machine learning into one research environment.

[**Open AXIOM LAB ↗**](https://axiom-lab-silk.vercel.app) &nbsp;·&nbsp; [Quick start](#quick-start) &nbsp;·&nbsp; [Architecture](#architecture) &nbsp;·&nbsp; [Report an issue](https://github.com/EthicalMaster/AXIOM-LAB/issues)

`HOSTED BETA` &nbsp; `REACT + TYPESCRIPT` &nbsp; `PYTHON + FASTAPI` &nbsp; `SUPABASE`

</div>

---

## Why AXIOM LAB?

Scientific work is often spread across spreadsheets, notebooks, statistical tools and separate model-building environments. AXIOM LAB brings these steps together, with an emphasis on preserving the original data and understanding how a result was obtained.

The platform separates **scientific computation** from **AI-assisted interpretation**. Numerical results are produced by implemented mathematical and statistical methods. The optional contextual guide helps explain those results; it does not replace the computational engine or independent scientific judgment.

## The research experience

| Stage | What you can do |
| :--- | :--- |
| **01 · Observe** | Import CSV and Excel files, preserve original bytes, inspect observations and examine inferred variable types. |
| **02 · Inspect** | Review missing values, completeness, distributions, outlier indicators and data quality. |
| **03 · Investigate** | Explore descriptive statistics, one-sample inference, mathematical methods and supported machine learning workflows. |
| **04 · Record** | Save supported chart experiments, compare revisions, replay recorded configurations and export results. |
| **05 · Organize** | Reopen saved datasets, label records and group datasets and experiments into research projects. |

### Designed specifically for research

<table>
<tr>
<td width="50%" valign="top">
<sub>AX / 01 — INTERACTIVE INSTRUMENT</sub>
<h3>Probability Field</h3>
<p>Explore a normal distribution directly from the landing page. Adjust the mean and standard deviation and observe how probability mass within a fixed interval changes in real time.</p>
<p><code>Client-side computation</code> · <code>No sign-in required</code></p>
</td>
<td width="50%" valign="top">
<sub>AX / 02 — RESEARCH WORKFLOW</sub>
<h3>Evidence Trail</h3>
<p>Follow the active dataset from source import and SHA-256 fingerprint through column inspection to analysis and experiment history. Readiness reflects real dataset state, not a fabricated progress score.</p>
<p><code>Dataset-aware</code> · <code>Source integrity</code></p>
</td>
</tr>
<tr>
<td valign="top">
<sub>AX / 03 — CONTEXTUAL EXPLORATION</sub>
<h3>Interactive Plot & Lens</h3>
<p>Inspect points and bins, pan and zoom through plotted observations, and ask contextual questions about selected evidence using the method guide.</p>
<p><code>Interactive coordinates</code> · <code>Optional AI</code></p>
</td>
<td valign="top">
<sub>AX / 04 — PRIVATE WORKSPACE</sub>
<h3>Research Library</h3>
<p>Search saved datasets, reopen original data, manage projects and access account settings. Hosted workspaces use managed Google authentication and account-scoped persistence.</p>
<p><code>Cloud persistence</code> · <code>Project organization</code></p>
</td>
</tr>
</table>

## Scientific capabilities

| Module | Implemented scope |
| :--- | :--- |
| Data Lab | CSV/XLS/XLSX ingestion, original-file fingerprints, column profiling and quality diagnostics |
| Statistics | Descriptive statistics, distributions, hypothesis-testing helpers and statistical diagnostics |
| Mathematics | Safe numeric expressions, bounded polynomial calculus, real square matrices and numerical methods |
| Machine Learning | Numeric-feature regression, classification, clustering and bounded model comparisons |
| Experiments | Supported chart-run history, revision lineage, comparison, replay and PDF/JSON/CSV exports |
| Method Guide | Built-in explanations and optional OpenAI-compatible provider assistance |
| System Checks | Connectivity and operational diagnostics |

The studio includes light and dark themes, responsive navigation, interactive charts, loading and recovery states, and a dedicated Google sign-in experience.

> **Scientific boundaries:** Methods have documented input limits, assumptions and failure modes. Not every analysis supports persisted replay; ML executions are currently distinct from saved chart-run history. See [Scientific validation](docs/SCIENTIFIC_VALIDATION.md) before interpreting results.

## Architecture

AXIOM LAB uses a modular Python backend rather than splitting each scientific module into a separate service. React presents the typed results; FastAPI validates requests and dispatches computation to scientific services.

```text
                       AXIOM LAB
                           |
              React + TypeScript / Vite
                           |
                 Same-origin /api/v1
                           |
                   FastAPI backend
                           |
         +-----------------+------------------+
         |                 |                  |
    Request validation  Scientific engine  Workspace services
    Auth & quotas       NumPy / SciPy      Dataset inventory
                        SymPy / sklearn    Projects & runs
         |                 |                  |
         |            Typed results           |
         |                 |                  |
         +-----------------+------------------+
                           |
            +--------------+--------------+
            |                             |
       Local mode                   Hosted mode
       SQLite + files               Supabase HTTPS APIs
                                    Postgres + private Storage
                                          |
                                    Google OAuth / PKCE

       Optional AI provider: advisory interpretation only
```

*Conceptual application architecture. Authentication is initiated in the browser with Supabase and verified by the backend; the diagram is not a request sequence or a performance benchmark.*

### Technology choices

| Layer | Stack | Responsibility |
| :--- | :--- | :--- |
| Interface | React 19, TypeScript, Vite | Research studio, visualizations and interactive workflows |
| API | Python, FastAPI, Pydantic, Uvicorn | Typed HTTP contracts, validation and orchestration |
| Scientific computing | NumPy, SciPy, SymPy, scikit-learn | Numerical, statistical, symbolic and ML methods |
| Data & reporting | openpyxl, xlrd, ReportLab | Spreadsheet ingestion and PDF reports |
| Identity | Supabase Auth, Google OAuth | Managed sessions and backend identity verification |
| Persistence | SQLite/files locally; Supabase Postgres/Storage in hosted mode | Original datasets, workspace metadata and recorded experiments |
| Hosting | Vercel, Docker Compose for local use | Separate deployed frontend and API; local container workflow |
| Verification | pytest, Vitest, TypeScript, GitHub Actions | Numerical, application and build checks |

## Quick start

Run the local workspace without configuring Google OAuth, a cloud database or an AI provider. Use Python **3.11+** (3.12 recommended), Node.js **22.12+**, npm and Git.

### 1. Clone and start the backend

**Windows / PowerShell**

```powershell
git clone https://github.com/EthicalMaster/AXIOM-LAB.git
cd AXIOM-LAB
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".\backend[dev]"
.\.venv\Scripts\python.exe scripts/start_backend.py
```

<details>
<summary>macOS / Linux</summary>

```bash
git clone https://github.com/EthicalMaster/AXIOM-LAB.git
cd AXIOM-LAB
python3 -m venv .venv
.venv/bin/python -m pip install -e './backend[dev]'
.venv/bin/python scripts/start_backend.py
```

</details>

### 2. Start the frontend

Open a second terminal at the repository root:

```bash
cd frontend
npm ci
npm run dev
```

| Service | Local URL |
| :--- | :--- |
| Application | http://127.0.0.1:5173 |
| API health | http://127.0.0.1:8898/api/v1/health |

Use the landing page to enter the research studio. Try a small sample dataset before importing your own observations.

<details>
<summary>Alternative: local Docker Compose</summary>

With Docker and Compose installed, run from the repository root:

```bash
docker compose config --quiet
docker compose build
docker compose up -d
```

Open http://127.0.0.1:8080. Stop using `docker compose down`; do not add `-v` for ordinary shutdown, because it removes the persistent volume.

</details>

### Optional configuration

Copy `.env.example` to `.env` at the repository root only when you need optional settings. Local mode does not require secrets. To enable an external AI provider, configure the following privately:

```dotenv
AXIOM_AI_BASE_URL=https://your-provider.example/v1
AXIOM_AI_MODEL=your-model-id
AXIOM_AI_API_KEY=your-private-key
```

Use a trusted HTTPS provider. Keep local and hosted credentials out of source control. Scientific methods remain available without an AI provider.

## Hosted beta

[**axiom-lab-silk.vercel.app**](https://axiom-lab-silk.vercel.app) is the hosted application. Access to individual workspaces is determined by the configured registration and invitation policy.

The hosted architecture is distinct from the legacy single-user Docker deployment:

- Separate Vercel frontend and FastAPI backend projects built from the repository.
- Google OAuth through Supabase Auth, with backend verification and explicit workspace authorization.
- Tenant-scoped dataset and experiment storage, private original-file objects, and distributed request-budget support.
- Account settings, owner-only operational views and a deletion-request workflow. A deletion request does not itself erase stored data.

<details>
<summary>Hosted configuration reference</summary>

Frontend build-time environment (`frontend/.env.local` for local testing):

```dotenv
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=your-publishable-key
```

Backend environment (server only):

```dotenv
AXIOM_HOSTED_MODE=1
AXIOM_PUBLIC_MODE=1
AXIOM_PUBLIC_ORIGIN=https://your-frontend.example
AXIOM_GOOGLE_AUTH=1
AXIOM_MULTI_USER=1
AXIOM_CLOUD_STORAGE=1
AXIOM_DISTRIBUTED_RPM=1
AXIOM_OPEN_REGISTRATION=0
AXIOM_GOOGLE_OWNER_ID=your-verified-owner-uuid
AXIOM_MULTI_USER_IDS=
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=your-publishable-key
SUPABASE_SECRET_KEY=your-server-only-secret-key
```

These are illustrative placeholders, not a complete deployment procedure. Apply and review the repository's cloud database schema, private storage policies and RPC permissions before enabling hosted mode. Configure Google/Supabase OAuth redirect URLs, Vercel project roots, API rewrites and rate limits for your own deployment. Keep `AXIOM_OPEN_REGISTRATION=0` for a restricted staging rollout until isolation and release checks pass. Never put `SUPABASE_SECRET_KEY` or AI secrets in any `VITE_` variable.

Hosted request limits may be tighter than the local scientific validator. Use small datasets for initial testing. See `.env.example`, `frontend/vercel.json` and `backend/vercel.json` for configuration starting points.

</details>

## Repository structure

```text
AXIOM-LAB/
├── frontend/                React research studio
│   ├── src/                 UI, visualizations and typed clients
│   └── vercel.json          Hosted routing and browser headers
├── backend/                 Python scientific API
│   ├── app/
│   │   ├── api/             HTTP routes and schemas
│   │   ├── core/            Auth, limits and shared infrastructure
│   │   ├── services/        Scientific methods
│   │   └── persistence/     Local and cloud storage
│   ├── tests/               Backend verification
│   └── index.py             Vercel ASGI entry point
├── deploy/                  Deployment assets
├── docs/                    Architecture and scientific validation
├── scripts/                 Development and release utilities
├── .github/workflows/       CI checks
└── .env.example             Private configuration template
```

## Testing & engineering standards

From the repository root, with the backend virtual environment activated:

```bash
python -m pytest backend/tests -q
python -m compileall -q backend/app
python scripts/release_check.py
```

Then test the frontend:

```bash
cd frontend
npm ci
npm run test
npm run typecheck
npm run build
```

[View continuous integration runs ↗](https://github.com/EthicalMaster/AXIOM-LAB/actions/workflows/ci.yml)

The project emphasizes numerical reference checks, input validation, immutable source fingerprints, train-only preprocessing, reproducible configurations and clear failure states. A passing health endpoint indicates service availability, not scientific correctness or security certification.

### Current boundaries

The hosted beta is not a claim of unlimited-scale readiness, independent security certification or universal statistical validity. Before a broader release, verify cross-account isolation, deployed upload limits, capacity under representative workloads, backup restoration and dependency security. Use synthetic or non-sensitive data for initial testing. Optional external AI commentary can transmit limited context to a configured provider; do not submit sensitive information to it.

## Documentation

| Resource | Purpose |
| :--- | :--- |
| [Scientific validation](docs/SCIENTIFIC_VALIDATION.md) | Method assumptions, independent references and numerical safeguards |
| [Architecture](docs/ARCHITECTURE.md) | Original modular architecture and engineering trade-offs |
| [Deployment](docs/DEPLOYMENT.md) | Local Docker deployment and historical single-user guidance |
| [Production readiness](docs/PRODUCTION_READINESS.md) | Admission controls and historical readiness gates |
| [Release gate](docs/RELEASE_GATE.md) | Verification, recovery and release checklist |
| [Contribution guide](CONTRIBUTING.md) | Development and contribution conventions |
| [Changelog](CHANGELOG.md) | Project history |

Some earlier documents describe the pre-cloud, single-user architecture. Use them as historical design records, not as the current hosted multi-user configuration.

## Contributing & license

Issues and suggestions are welcome through [GitHub Issues](https://github.com/EthicalMaster/AXIOM-LAB/issues). Include a reproducible example, expected result and relevant environment details when reporting scientific or technical problems. Do not attach credentials or private datasets.

Copyright © 2026 EthicalMaster (AXIOM LAB contributors retain their respective rights).

AXIOM LAB's original project code is licensed under the **GNU Affero General Public License v3.0 only** (`AGPL-3.0-only`). See [LICENSE](LICENSE) for the full terms.

You may use, study, modify and redistribute covered code, including commercially, subject to the license. Modified network-accessible versions have corresponding-source obligations under section 13.

The hosted application offers its source through its footer. Deployment operators must provide the corresponding source for the actual version they run. Private user datasets, credentials and third-party components are not relicensed by this notice. See [NOTICE](NOTICE) and [third-party notices](THIRD_PARTY_NOTICES.md).

---

<div align="center">

**AXIOM LAB** · Evidence first.

Built and maintained by [EthicalMaster](https://github.com/EthicalMaster).

[Live workspace](https://axiom-lab-silk.vercel.app) &nbsp;·&nbsp; [Source](https://github.com/EthicalMaster/AXIOM-LAB) &nbsp;·&nbsp; [Issues](https://github.com/EthicalMaster/AXIOM-LAB/issues)

</div>
