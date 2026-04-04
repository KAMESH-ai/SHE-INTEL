"""
Smoke tests for the ASGI shim at backend/main.py.

These tests are intended to be run from the **project root** (not from
inside the ``backend/`` directory) so that ``backend`` resolves as a
top-level Python package:

    pytest tests/test_shim.py -v

Acceptance criteria (from the problem statement):
- ``import backend.main`` succeeds.
- ``backend.main.app`` is the FastAPI application instance.
"""
import importlib


def test_import_backend_main():
    """backend.main must be importable from the project root."""
    mod = importlib.import_module("backend.main")
    assert mod is not None


def test_backend_main_app_is_fastapi():
    """backend.main.app must be the FastAPI ASGI application."""
    from fastapi import FastAPI

    import backend.main as shim

    assert hasattr(shim, "app"), "backend.main must expose an 'app' attribute"
    assert isinstance(shim.app, FastAPI), (
        f"backend.main.app must be a FastAPI instance, got {type(shim.app)}"
    )


def test_backend_main_app_is_same_as_backend_app_main():
    """The shim must re-export the identical app object from backend.app.main."""
    import backend.main as shim
    import backend.app.main as real

    assert shim.app is real.app, (
        "backend.main.app should be the same object as backend.app.main.app"
    )
