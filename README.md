# SHE-INTEL INDIA

Context-aware predictive health intelligence app for Indian women, built with a FastAPI backend and a vanilla JavaScript frontend.

## Features

- User authentication (register/login with JWT)
- Period tracking and cycle history
- Symptom logging with fatigue/sleep indicators
- ML-powered health risk analysis
- India-specific context recommendations

## Tech Stack

- Backend: FastAPI, SQLAlchemy, SQLite, XGBoost
- Frontend: HTML, CSS, JavaScript
- Testing: Pytest

## Prerequisites

- Python 3.10+
- pip
- Node.js (optional, only if using `npx serve` for frontend)

## Local Setup

1. Clone the repository:

```bash
git clone <your-repo-url>
cd she-intel-india
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

## Deployment (Render)

The correct Uvicorn start command is:

```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The FastAPI application lives at `backend/app/main.py`. When Uvicorn is launched from
within the `backend/` directory the module path is `app.main:app`. Using
`backend.main:app` (without `cd backend`) will cause:

```
Error loading ASGI app. Could not import module 'backend.main'.
```

This is already set correctly in `render.yaml`. If you see this error on Render, check
**Settings → Start Command** in the Render dashboard and make sure it matches the
command above.

## Run the Project

1. Start backend API:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

Backend URL: http://localhost:8002

2. Start frontend (new terminal):

Option A (Node):

```bash
cd frontend
npx serve -l 5173
```

Option B (Python):

```bash
cd frontend
python3 -m http.server 5173
```

Frontend URL: http://localhost:5173

## Run Tests

From the project root:

```bash
cd backend
pytest tests -v
```

## Optional: Seed Demo Data

```bash
cd backend
python3 scripts/seed_demo_data.py
```

## Deploy on Railway

This repo is configured for a single-service Railway deploy (backend serves frontend from `/`).

1. Push your latest code to GitHub.
2. In Railway, create a new project from this repo.
3. Ensure the service uses these settings (already encoded in `Procfile` and `railway.json`):

```bash
Start command: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

4. Add environment variables in Railway:

```bash
DATABASE_URL=sqlite:///./she_intel.db
XGB_MODEL_ARTIFACT_PATH=backend/app/ml/artifacts/xgb_model.joblib
```

5. Deploy.

After deployment:

- App UI: `https://<your-service>.up.railway.app/`
- API status: `https://<your-service>.up.railway.app/api`

## Important Git Ignore Rules

This repository is configured to exclude non-source folders/files such as:

- `node_modules/`
- `.build/`
- `.env`
- `__pycache__/`

## Project Structure

```text
she-intel-india/
├── backend/
│   ├── app/
│   ├── requirements.txt
│   ├── scripts/
│   └── tests/
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── render.yaml
└── README.md
```