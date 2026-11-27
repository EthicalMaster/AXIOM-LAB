# Release assurance — v1.0 RC

Baseline: `6d9e80ba3dfaadfc5aea86f7d999f3618a345994` (2026-11-27). Restricted single-operator candidate, not certified public infrastructure.

## Commit-specific evidence

- [Foundation checks](https://github.com/EthicalMaster/AXIOM-LAB/actions/runs/46027575610): success (backend and frontend tests, typecheck, build and release assets).
- [Security workflow](https://github.com/EthicalMaster/AXIOM-LAB/actions/runs/46027575611): failure. Private-file path check passed; npm audit logged zero vulnerabilities. Python audit exited with `axiom-lab-backend: distribution marked as editable` before completing.
- Correction: install in isolated environment, check dependency consistency, export all exact versions except unpublished first-party project and audit strictly. No vulnerability IDs suppressed. Fresh green run required.

| Priority | Finding | Disposition |
|---|---|---|
| Blocker | Python audit incomplete | Correct workflow, rerun, remediate real findings |
| Blocker | Docker, HTTPS, persistent storage and hosted recovery unverified | Protected staging; follow RELEASE_GATE.md |
| High | Private-file scan is paths only, not secret contents/history | Secret scanning, history review, container scans, independent security review |
| High | Python dependency ranges and mutable image tags | Resolve, audit and record deployed versions/image digests |
| High | Shared token and process-local budgets | Restricted one trusted operator only; no multi-tenant release |
| Medium | Browser accessibility, mobile, Lens and live provider unverified | Manual acceptance |
| Medium | Stale docs | Updated; preserve historical phase records |
| Medium | No explicit license | Owner chooses before inviting external reuse |

## Acceptance gates

- [ ] New commit foundation and security workflows green; review advisory findings.
- [ ] Synthetic CSV and Excel import; reject invalid input; check known stats, math and ML; save/reopen/compare/replay chart and inspect reports.
- [ ] Both themes, loading/error, zoom/pan, small screens, keyboard focus, reduced motion, Guide and Lens selection/consent/fallback; test provider using synthetic context only.
- [ ] Docker build/start and persistent restart; approved synthetic capacity probe, offline backup and independent restore.
- [ ] Protected staging: HTTPS, exact origin, login/logout/CSRF, budgets, no-store, monitoring and rollback.
- [ ] Resolve security/image/secret findings, record deployed versions, choose license and tag only after acceptance.

No production traffic was tested. Source and automated checks do not replace independent scientific or security review. UI, motion and scientific behavior unchanged by this patch. Do not publish private data or keys.
