# Phase 01B learning — Column inspection

## Problem

The Phase 01A preview shows cell text but does not say which values are numeric, categorical, dates or missing. Without inspection, running a statistical algorithm can be meaningless.

## Key ideas

- **Type inference:** a provisional guess based on observed values, unlike a confirmed measurement type.
- **Missingness:** the count of empty and whitespace-only cells. `NA` is treated as text, not silently discarded.
- **Cardinality:** how many distinct observed values exist. Exact tracking requires memory, so the present implementation reports a lower bound when it exceeds 1,000.
- **Immutability and integrity:** compare the original SHA-256 before deriving column metadata; never rewrite original input.
- **Conservative inference:** a leading-zero code like `0012` is categorical, even though it resembles a number.

## Trace the code

React `App.tsx` → `columnProfile.ts` → `GET /api/v1/datasets/{id}/profile` in `api/datasets.py` → `persistence/dataset_store.py` verified read → `services/column_profiling.py` → JSON → `ColumnProfilePanel.tsx`.

## Explain independently

1. Why is the backend (not the browser) authoritative about full-dataset types?
2. Why can an integer-looking string be an identifier rather than a measurement?
3. Why are missing cells different from a literal string `NA`?
4. Why does the profile sometimes show `>1000` instead of an exact distinct count?
5. Which problem arises if the stored original file changes after import?
6. What would have to change to support thousands of simultaneous profile requests?
