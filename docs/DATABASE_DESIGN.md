# Database design — Phase 01A minimal dataset metadata

**Status:** Minimal SQLite schema implemented for dataset originals and inspection metadata. The full experiment engine is planned for later slices.

## Implemented datasets table

Primary key: random hex UUID `id`. Fields include `original_name`, `file_format`, `sha256`, `size_bytes`, `uploaded_at`, `row_count`, `column_count`, `headers_json`, `sheet_name`, `sheet_names_json`, `warnings_json`, `storage_relative_path`.

- Database: `runtime/axiom.sqlite3`.
- Original files: `runtime/datasets/<dataset-id>/original.<format>`.
- Storage writes are exclusive and never use the original filename as a destination.
- Duplicate byte-identical uploads receive unique IDs and share a SHA-256 value.
- There is no user/auth table, no artifact download endpoint, no data cleaning/revision table yet.
- SQLite table creation is initialized lazily for this local-only first slice. Proper database migrations are still required before more complex schema evolution.

## Planned entities

- Dataset and immutable DatasetVersion records (Phase 01B onward).
- Experiment, ExperimentConfigRevision, Run and ResultArtifact (minimal Phase 01D; expanded Phase 05).
- ExecutionDiagnostic and method-version metadata.

Future runs must reference exact dataset versions, configurations, diagnostic results, method versions and random seeds where applicable.
