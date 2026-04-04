#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8002}"
EMAIL="demo_walkthrough_$(date +%s)@example.com"
PASSWORD="secret123"

echo "1) Register"
REGISTER=$(curl -sS -X POST "$API_URL/auth/register" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"name\":\"Walkthrough User\",\"age\":30,\"state\":\"Tamil Nadu\"}")
echo "$REGISTER" | head -c 200; echo

echo "2) Login"
LOGIN=$(curl -sS -X POST "$API_URL/auth/login" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
TOKEN=$(echo "$LOGIN" | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')
if [[ -z "$TOKEN" ]]; then
  echo "Failed to parse token"
  exit 1
fi
echo "Token acquired"

echo "3) Create periods"
curl -sS -X POST "$API_URL/periods/" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"start_date":"2026-03-01T00:00:00","end_date":"2026-03-05T00:00:00","flow_level":"Medium","symptoms":"cramps"}' >/dev/null
curl -sS -X POST "$API_URL/periods/" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"start_date":"2026-02-01T00:00:00","end_date":"2026-02-05T00:00:00","flow_level":"Heavy","symptoms":"fatigue"}' >/dev/null
echo "Periods created"

echo "4) Create symptom"
curl -sS -X POST "$API_URL/symptoms/" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"description":"Feeling tired with dizziness and poor sleep","fatigue_level":8,"sleep_quality":4,"mood":"anxious"}' >/dev/null
echo "Symptom created"

echo "5) Analyze"
ANALYSIS=$(curl -sS -X POST "$API_URL/analysis/analyze" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"description":"Feeling tired with dizziness and poor sleep","fatigue_level":8,"sleep_quality":4,"mood":"anxious"}')
echo "$ANALYSIS" | head -c 400; echo

echo "6) Fetch history"
HISTORY=$(curl -sS "$API_URL/analysis/history" -H "Authorization: Bearer $TOKEN")
echo "$HISTORY" | head -c 300; echo

echo "Walkthrough complete for $EMAIL"
