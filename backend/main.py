"""ASGI entrypoint shim.

Some hosts/service configs may start the app as:
  uvicorn backend.main:app

Our real FastAPI app lives at backend/app/main.py (module: backend.app.main).
This file keeps both working.
"""

from backend.app.main import app
