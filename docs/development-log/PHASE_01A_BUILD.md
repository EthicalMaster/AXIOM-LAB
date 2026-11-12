# Bundle 01A — build and review record

**Objective:** deliver the first real and bounded AXIOM LAB dataset import workflow.

**Changes:** new dataset validation service, datasets API, SQLite metadata + immutable raw-file storage, React import panel and preview, tests, scientific methodology and review documents.

**Trade-offs:** single-user local deployment; one worksheet parsed; no type inference, transformation, analysis, or experiment/run records yet. Input is limited to 5 MiB / 50k rows / 150 columns. No backend numerical correctness claims.

**Known environment limitations:** builder cannot fetch npm packages or xlrd for a positive XLS test. Windows functional and frontend validation must be performed by the project owner before commit.

**Next slice:** Phase 01B, dataset inspection and column profiling, only after Phase 01A verification and concept review.
