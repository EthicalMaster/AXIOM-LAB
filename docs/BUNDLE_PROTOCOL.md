# Git bundle protocol — required for subsequent updates

## What every bundle contains

- `manifest.json`: bundle ID, purpose, required base Git revision, affected modules, tests, learning objectives.
- `changes.patch`: text/binary Git patch generated from the approved baseline (`git diff --binary`).
- `APPLY.md`: Windows PowerShell application procedure and rollback instructions.
- `REVIEW.md`: manual behaviour checks and learning questions.
- Source changes and documentation changes are included in the patch.

## Safe application (PowerShell from repository root)

1. Confirm you are on the intended branch and have a clean working tree (`git status`).
2. Check that `git rev-parse HEAD` matches the required base commit listed in the manifest.
3. Create a topic branch: `git switch -c phase/01a-dataset-import`.
4. Extract the bundle **outside** the repository (e.g., `$HOME\Downloads\AXIOM-BUNDLE-01A`).
5. `git apply --check "$HOME\Downloads\AXIOM-BUNDLE-01A\changes.patch"`.
6. Only if validation succeeds: `git apply "$HOME\Downloads\AXIOM-BUNDLE-01A\changes.patch"`.
7. Install changed dependencies if required by the bundle, then run all automated and manual checks in `REVIEW.md`.
8. Explain important concepts, update your own observations in the learning/test logs, and review `git diff`.
9. Commit only when green: `git add .; git commit -m "feat(phase-01a): implement dataset import"`.
10. Merge or fast-forward into `main` after verification; push both history and final `main` to GitHub. Detailed per-bundle commands will be provided.

## Why patch bundles?

A patch changes only reviewed files, preserving Git history and existing working functionality. It can be preflight checked and fails instead of silently replacing the entire folder. Each bundle is generated for the exact approved base commit, so **never skip bundles or apply one to an unrelated revision**.

## Failure rule

Never force an incompatible patch. Report `git status`, `git rev-parse HEAD`, the bundle ID, the original command, and its full error. Keep failing tests and unsuccessful investigations documented.

## Important limitation

Bundle delivery is not a remote automatic updater. You manually apply and verify it; deployment changes are separate and require explicit approval. If a future bundle includes non-patchable content or migrations, its manifest and procedures must clearly describe those steps.
