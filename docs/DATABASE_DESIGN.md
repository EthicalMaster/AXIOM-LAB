# Database design — proposed (not implemented)

Phase 0 uses **no persistent database**. Phase 01 introduces SQLite metadata and local artifact storage.

Planned entities: Dataset, DatasetVersion, Experiment, ExperimentConfigRevision, Run, ResultArtifact, ExecutionDiagnostic.

Critical relationships:
- Dataset -> multiple immutable DatasetVersion records.
- Experiment -> multiple configuration revisions and runs.
- Run -> specific dataset version(s), frozen config, method, statuses, seed as applicable, environment metadata.
- Run -> zero or more result artifacts, warnings and error diagnostics.

Design details (IDs, relationships, migrations, storage strategy, cleanup) must be reviewed in Phase 01A before any database schema is implemented.
