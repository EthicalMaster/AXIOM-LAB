# Development guidelines

1. Read the master specification and architectural decisions before changing system boundaries.
2. Work on one approved vertical slice at a time.
3. Explain scientific principles and algorithms before implementation.
4. Do not introduce untrusted Python/shell execution, fake scientific results, silent data modification, or secrets in Git.
5. Run unit tests, typechecks/build, relevant scientific reference tests, and manual workflows.
6. Preserve actual failures in development/test/problem logs.
7. Commit a bundle only after its acceptance conditions pass and the developer understands its important responsibilities.

## Code quality rule — adopted November 20, 2026

Before adding code: (1) name the behaviour and necessary invariant, (2) reuse the existing service/contracts where appropriate, (3) reject new dependencies and abstraction layers without a specific benefit, (4) prefer the shortest readable implementation that preserves correctness and safe failure modes, (5) add numerical/edge-case regression tests, and (6) document the decision, alternatives and disadvantage. Keep source bytes immutable and avoid hidden side effects.

At the final release gate, perform a **dead-code and redundant-module audit**, consolidate duplicated logic only when tests prove equivalence, remove stale placeholder UI and docs, benchmark performance hotspots, and run a complete security, numerical, usability, accessibility and load review. No uncontrolled refactoring immediately before release.
