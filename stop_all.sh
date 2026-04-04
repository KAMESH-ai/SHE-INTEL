#!/usr/bin/env bash
set -euo pipefail

stop_from_pid_file() {
  local file="$1"
  local label="$2"
  if [[ -f "$file" ]]; then
    local pid
    pid="$(cat "$file")"
    if kill -0 "$pid" >/dev/null 2>&1; then
      kill "$pid"
      echo "Stopped $label (PID $pid)"
    else
      echo "$label already stopped"
    fi
    rm -f "$file"
  else
    echo "No PID file for $label"
  fi
}

stop_from_pid_file /tmp/she_intel_backend.pid "backend"
stop_from_pid_file /tmp/she_intel_frontend.pid "frontend"
