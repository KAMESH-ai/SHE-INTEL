"""
Root-level conftest.py – sets the minimum environment variables required
by the backend application so that ``import backend.main`` succeeds when
pytest is run from the project root.
"""
import os
import tempfile
from pathlib import Path

os.environ.setdefault(
    "DATABASE_URL",
    f"sqlite:///{Path(tempfile.gettempdir()) / 'she_intel_shim_test.db'}",
)
os.environ.setdefault(
    "XGB_MODEL_ARTIFACT_PATH",
    str(Path(tempfile.gettempdir()) / "she_intel_xgb_model.joblib"),
)
