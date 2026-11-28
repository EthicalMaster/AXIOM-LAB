"""Vercel entry point for AXIOM LAB."""
import os

from app.hosted import preflight

for name in (
    "AXIOM_PUBLIC_MODE",
    "AXIOM_GOOGLE_AUTH",
    "AXIOM_MULTI_USER",
    "AXIOM_CLOUD_STORAGE",
    "AXIOM_DISTRIBUTED_RPM",
):
    if os.getenv(name) != "1":
        raise RuntimeError(f"Required deployment setting missing: {name}")

if os.getenv("AXIOM_HOSTED_MODE", "1") != "1":
    raise RuntimeError("Hosted mode required.")

preflight()

from app.main import app
