# Data flow — implemented and planned

## Implemented in Phase 01A

```text
User chooses CSV/XLSX/XLS via React (client checks are advisory)
  -> POST multipart /api/v1/datasets/import (Vite proxy)
  -> backend reads at most 5 MiB + 1 byte
  -> server validates allowed format and file structure
  -> generate random dataset ID + SHA-256 of exact original bytes
  -> write original file exclusively under runtime/datasets/<id>/
  -> insert metadata into SQLite
  -> return HTTP 201 + metadata + first 8 text-preview rows
  -> React renders preview, warnings and fingerprint
```

Readback: `GET /api/v1/datasets/{id}` queries SQLite and returns metadata only. Uploaded file bytes are not currently downloadable through the API. No AI service sees dataset contents.

**Important:** A bounded text preview is derived output; it is not the authoritative dataset and is not a cleaning operation. Spreadsheet formulas are not executed. The first sheet is inspected and the selected sheet is included in the response.

## Planned later in Phase 01

```text
Stored immutable dataset
  -> column type inference and detailed data inspection (01B)
  -> independently validated statistical methods (01C)
  -> chart data, experiment, run and result records (01D)
```

Original user data must never be silently altered or added to source control, logs, or AI prompts.
