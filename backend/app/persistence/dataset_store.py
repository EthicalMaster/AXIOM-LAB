"""Local single-user dataset persistence. Original bytes are never overwritten."""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from app.services.dataset_validation import DatasetProfile


def _data_root() -> Path:
    # Parent of backend/ is the project root.
    return Path(os.environ.get("AXIOM_DATA_DIR", str(Path(__file__).resolve().parents[3] / "runtime"))).resolve()


def _database(root: Path) -> sqlite3.Connection:
    root.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(root / "axiom.sqlite3", timeout=5)
    connection.execute("""CREATE TABLE IF NOT EXISTS datasets (
        id TEXT PRIMARY KEY, original_name TEXT NOT NULL, file_format TEXT NOT NULL,
        sha256 TEXT NOT NULL, size_bytes INTEGER NOT NULL, uploaded_at TEXT NOT NULL,
        row_count INTEGER NOT NULL, column_count INTEGER NOT NULL,
        headers_json TEXT NOT NULL, sheet_name TEXT, sheet_names_json TEXT NOT NULL,
        warnings_json TEXT NOT NULL, storage_relative_path TEXT NOT NULL
    )""")
    return connection


def save_dataset(raw: bytes, original_name: str, extension: str, profile: DatasetProfile) -> dict:
    root = _data_root()
    dataset_id = uuid.uuid4().hex
    sha256 = hashlib.sha256(raw).hexdigest()
    uploaded_at = datetime.now(timezone.utc).isoformat()
    relative_path = Path("datasets") / dataset_id / f"original{extension}"
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=False)
    try:
        # 'xb' refuses overwrite, even if an unexpected path already exists.
        with destination.open("xb") as handle:
            handle.write(raw)
        with closing(_database(root)) as connection, connection:
            connection.execute(
                """INSERT INTO datasets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (dataset_id, original_name, profile.file_format, sha256, len(raw), uploaded_at,
                 profile.row_count, profile.column_count, json.dumps(profile.headers),
                 profile.worksheet, json.dumps(profile.sheet_names), json.dumps(profile.warnings),
                 str(relative_path.as_posix())),
            )
    except Exception:
        if destination.exists():
            destination.unlink()
        destination.parent.rmdir()
        raise
    return {
        "id": dataset_id, "original_name": original_name, "format": profile.file_format,
        "sha256": sha256, "size_bytes": len(raw), "uploaded_at": uploaded_at,
        "row_count": profile.row_count, "column_count": profile.column_count,
        "headers": profile.headers, "worksheet": profile.worksheet,
        "sheet_names": profile.sheet_names, "warnings": profile.warnings,
    }


def find_dataset(dataset_id: str) -> dict | None:
    root = _data_root()
    if not (root / "axiom.sqlite3").exists():
        return None
    with closing(_database(root)) as connection:
        connection.row_factory = sqlite3.Row
        record = connection.execute(
            "SELECT * FROM datasets WHERE id = ?", (dataset_id,)
        ).fetchone()
    if record is None:
        return None
    return {
        "id": record["id"], "original_name": record["original_name"],
        "format": record["file_format"], "sha256": record["sha256"],
        "size_bytes": record["size_bytes"], "uploaded_at": record["uploaded_at"],
        "row_count": record["row_count"], "column_count": record["column_count"],
        "headers": json.loads(record["headers_json"]), "worksheet": record["sheet_name"],
        "sheet_names": json.loads(record["sheet_names_json"]),
        "warnings": json.loads(record["warnings_json"]),
    }
