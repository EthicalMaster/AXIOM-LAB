# Phase 05B — Append-only experiment revisions

- **Why:** A run is evidence, not a mutable scratch value; reruns append monotonically numbered revisions.
- **API:** `POST /api/v1/experiments/{id}/runs` with a validated numeric column. Existing `GET` endpoints remain compatible.
- **Storage:** Forward-only SQLite addition `revision`, `source_run_id`; an immediate transaction assigns the next revision under concurrent writers. Original uploads are unchanged and checked for SHA-256 integrity before a new run.
- **Trade-off:** This is local single-user storage, not multi-tenant collaboration; one run stores a bounded observation chart, not an arbitrary pipeline.
- **Manual:** Import a two-column numeric dataset; create a run on the first column; open History; repeat the run; assert revision 2 appears while revision 1 remains readable. Modify the original on disk and verify run creation fails.
- **Tests:** `python -m pytest backend/tests -q`, frontend test/typecheck/build, browser reload and accessibility keyboard navigation.
