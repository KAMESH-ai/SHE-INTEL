# Shim: allows `uvicorn backend.main:app` to work from the project root.
# Adds backend/ to sys.path so that `app.*` imports in backend/app/main.py resolve correctly.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.main import app  # noqa: F401, E402
