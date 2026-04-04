# SHE-INTEL INDIA

Context-aware predictive health intelligence app for Indian women with FastAPI backend and vanilla frontend.

## Features

- **Authentication** - User registration, login, JWT tokens
- **Period Tracking** - Log periods, view history, cycle prediction
- **Symptom Logging** - Track fatigue, sleep quality, mood
- **Health Analysis** - ML-powered risk assessment for:
  - Iron Deficiency Anemia
  - PCOS
  - Thyroid Disorder
  - Diabetes Risk
  - Vitamin D Deficiency
- **India Context** - State-based diet recommendations, AQI data, government schemes, lab cost estimates
- **Dark/Light Mode** - Toggle theme in navbar

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite, XGBoost ML
- **Frontend**: Vanilla HTML/CSS/JS
- **Testing**: Pytest

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js (for frontend server)

### 1. Clone and Setup Backend

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 2. Run Backend

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002
```

Backend runs at: http://localhost:8002

### 3. Run Frontend

```bash
cd frontend
npx serve -l 5173
```

Or using Python:
```bash
cd frontend
python -m http.server 5173
```

Frontend runs at: http://localhost:5173

### 4. Run Tests

```bash
cd backend
pytest tests/ -v
```

### 5. Seed Demo Data (Optional)

```bash
cd backend
python scripts/seed_demo_data.py
```

## Demo Accounts

After seeding demo data, use these credentials:

| Email | Password |
|-------|----------|
| demo_10016dc7@example.com | secret123 |
| demo_71c30ef8@example.com | secret123 |
| demo_c04fc623@example.com | secret123 |

## Project Structure

```
she-intel-india/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── database.py      # SQLAlchemy setup
│   │   ├── auth.py          # JWT authentication
│   │   ├── models/          # Database models
│   │   ├── routers/         # API endpoints
│   │   ├── ml/              # ML model
│   │   └── services/        # India context data
│   ├── tests/               # Pytest tests
│   ├── scripts/             # Seed data script
│   └── requirements.txt
├── frontend/
│   ├── index.html           # Main HTML
│   ├── app.js               # Frontend logic
│   └── styles.css           # Styling
└── README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register new user |
| `/auth/login` | POST | Login user |
| `/auth/me` | GET | Get current user |
| `/periods/` | POST/GET | Create/list periods |
| `/periods/calendar` | GET | Get calendar with prediction |
| `/symptoms/` | POST/GET | Create/list symptoms |
| `/analysis/analyze` | POST | Get health analysis |
| `/analysis/history` | GET | Get analysis history |

## Environment Variables

Optional (defaults work out of the box):
- `DATABASE_URL` - SQLite database path
- `XGB_MODEL_ARTIFACT_PATH` - ML model path

## License

MIT