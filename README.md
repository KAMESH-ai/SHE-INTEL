# SHE-INTEL INDIA

A context-aware health intelligence platform for Indian women with ML-powered health risk analysis, period tracking, and India-specific health context.

## Features

- **ML-Powered Health Analysis**: 14 trained models for health risk prediction (99%+ accuracy)
- **Period Tracking**: Log periods with date picker, view cycle history
- **Cycle Predictions**: Predict next period date based on cycle history
- **India-Specific Context**: Air quality data, government schemes, diet recommendations by region
- **Multi-language Support**: English, Hindi, Tamil, Malayalam
- **JWT Authentication**: Secure user login/registration
- **Dark Theme UI**: Modern glassmorphism design with green accents

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript (SPA)
- **Backend**: Python FastAPI
- **ML**: scikit-learn, CatBoost
- **Database**: SQLite

## Quick Start (Local)

### 1. Clone & Setup

```bash
git clone <repo-url>
cd she-intel-india
```

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Run Backend

```bash
python main.py
```

The API server will start at `http://localhost:8001`

### 4. Open Frontend

**Important**: Open the app via the backend server, not file://

Navigate to: **http://localhost:8001/app**

### 5. Login Credentials

- **Email**: demo@sheintel.in
- **Password**: demo123

Or register a new account via the Register form.

## Project Structure

```
she-intel-india/
├── index.html          # Frontend (SPA)
├── app.js              # Frontend utilities
├── backend/
│   ├── main.py         # FastAPI server
│   ├── ml_analyzer.py # ML models
│   ├── database.py    # SQLite database
│   ├── auth.py        # JWT authentication
│   ├── aqi_service.py # Air quality API
│   └── requirements.txt
├── README.md
└── SPEC.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register new user |
| `/auth/login` | POST | Login and get JWT |
| `/periods` | GET/POST | Get/Create period records |
| `/periods/prediction` | GET | Get cycle prediction |
| `/analyze` | POST | Run health analysis |
| `/states` | GET | List Indian states |

## Deployment (Railway)

1. Push code to GitHub
2. Create new project on Railway.app
3. Connect GitHub repository
4. Set environment variables if needed
5. Deploy

The frontend is served from `/app` route on the same server.

## Notes

- The app requires the backend to be running for full functionality
- Some features (AQI data) require internet connection
- Demo user is pre-created on first backend startup