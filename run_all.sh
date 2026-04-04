#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
PYTHON_BIN="/Users/kamesh/Documents/ossame hack/.venv/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python environment not found at: $PYTHON_BIN"
  exit 1
fi

is_port_busy() {
  lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1
}

if is_port_busy 8002; then
  echo "Backend already running on port 8002"
else
  cd "$BACKEND_DIR"
  nohup "$PYTHON_BIN" -m uvicorn app.main:app --host 0.0.0.0 --port 8002 > /tmp/she_intel_backend.log 2>&1 &
  echo $! > /tmp/she_intel_backend.pid
fi

if is_port_busy 5173; then
  echo "Frontend already running on port 5173"
else
  cd "$FRONTEND_DIR"
  nohup "$PYTHON_BIN" -m http.server 5173 > /tmp/she_intel_frontend.log 2>&1 &
  echo $! > /tmp/she_intel_frontend.pid
fi

echo "Backend: http://localhost:8002"
echo "Frontend: http://localhost:5173"
echo "Logs: /tmp/she_intel_backend.log, /tmp/she_intel_frontend.log"
