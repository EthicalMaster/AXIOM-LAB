"""PostgreSQL metadata and immutable Supabase objects with durable quota reservation."""
from __future__ import annotations
import hashlib
import json
import uuid
from datetime import datetime, timezone
from app.persistence import cloud
from app.persistence.dataset_store import DatasetStorageError, DatasetStorageQuotaError
from app.core.request_guard import setting


def _metadata(row):
    return {"id": row["id"], "original_name": row["original_name"], "format": row["file_format"],
            "sha256": row["sha256"], "size_bytes": row["size_bytes"], "uploaded_at": row["uploaded_at"],
            "row_count": row["row_count"], "column_count": row["column_count"],
            "headers": json.loads(row["headers_json"]), "worksheet": row["sheet_name"],
            "sheet_names": json.loads(row["sheet_names_json"]), "warnings": json.loads(row["warnings_json"])}


def save_dataset(raw, original_name, extension, profile):
    dataset_id = uuid.uuid4().hex
    sha = hashlib.sha256(raw).hexdigest()
    if not 0 < len(raw) <= cloud.MAX_FILE_BYTES:
        raise DatasetStorageQuotaError("Cloud files are limited to 4 MiB.")
    timestamp = datetime.now(timezone.utc).isoformat()
    path = f"{dataset_id}/original{extension}"
    # Reserve before network IO. Pending reservations count toward quota even on
    # ambiguous failures; administrator recovery must verify objects before release.
    with cloud.database() as conn:
        conn.execute("SELECT pg_advisory_xact_lock(7311001)")
        totals = conn.execute("SELECT count(*) AS count, coalesce(sum(size_bytes),0) AS bytes FROM datasets").fetchone()
        quota = setting("AXIOM_DATASET_QUOTA_MIB", 100, 100) * 1024 * 1024
        if totals["count"] >= setting("AXIOM_DATASET_MAX_COUNT", 500, 500) or totals["bytes"] + len(raw) > quota:
            raise DatasetStorageQuotaError("Original dataset storage allowance reached.")
        row = conn.execute("""INSERT INTO datasets
            (id,original_name,file_format,sha256,size_bytes,uploaded_at,row_count,column_count,
            headers_json,sheet_name,sheet_names_json,warnings_json,storage_relative_path,storage_state)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'pending') RETURNING *""",
            (dataset_id,original_name,profile.file_format,sha,len(raw),timestamp,profile.row_count,
             profile.column_count,json.dumps(profile.headers),profile.worksheet,json.dumps(profile.sheet_names),
             json.dumps(profile.warnings),path)).fetchone()
    try:
        cloud.write_original(dataset_id, extension, raw)
        with cloud.database() as conn:
            conn.execute("UPDATE datasets SET storage_state='ready' WHERE id=%s AND storage_state='pending'", (dataset_id,))
    except Exception:
        raise DatasetStorageError("Cloud upload incomplete; contact the workspace administrator.") from None
    return _metadata(row)


def find_dataset(dataset_id):
    with cloud.database() as conn:
        row = conn.execute("SELECT * FROM datasets WHERE id=%s AND storage_state='ready'", (dataset_id,)).fetchone()
        return _metadata(row) if row else None


def read_original_dataset(dataset_id, metadata):
    try:
        raw = cloud.read_original(dataset_id, "." + metadata["format"])
    except Exception:
        raise DatasetStorageError("The original dataset is unavailable.") from None
    if len(raw) != metadata["size_bytes"] or hashlib.sha256(raw).hexdigest() != metadata["sha256"]:
        raise DatasetStorageError("The original dataset failed its integrity check.")
    return raw
