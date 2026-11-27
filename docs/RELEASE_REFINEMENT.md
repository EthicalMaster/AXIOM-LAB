# Release refinement: motion, UI, persistent AI and cleanup

Baseline: `0166879967e364e3372cdd2e68288022096a3e42` (accepted mathematics/graph upgrade).

## Design decisions
- Reuse existing theme tokens, semantic controls and graph camera. Shared SVG identity, request-driven loading, moving navigation indicator, staggered card entrances and a short theme transition. Native CSS and ResizeObserver keep the dependency footprint small; no new JS animation runtime. Decorative animations are disabled for reduced-motion preferences. No numerical count-up or invented progress is shown.
- Align the workspace at the top, prevent oversized content from forcing the layout wider, wrap long saved IDs, and improve details, action groups and guide scroll/focus. The guide restores launcher focus on close and disables conflicting topic actions while a question is pending. Session lock errors are visible and duplicate lock clicks are prevented. A skip link improves keyboard navigation.
- Local launcher reads the private `.env` before ASGI imports. Existing environment variables override file values. `python-dotenv` is the one new explicit Python dependency; no Vite secrets. Server-only credentials and optional advisory consent are unchanged. See `AI_SETUP.md`.
- Consolidate non-success handling in `apiFetch` (which already throws before returning a response); remove unreachable per-caller status checks, error response clones, old chart helpers used only by obsolete tests, and unused loader CSS. Reuse one number formatter rather than allocating it on every axis tick. Preserve all scientific modules, data records, graph camera and API routes. No sweeping dependency or algorithm removal without evidence.

## Verification
- Backend: 128 passed, including 7 new configuration cases. No actual AI provider calls in the tests.
- New frontend tests cover the shared request contract; local npm test/build/typecheck still required. Syntax/CSS validation and direct Node assertions supplement but do not replace the real frontend suite.
- Inspect both themes and all workspaces at desktop and narrow widths. Navigate by keyboard; open/close guide; try an import, long experiment ID, expanded details, theme switch, slow request, failed login and recovery. Check no visible movement with reduced motion enabled. Verify existing graph zoom/pinch/fullscreen and saved data remain correct.
- `.env` remains plaintext on disk and must be kept private. Restart server when changing it. Provider status reports configuration only, not authentication or successful remote generation.
- Full visual browser QA, dependency/security review, realistic deployed load tests, backup/restore and hosting setup remain release gates. Local code cleanup is not proof that every path in the repository is unused or every dependency is safe.
