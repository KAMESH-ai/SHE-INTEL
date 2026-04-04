import sys
from pathlib import Path

_tests_dir = Path(__file__).resolve().parent
_backend_dir = _tests_dir.parent
_project_root = _backend_dir.parent

# Ensure backend/ is on sys.path so that `from app.main import app` works
# in test_backend.py (app.* imports are relative to backend/).
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

# Append project root so that `import backend.main` works in test_shim.py.
if str(_project_root) not in sys.path:
    sys.path.append(str(_project_root))
