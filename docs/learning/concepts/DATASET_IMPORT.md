# Learning note — Dataset input is not yet data analysis

## 1. Problem

Scientific calculations are only meaningful when users can inspect and trust the data entering them. AXIOM LAB therefore treats importing a dataset as a validated engineering operation, not just a file-picker UI event.

## 2. Key concepts

- **Encoding:** CSV stores text as bytes. This milestone explicitly decodes UTF-8 (and UTF-8 with BOM) to avoid hidden, platform-specific character conversion.
- **Structure:** The header defines named columns. Rows should match their declared shape. Duplicate or empty column names are rejected before more complex analysis.
- **Raw vs derived:** Original file bytes remain unchanged. The table preview is derived display data; clipping a preview cell must not change the original upload.
- **Fingerprint:** SHA-256 computes a digest of the original bytes. Identical bytes produce the same digest, which is useful for integrity checks. It is **not encryption**.
- **Opaque identity:** A random dataset ID avoids filename collisions and prevents user-supplied paths from becoming filesystem destinations.
- **API contract:** `POST /api/v1/datasets/import` receives multipart form data, validates it, stores raw bytes and metadata, and returns a defined response shape.
- **Two layers of validation:** The browser checks extensions and size for quick feedback; the server remains authoritative because client-side checks can be bypassed.

## 3. Implementation separation

`api/datasets.py` is responsible for HTTP input/output; `services/dataset_validation.py` for bounded and format-aware inspection; `persistence/dataset_store.py` for saved original bytes and SQLite metadata. This prevents scientific parsers from depending directly on React or API routing.

## 4. What we can and cannot conclude

We can verify structural properties: format, number of columns, counted nonblank data rows, header names, file fingerprint, and preview. We **cannot** yet conclude column data types, correlation, statistical significance, or dataset suitability for a particular scientific method.

## 5. Exercise

Create a CSV with a single duplicate header and predict the API response before trying it. Then create a CSV with a blank line and explain why its raw bytes and counted data rows differ. Use the tests as evidence, not as an answer key to memorize.
