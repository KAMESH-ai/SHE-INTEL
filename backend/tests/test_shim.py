"""Minimal import tests for the backend.main shim.

These ensure that `uvicorn backend.main:app` can resolve the FastAPI app
from the project root without an import error.
"""
import backend.main
from fastapi import FastAPI


def test_backend_main_is_importable():
    """backend.main module must be importable (no ImportError)."""
    assert backend.main is not None


def test_backend_main_app_is_fastapi():
    """backend.main.app must be a FastAPI instance (the shim re-exports it)."""
    assert isinstance(backend.main.app, FastAPI)
