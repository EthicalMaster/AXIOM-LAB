"""Cloud-only connections and restricted storage identity. No administrator key."""
from __future__ import annotations

import os
import re
import time
from threading import Lock
from urllib.parse import urlsplit
from contextlib import contextmanager

import httpx

BUCKET = "axiom-datasets"
MAX_FILE_BYTES = 4 * 1024 * 1024
_token_lock = Lock()
_token = None
_token_expiry = 0.0


def enabled() -> bool:
    return os.getenv("AXIOM_STORAGE_MODE", "local") == "supabase"


def configuration() -> None:
    from app.hosted import https_origin
    if not enabled() or os.getenv("AXIOM_PUBLIC_MODE") != "1":
        raise ValueError("Cloud deployment requires protected Supabase mode.")
    if len(os.getenv("AXIOM_ACCESS_TOKEN", "").strip()) < 32:
        raise ValueError("Cloud deployment requires a strong access token.")
    origin = os.getenv("AXIOM_PUBLIC_ORIGIN", "")
    if https_origin(origin) != origin:
        raise ValueError("Cloud deployment requires an exact frontend origin.")
    for key in ("AXIOM_DATABASE_URL", "AXIOM_SUPABASE_URL", "AXIOM_SUPABASE_PUBLISHABLE_KEY",
                "AXIOM_STORAGE_EMAIL", "AXIOM_STORAGE_PASSWORD", "AXIOM_STORAGE_UID"):
        if not os.getenv(key, "").strip():
            raise ValueError("Cloud configuration is incomplete: " + key)
    from psycopg.conninfo import conninfo_to_dict
    options = conninfo_to_dict(os.environ["AXIOM_DATABASE_URL"])
    if not re.fullmatch(r"axiom_backend(?:\.[a-z0-9]+)?", options.get("user", "")):
        raise ValueError("Cloud database requires the dedicated axiom_backend role.")
    host = options.get("host", "")
    if not re.fullmatch(r"[a-z0-9.-]+\.pooler\.supabase\.com", host) or options.get("port") != "6543":
        raise ValueError("Cloud database requires the Supabase transaction pooler.")
    storage_url = os.environ["AXIOM_SUPABASE_URL"]
    if not re.fullmatch(r"https://[a-z0-9]+\.supabase\.co", storage_url):
        raise ValueError("Invalid Supabase project URL.")
    if not re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", os.environ["AXIOM_STORAGE_UID"]):
        raise ValueError("Invalid dedicated storage identity.")
    if not os.environ["AXIOM_SUPABASE_PUBLISHABLE_KEY"].startswith("sb_publishable_"):
        raise ValueError("Use a publishable key, not a service-role key.")


@contextmanager
def database():
    import psycopg
    from psycopg.rows import dict_row
    with psycopg.connect(os.environ["AXIOM_DATABASE_URL"], connect_timeout=5,
                         sslmode="verify-full", sslrootcert="system",
                         prepare_threshold=None, row_factory=dict_row) as conn:
        conn.execute("SET LOCAL search_path TO axiom_lab, pg_catalog")
        conn.execute("SET LOCAL statement_timeout TO '8s'")
        conn.execute("SET LOCAL lock_timeout TO '5s'")
        yield conn


def _access_token(client: httpx.Client) -> str:
    global _token, _token_expiry
    with _token_lock:
        if _token and time.monotonic() < _token_expiry:
            return _token
        response = client.post(os.environ["AXIOM_SUPABASE_URL"] + "/auth/v1/token",
            params={"grant_type": "password"},
            headers={"apikey": os.environ["AXIOM_SUPABASE_PUBLISHABLE_KEY"]},
            json={"email": os.environ["AXIOM_STORAGE_EMAIL"], "password": os.environ["AXIOM_STORAGE_PASSWORD"]})
        response.raise_for_status()
        payload = response.json()
        if payload["user"]["id"] != os.environ["AXIOM_STORAGE_UID"]:
            raise ValueError("Unexpected storage identity.")
        _token = payload["access_token"]
        _token_expiry = time.monotonic() + max(0, min(1800, int(payload["expires_in"]) - 60))
        return _token


def _object_url(dataset_id: str, extension: str, *, download: bool = False) -> str:
    if not re.fullmatch(r"[0-9a-f]{32}", dataset_id) or extension not in (".csv", ".xls", ".xlsx"):
        raise ValueError("Invalid object identifier.")
    prefix = "/storage/v1/object/authenticated/" if download else "/storage/v1/object/"
    return os.environ["AXIOM_SUPABASE_URL"] + prefix + BUCKET + "/" + dataset_id + "/original" + extension


def write_original(dataset_id: str, extension: str, raw: bytes) -> None:
    if not 0 < len(raw) <= MAX_FILE_BYTES:
        raise ValueError("Cloud file limit exceeded.")
    with httpx.Client(timeout=15, follow_redirects=False, trust_env=False) as client:
        token = _access_token(client)
        response = client.post(_object_url(dataset_id, extension), content=raw,
            headers={"apikey": os.environ["AXIOM_SUPABASE_PUBLISHABLE_KEY"],
                     "Authorization": "Bearer " + token, "Content-Type": "application/octet-stream",
                     "x-upsert": "false"})
        response.raise_for_status()


def read_original(dataset_id: str, extension: str) -> bytes:
    with httpx.Client(timeout=15, follow_redirects=False, trust_env=False) as client:
        token = _access_token(client)
        with client.stream("GET", _object_url(dataset_id, extension, download=True),
                headers={"apikey": os.environ["AXIOM_SUPABASE_PUBLISHABLE_KEY"],
                         "Authorization": "Bearer " + token}) as response:
            response.raise_for_status()
            result = bytearray()
            for chunk in response.iter_bytes():
                if len(result) + len(chunk) > MAX_FILE_BYTES:
                    raise ValueError("Stored object exceeds cloud file limit.")
                result.extend(chunk)
        return bytes(result)


def take_budget(bucket: str, limit: int, seconds: int) -> bool:
    # Fixed windows; one atomic write per operation, no unbounded keys.
    if bucket not in {"login", "api", "upload", "compute", "guide", "ai_minute", "ai_day"}:
        raise ValueError("Unknown budget.")
    with database() as conn:
        row = conn.execute("""
            INSERT INTO rate_windows(bucket, window_start, request_count)
            VALUES (%s, floor(extract(epoch from now()) / %s)::bigint, 1)
            ON CONFLICT(bucket) DO UPDATE SET
                window_start=EXCLUDED.window_start,
                request_count=CASE WHEN rate_windows.window_start=EXCLUDED.window_start
                    THEN rate_windows.request_count+1 ELSE 1 END
            WHERE rate_windows.window_start<>EXCLUDED.window_start OR rate_windows.request_count<%s
            RETURNING request_count
        """, (bucket, seconds, limit)).fetchone()
        return row is not None
