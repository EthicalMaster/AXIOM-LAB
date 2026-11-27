# Phase 07A — Scientific run reports

Recorded chart runs export in **PDF**, JSON and numeric CSV without model-authored interpretations. PDFs include dataset fingerprint, run metadata, method, parameters, environment, observation counts, sampled warning, first 20 recorded points, and limitations. JSON contains the complete saved record. CSV contains the saved chart points only (up to 250 displayed values), never full raw datasets.

Manual: save an experiment, open History, export all three formats, check PDF visually and SHA-256, check CSV sums against chart points and MIME types. Tamper with an ID: 404. Change `format` to `html`: 422.

Limit: no full scientific manuscript, arbitrary figure export, or proof of source availability. Reports describe stored observations; they never manufacture conclusions.
