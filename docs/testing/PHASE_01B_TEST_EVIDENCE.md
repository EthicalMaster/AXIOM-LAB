# Phase 01B test evidence — builder environment

**Execution:** `PYTHONPATH=backend pytest backend/tests -q` on Python 3.13.5.

**Result:** `26 passed` (including all existing 01A tests; 12 new 01B tests).

**Coverage:** numeric/categorical/boolean/datetime/mixed/empty patterns, blank cells, literal `NA`, leading zeros, non-finite values, bounded distinct counting, original hash mismatch, invalid IDs, real XLSX worksheet, formula non-execution, blank-row consistency and API schema.

**Not verified in this environment:** `npm install`, `npm run test`, `npm run typecheck`, `npm run build`, UI browser interaction, positive legacy XLS sample on Windows. Installation of npm dependencies stalled under current network restrictions; no false success is claimed.

The project owner must run the documented Windows suite and record actual results before accepting and committing the milestone.
