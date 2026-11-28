# Third-party notices and dependency review

AXIOM LAB uses independently licensed third-party software. Those components retain their original copyrights and licenses.

## Frontend direct dependencies

| Package | Resolved version | Declared license in package-lock.json | Scope |
|---|---|---|---|
| `@supabase/supabase-js` | 2.119.2 | MIT | Runtime |
| `react` | 19.3.1 | MIT | Runtime |
| `react-dom` | 19.3.1 | MIT | Runtime |
| `@types/node` | 22.20.5 | MIT | Development |
| `@types/react` | 19.3.0 | MIT | Development |
| `@types/react-dom` | 19.3.0 | MIT | Development |
| `@vitejs/plugin-react` | 5.2.0 | MIT | Development |
| `typescript` | 5.9.3 | Apache-2.0 | Development |
| `vite` | 7.3.7 | MIT | Development |
| `vitest` | 4.1.12 | MIT | Development |

## Backend dependencies

See `backend/pyproject.toml` for the declared runtime and development dependencies. Resolved Python versions and installed license texts vary by environment; inspect the exact build before distributing it.

## Release compliance checklist (not a completed audit)

- Review all direct and transitive dependencies, fonts, images, code snippets and other assets for provenance and license compatibility.
- Preserve the required third-party copyright, license and attribution texts in source distributions and distributed builds. This inventory is not a substitute for those texts.
- Inspect `frontend/package-lock.json`, installed npm package license files, and installed Python distribution metadata and license files for the actual release.
- Resolve any unknown, incompatible or restricted materials before publishing. Record the reviewed versions and preserve necessary notices.
- Verify that the hosted source link corresponds to both the deployed frontend and backend; do not publish environment secrets or private research data.

The npm entries above are derived from the checkout lockfile at installation time. They are not an independent legal audit.
