import os
import sys
import tempfile
from pathlib import Path

_tests_dir = Path(__file__).resolve().parent
_backend_dir = _tests_dir.parent
_project_root = _backend_dir.parent

# backend/ must take priority (position 0) so that `from app.main import app`
# in test_backend.py resolves to backend/app/main.py rather than any top-level
# `app` package that might exist on the system.
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

# project root is appended (lower priority) so that `import backend.main`
# works in test_shim.py without shadowing the `backend/app` package above.
if str(_project_root) not in sys.path:
    sys.path.append(str(_project_root))

# Shared environment variable defaults so all tests get a consistent DB and
# model path regardless of which test file loads first.
os.environ.setdefault("DATABASE_URL", f"sqlite:///{Path(tempfile.gettempdir()) / 'she_intel_test.db'}")
os.environ.setdefault("XGB_MODEL_ARTIFACT_PATH", str(Path(tempfile.gettempdir()) / "she_intel_xgb_model.joblib"))
