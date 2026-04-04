"""Minimal import tests for the backend.main shim.

These ensure that `uvicorn backend.main:app` can resolve the FastAPI app
from the project root without an import error.
"""
import os
import tempfile
from pathlib import Path

os.environ.setdefault("DATABASE_URL", f"sqlite:///{Path(tempfile.gettempdir()) / 'she_intel_test.db'}")
os.environ.setdefault("XGB_MODEL_ARTIFACT_PATH", str(Path(tempfile.gettempdir()) / 'she_intel_xgb_model.joblib'))

import backend.main  # noqa: E402
from fastapi import FastAPI  # noqa: E402


def test_backend_main_is_importable():
    """backend.main module must be importable (no ImportError)."""
    assert backend.main is not None


def test_backend_main_app_is_fastapi():
    """backend.main.app must be a FastAPI instance (the shim re-exports it)."""
    assert isinstance(backend.main.app, FastAPI)
