# SHE-INTEL INDIA - Complete Technical Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Tech Stack](#tech-stack)
4. [How the Tech Stack Works Together](#how-the-tech-stack-works-together)
5. [How NLP Works Here](#how-nlp-works-here)
6. [How ML Model Works](#how-ml-model-works)
7. [Database Schema](#database-schema)
8. [API Endpoints](#api-endpoints)
9. [ML Model Details](#ml-model-details)
10. [India Context Features](#india-context-features)
11. [Frontend Features](#frontend-features)
12. [Testing](#testing)
13. [Deployment](#deployment)

---

## 1. Project Overview

**SHE-INTEL INDIA** is a context-aware predictive health intelligence application designed for Indian women. The app helps users track their menstrual cycles, log symptoms, and receive AI-powered health risk assessments.

### Key Capabilities
- User authentication (register/login)
- Period tracking with cycle prediction
- Symptom logging (fatigue, sleep quality, mood)
- ML-based health risk analysis
- India-specific context (diet, AQI, government schemes, lab costs)
- Dark/Light theme toggle

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Static)                        │
│                    HTML + CSS + JavaScript                      │
│                   http://localhost:5173                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP Requests (JSON)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI)                         │
│                    http://localhost:8002                        │
├─────────────────────────────────────────────────────────────────┤
│  Routes:                                                        │
│  ├── /auth/*    - Authentication                                │
│  ├── /periods/* - Period tracking                              │
│  ├── /symptoms/* - Symptom logging                             │
│  └── /analysis/* - Health analysis + ML                         │
├─────────────────────────────────────────────────────────────────┤
│  Services:                                                     │
│  ├── ML Model (XGBoost) - Risk prediction                      │
│  └── India Context - Diet, AQI, schemes, costs                 │
├─────────────────────────────────────────────────────────────────┤
│  Database: SQLite                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | Web framework for building APIs |
| **SQLAlchemy** | ORM for database operations |
| **SQLite** | Lightweight database |
| **Pydantic** | Data validation |
| **Python-JOSE** | JWT token generation |
| **Passlib** | Password hashing |

### Machine Learning
| Technology | Purpose |
|------------|---------|
| **XGBoost** | Gradient boosting classifier |
| **Scikit-learn** | Feature extraction, metrics |
| **NumPy** | Numerical operations |
| **Joblib** | Model serialization |

### Frontend
| Technology | Purpose |
|------------|---------|
| **Vanilla HTML5** | Structure |
| **Vanilla CSS3** | Styling with CSS variables |
| **Vanilla JavaScript** | Client-side logic |

### Testing
| Technology | Purpose |
|------------|---------|
| **Pytest** | Unit testing |
| **FastAPI TestClient** | API testing |

---

## 4. How the Tech Stack Works Together

```
User Action (Frontend)
       │
       ▼
HTML Form Submit → JavaScript (app.js)
       │
       ▼
Fetch API → HTTP Request (JSON)
       │
       ▼
FastAPI (Backend)
       │
       ├─▶ Routes (auth/periods/symptoms/analysis)
       │
       ├─▶ SQLAlchemy → SQLite Database
       │
       └─▶ ML Model (XGBoost) → Risk Prediction
       │
       ▼
Response (JSON)
       │
       ▼
Frontend Updates DOM
```

### Tech Stack Purpose Details

#### **FastAPI** (Backend Framework)
```python
# app/main.py
from fastapi import FastAPI

app = FastAPI(title="SHE-INTEL INDIA")

@app.get("/")
def root():
    return {"message": "SHE-INTEL INDIA API"}

app.include_router(auth.router)
app.include_router(periods.router)
app.include_router(symptoms.router)
app.include_router(analysis.router)
```
**Purpose**: Creates the web server, handles routes, processes requests

---

#### **SQLAlchemy** (Database ORM)
```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///./she_intel.db")
SessionLocal = sessionmaker(bind=engine)

# app/models/models.py
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    name = Column(String)
    # ... relationships to Period, Symptom
```
**Purpose**: Python code to interact with database instead of raw SQL

---

#### **JWT (JSON Web Tokens)** (Authentication)
```python
# app/auth.py
from jose import jwt

SECRET_KEY = "secret-key"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# Token contains: {"sub": "user@email.com", "exp": 1234567890}
```
**Purpose**: Securely identify users without storing sessions

---

#### **XGBoost** (Machine Learning)
```python
# app/ml/xgb_model.py
from xgboost import XGBClassifier

model = XGBClassifier(
    n_estimators=180,
    max_depth=4,
    learning_rate=0.08
)
model.fit(X_train, y_train)
prediction = model.predict_proba(X_new)
```
**Purpose**: Gradient boosting classifier for disease prediction

---

## 5. How NLP Works Here

### Step 1: User Input (Text)
```
User enters: "Feeling very tired with dizziness and pale skin"
```

### Step 2: Keyword Extraction
```python
# app/ml/xgb_model.py

KEYWORDS = {
    "iron_deficiency_anemia": ["fatigue", "dizzy", "dizziness", "weak", "pale", "heavy bleeding"],
    "pcos": ["irregular period", "acne", "weight gain"],
    "thyroid_disorder": ["hair loss", "cold", "constipation"],
    # ...
}

def _count_keywords(text, keywords):
    text = text.lower()
    return sum(1 for keyword in keywords if keyword in text)

# Example: "Feeling very tired with dizziness and pale skin"
# iron_deficiency_anemia keywords found: 3 (tired/dizzy/pale)
```

### Step 3: Feature Vector Creation
```python
# app/ml/xgb_model.py

def build_features(description, fatigue_level, sleep_quality, age, ...):
    return {
        "fatigue_level": 7,
        "sleep_quality": 4,
        "age": 28,
        "iron_kw": 3,      # ← Keyword count
        "pcos_kw": 0,
        "thyroid_kw": 0,
        # ... 25 features total
    }
```

### Visual: NLP Feature Extraction
```
Input Text: "Feeling dizzy, pale, and very tired with heavy bleeding"

┌─────────────────────────────────────────────────────┐
│                   TEXT PROCESSING                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  "Feeling dizzy, pale, and very tired..."          │
│         │        │      │        │                  │
│         ▼        ▼      ▼        ▼                  │
│    ┌─────────┬──────┬────────┬──────────────┐    │
│    │  dizzy  │ pale │ tired  │ heavy bleeding│    │
│    │    ✓    │  ✓   │   ✓    │      ✓        │    │
│    └─────────┴──────┴────────┴──────────────┘    │
│         │        │      │        │                  │
│         ▼        ▼      ▼        ▼                  │
│    iron_kw = 4  (count of matching keywords)       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 6. How ML Model Works

### Training Phase (Done at startup)
```python
# app/ml/xgb_model.py

# 1. Create synthetic training data
TRAINING_DATA = {
    "iron_deficiency_anemia": [
        {"fatigue_level": 9, "sleep_quality": 4, "iron_kw": 3, "dizziness_kw": 1},
        # ... 35 samples per disease
    ],
    "pcos": [...],
    # ... 6 categories
}

# 2. Train XGBoost model
model = XGBClassifier(n_estimators=180, max_depth=4)
model.fit(X_train, y_train)

# 3. Save model to disk
joblib.dump(model, "xgb_model.joblib")
```

### Prediction Phase (On User Request)
```python
# When user submits symptoms for analysis

# 1. Build feature vector from user input
features = build_features(
    description="Feeling dizzy with pale skin",
    fatigue_level=8,
    sleep_quality=4,
    age=25,
    avg_cycle_length=28,
    cycle_variation=3,
    recent_fatigue_avg=5,
    recent_sleep_avg=6
)

# 2. Get prediction from ML model
result = model.predict_proba([features])

# Result: [0.85, 0.05, 0.03, 0.02, 0.01, 0.04]
#          ↑
#          85% probability of iron_deficiency_anemia
```

### Visual: ML Prediction Flow

```
┌────────────────────────────────────────────────────────────────┐
│                    ML PREDICTION PIPELINE                     │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  USER INPUT                                                    │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ description: "Feeling dizzy with pale skin"            │ │
│  │ fatigue_level: 8                                        │ │
│  │ sleep_quality: 4                                        │ │
│  │ age: 28                                                 │ │
│  └──────────────────────────────────────────────────────────┘ │
│                          │                                      │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ FEATURE EXTRACTION                                        │ │
│  │ • fatigue_level: 8                                       │ │
│  │ • sleep_quality: 4                                       │ │
│  │ • iron_kw: 3 (keywords found in text)                   │ │
│  │ • pcos_kw: 0                                             │ │
│  │ • thyroid_kw: 0                                          │ │
│  │ • ... (25 features total)                                │ │
│  └──────────────────────────────────────────────────────────┘ │
│                          │                                      │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ XGBOOST MODEL (xgb_model.joblib)                         │ │
│  │                                                          │ │
│  │   Input: [8, 4, 28, 3, 3, 0, 0, 0, 3, ...]             │ │
│  │       │                                                  │ │
│  │       ▼                                                  │ │
│  │   ┌─────────────────────────────────────┐                │ │
│  │   │   Decision Tree Ensemble            │                │ │
│  │   │   (180 trees, max_depth=4)         │                │ │
│  │   └─────────────────────────────────────┘                │ │
│  │       │                                                  │ │
│  │       ▼                                                  │ │
│  │   Output: [0.85, 0.05, 0.03, 0.02, 0.01, 0.04]         │ │
│  └──────────────────────────────────────────────────────────┘ │
│                          │                                      │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ RESULT                                                     │ │
│  │ • Risk: iron_deficiency_anemia                            │ │
│  │ • Confidence: 85% (HIGH)                                   │ │
│  │ • Recommendations: [CBC test, iron-rich foods]          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### Complete Request-Response Example

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USER INPUT (Frontend)                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Form Data:                                                      │
│ • description: "Feeling dizzy, pale, tired with heavy flow"   │
│ • fatigue_level: 8                                              │
│ • sleep_quality: 3                                             │
│                                                                 │
│ POST /analysis/analyze                                          │
│ Authorization: Bearer <jwt_token>                               │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. BACKEND PROCESSING                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ a) Validate token (JWT)                                        │
│    └─► Get user ID from token                                  │
│                                                                 │
│ b) Fetch user history from DB                                  │
│    └─► Get last 5 periods                                      │
│    └─► Get last 5 symptoms                                     │
│                                                                 │
│ c) Calculate features                                          │
│    • avg_cycle_length: 28 days                                 │
│    • cycle_variation: 2 days                                   │
│    • recent_fatigue_avg: 6.5                                    │
│    • recent_sleep_avg: 5.2                                     │
│                                                                 │
│ d) Run ML prediction                                           │
│    └─► Build feature vector                                    │
│    └─► Call XGBoost model                                      │
│    └─► Get probabilities: [0.85, 0.08, 0.03, 0.02, 0.01, 0.01]│
│                                                                 │
│ e) Get India context                                           │
│    └─► Get state (Tamil Nadu)                                   │
│    └─► Get diet recommendations                                │
│    └─► Get AQI data                                            │
│    └─► Get government schemes                                   │
│                                                                 │
│ f) Save analysis to database                                   │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. RESPONSE (Frontend)                                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ {                                                              │
│   "risk_type": "iron_deficiency_anemia",                      │
│   "confidence_score": 0.85,                                   │
│   "confidence_label": "high",                                 │
│   "recommendations": [                                         │
│     "Consider CBC and ferritin tests.",                        │
│     "Include iron-rich foods: ragi, lentils, spinach"        │
│   ],                                                            │
│   "india_context": "Low iron intake is common...",            │
│   "diet_recommendations": ["Prioritize iron-rich meals..."],   │
│   "aqi_enrichment": {"city": "Chennai", "aqi_value": 85},     │
│   "government_schemes": ["Pradhan Mantri Matru..."],           │
│   "medical_disclaimer": "This is not a diagnosis..."           │
│ }                                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Files & Their Purpose

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app setup, CORS, route registration |
| `app/auth.py` | JWT token creation/verification, password hashing |
| `app/database.py` | SQLAlchemy engine, session, base |
| `app/models/models.py` | User, Period, Symptom, HealthAnalysis tables |
| `app/routers/auth.py` | /auth/register, /auth/login, /auth/me |
| `app/routers/periods.py` | Period CRUD, calendar with prediction |
| `app/routers/symptoms.py` | Symptom CRUD with validation |
| `app/routers/analysis.py` | ML analysis endpoint |
| `app/ml/xgb_model.py` | ML model, features, prediction |
| `app/services/india_context.py` | Diet, AQI, schemes, costs |
| `frontend/app.js` | API calls, UI updates, theme toggle |
| `frontend/styles.css` | All styling with CSS variables |

---

## 7. Database Schema

### Users Table
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String)
    age = Column(Integer)
    state = Column(String)  # Indian state for context
    created_at = Column(DateTime)
    
    # Relationships
    periods = relationship("Period", back_populates="user")
    symptoms = relationship("Symptom", back_populates="user")
    analyses = relationship("HealthAnalysis", back_populates="user")
```

### Periods Table
```python
class Period(Base):
    __tablename__ = "periods"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    flow_level = Column(String)  # Light, Medium, Heavy
    symptoms = Column(Text, nullable=True)
    created_at = Column(DateTime)
```

### Symptoms Table
```python
class Symptom(Base):
    __tablename__ = "symptoms"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime)
    description = Column(Text)
    fatigue_level = Column(Integer)  # 1-10
    sleep_quality = Column(Integer)  # 1-10
    mood = Column(String, nullable=True)
    created_at = Column(DateTime)
```

### Health Analysis Table
```python
class HealthAnalysis(Base):
    __tablename__ = "health_analyses"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime)
    risk_type = Column(String)  # Predicted condition
    confidence_score = Column(Float)
    baseline_deviation = Column(Text)
    india_context = Column(Text)
    recommendations = Column(Text)
```

---

## 8. API Endpoints

### Authentication (`/auth`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register new user |
| `/auth/login` | POST | Login, get JWT token |
| `/auth/me` | GET | Get current user info |

### Periods (`/periods`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/periods/` | POST | Log new period |
| `/periods/` | GET | List all periods |
| `/periods/calendar` | GET | Get calendar with prediction |

### Symptoms (`/symptoms`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/symptoms/` | POST | Log new symptom |
| `/symptoms/` | GET | List symptoms (limit 365) |

### Analysis (`/analysis`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analysis/analyze` | POST | Get ML health analysis |
| `/analysis/history` | GET | Get analysis history |

---

## 9. ML Model Details

### Model Architecture

**XGBoost Classifier** with the following configuration:
```python
XGBClassifier(
    objective="multi:softprob",
    num_class=6,  # 6 disease categories
    n_estimators=180,
    max_depth=4,
    learning_rate=0.08,
    subsample=0.9,
    colsample_bytree=0.9,
    reg_lambda=1.0,
    tree_method="hist"
)
```

### Disease Categories
1. **iron_deficiency_anemia**
2. **pcos** (Polycystic Ovary Syndrome)
3. **thyroid_disorder**
4. **vitamin_d_deficiency**
5. **diabetes_risk**
6. **normal**

### Feature Engineering

The model uses **25 features** extracted from user input:

| Feature Type | Features |
|--------------|----------|
| **Numeric** | fatigue_level, sleep_quality, age, avg_cycle_length, cycle_variation |
| **Derived** | fatigue_delta, sleep_delta, text_length |
| **Keyword Counts** | iron_kw, pcos_kw, thyroid_kw, vitamin_d_kw, diabetes_kw, normal_kw |
| **Specific Indicators** | dizziness_kw, bleeding_kw, acne_kw, hair_loss_kw, weight_gain_kw, cold_kw, constipation_kw, thirst_kw, urination_kw, bone_pain_kw, muscle_pain_kw |

### Keyword Detection

```python
KEYWORDS = {
    "iron_deficiency_anemia": ["fatigue", "dizzy", "dizziness", "weak", "pale", "heavy bleeding", "craving", "shortness of breath"],
    "pcos": ["irregular period", "irregular cycle", "acne", "weight gain", "excess hair", "hair growth", "missed period"],
    "thyroid_disorder": ["hair loss", "cold", "constipation", "weight gain", "fatigue", "slow", "swelling"],
    "vitamin_d_deficiency": ["bone pain", "muscle pain", "joint pain", "low sunlight", "sunlight", "tired", "weak bones"],
    "diabetes_risk": ["thirst", "frequent urination", "urination", "hunger", "blurred vision", "weight loss", "sugar"],
    "normal": ["regular cycle", "normal", "fine", "ok", "good sleep", "no issues", "healthy"],
}
```

### Training Data

- **210 samples** (35 per category × 6 categories)
- Synthetic training data generated from templates
- 80/20 train-test split
- **Model metrics**: Accuracy ~100%, Macro F1 ~100%

### Prediction Output

```python
{
    "risk_type": "pcos",              # Predicted disease
    "confidence_score": 0.87,         # 0-1 probability
    "confidence_label": "high",       # high/medium/low
    "probabilities": {                 # All class probabilities
        "iron_deficiency_anemia": 0.02,
        "pcos": 0.87,
        "thyroid_disorder": 0.05,
        ...
    }
}
```

### Confidence Thresholds
- **High**: ≥ 0.85 confidence
- **Medium**: 0.65 - 0.84 confidence
- **Low**: < 0.65 confidence

---

## 10. India Context Features

### State-Based Diet Recommendations
- Different states have different dietary recommendations
- Iron-rich foods for anemia
- Balanced diet for PCOS
- Consistent meals for thyroid

### AQI Enrichment
- Fetches real-time AQI from Open-Meteo API
- Falls back to estimated values if API unavailable
- Cached for 30 minutes

### Government Schemes
- National schemes applicable to all Indian women
- State-specific schemes based on user's state

### Lab Cost Estimates
- Test costs vary by state (city factor)
- Base costs defined per disease category

### Gender Bias Awareness
- Contextual notes about healthcare biases
- Specific to each predicted condition

---

## 11. Frontend Features

### Pages
1. **Login Page** - Email/password authentication
2. **Register Page** - Create account with name, email, password, age, state
3. **Dashboard** - Main view with:
   - Overview (cycle status, symptom count, calendar)
   - Periods (log periods, view history)
   - Symptoms (log symptoms, view history)
   - Analyze (ML-powered health analysis)
   - History (past analysis results)

### UI Features
- Dark/Light theme toggle (persists in localStorage)
- Toast notifications for user feedback
- Character counters for textareas
- Skeleton loaders while data loads
- Responsive design (mobile-friendly)
- Accessibility: ARIA labels, keyboard navigation

### API Communication
- JWT token stored in localStorage
- All API calls include Authorization header
- Error handling with user-friendly messages

---

## 12. Testing

### Backend Tests (8 tests)

```python
# Tests cover:
1. Analysis response includes model metrics and india_context
2. AQI fallback is cached for repeated requests
3. Model artifact is persisted and loaded
4. API smoke for history and auth guards
5. Auth: register, login, /me endpoints
6. Periods: create, list, calendar, invalid dates
7. Symptoms: create, list, limit, auth guard
8. Auth: missing token and bad payload
```

### Run Tests
```bash
cd backend
pytest tests/ -v
```

---

## 13. Deployment

### Backend (Render/Vercel/AWS)
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Frontend (Netlify/Vercel/GitHub Pages)
```bash
# Serve static files
npx serve -l 5173
# Or
python -m http.server 5173
```

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | sqlite:///./she_intel.db | Database path |
| `XGB_MODEL_ARTIFACT_PATH` | app/ml/artifacts/xgb_model.joblib | ML model path |

---

## Project File Structure

```
she-intel-india/
├── PROJECT_DETAILS.md       # This file
├── README.md               # Quick start guide
├── requirements.txt        # Python dependencies
├── run_all.sh             # Start both servers
├── stop_all.sh            # Stop servers
├── render.yaml            # Render deployment config
│
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI app entry point
│   │   ├── auth.py         # JWT authentication
│   │   ├── database.py     # SQLAlchemy setup
│   │   ├── models/
│   │   │   └── models.py   # Database models
│   │   ├── routers/
│   │   │   ├── auth.py     # Auth endpoints
│   │   │   ├── periods.py  # Period endpoints
│   │   │   ├── symptoms.py # Symptom endpoints
│   │   │   └── analysis.py # Analysis endpoints
│   │   ├── ml/
│   │   │   ├── xgb_model.py    # ML model code
│   │   │   └── artifacts/
│   │   │       └── xgb_model.joblib
│   │   └── services/
│   │       ├── india_context.py      # India-specific features
│   │       └── india_context_data.json # State data
│   ├── tests/
│   │   └── test_backend.py  # Pytest tests
│   └── scripts/
│       └── seed_demo_data.py # Demo data seeder
│
└── frontend/
    ├── index.html          # Main HTML
    ├── app.js             # Frontend logic
    └── styles.css         # Styling
```

---

## Summary

SHE-INTEL INDIA is a complete full-stack health intelligence application with:
- ✅ User authentication (register/login/JWT)
- ✅ Period & symptom tracking
- ✅ ML-powered risk prediction (XGBoost) with NLP keyword extraction
- ✅ India-specific context (diet, AQI, schemes, costs)
- ✅ Responsive frontend with dark/light mode
- ✅ Comprehensive testing
- ✅ Ready for deployment