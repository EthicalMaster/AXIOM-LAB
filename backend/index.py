"""Vercel entry point: never expose local mode or temporary persistence."""
from app.persistence.cloud import configuration

configuration()
from app.main import app
