"""
ASGI entrypoint shim.

Some hosts (e.g. Render) may be configured to start the app as:
  uvicorn backend.main:app

The actual FastAPI application lives at backend/app/main.py
(importable as ``backend.app.main``).  This shim re-exports ``app``
so that both of the following start commands work without changes to
the host's service configuration:

  uvicorn backend.main:app          # legacy / fallback
  uvicorn backend.app.main:app      # preferred / unambiguous
"""
from backend.app.main import app  # noqa: F401  re-export
