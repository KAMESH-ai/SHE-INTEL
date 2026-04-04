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

## Run the Project

1. Start backend API:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

Backend URL: http://localhost:8002

> **Production note:** On Render and other platforms that run from the project root, the FastAPI app is started via the shim at `backend/main.py`:
> ```bash
> uvicorn backend.main:app --host 0.0.0.0 --port $PORT
> ```
> `backend/main.py` re-exports the `app` object from `backend/app/main.py`, so both `uvicorn backend.main:app` and `cd backend && uvicorn app.main:app` point to the same application.

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
│   ├── __init__.py          # makes backend/ a Python package
│   ├── main.py              # shim: re-exports app from backend/app/main.py
│   ├── app/
│   │   ├── __init__.py      # makes backend/app/ a Python package
│   │   └── main.py          # FastAPI application entry point
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