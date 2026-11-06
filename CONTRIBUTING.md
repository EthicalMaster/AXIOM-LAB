# Development guidelines

1. Read the master specification and architectural decisions before changing system boundaries.
2. Work on one approved vertical slice at a time.
3. Explain scientific principles and algorithms before implementation.
4. Do not introduce untrusted Python/shell execution, fake scientific results, silent data modification, or secrets in Git.
5. Run unit tests, typechecks/build, relevant scientific reference tests, and manual workflows.
6. Preserve actual failures in development/test/problem logs.
7. Commit a bundle only after its acceptance conditions pass and the developer understands its important responsibilities.
