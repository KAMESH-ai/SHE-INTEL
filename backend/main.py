"""
SHE-INTEL INDIA - FastAPI Backend
Health Risk Prediction API using ML Model
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="SHE-INTEL INDIA API",
    description="Context-Aware Health Intelligence for Indian Women",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import ML components
from ml_analyzer import (
    HealthRiskModel,
    get_india_context,
    get_gender_bias,
    get_recommended_actions,
)
from aqi_service import get_aqi
from database import get_db, init_db
from models import UserCreate, UserResponse, Token, PeriodCreate, PeriodResponse
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
import translations
from translations import TRANSLATIONS
from fastapi.security import HTTPBearer

# Initialize ML model
model = None


@app.on_event("startup")
async def load_model():
    global model
    print("Loading ML model...")
    model = HealthRiskModel()
    if not model.is_trained:
        model.train()
    print("Model loaded successfully!")
    init_db()
    print("Database initialized!")

    # Create demo user
    from database import get_db
    from auth import get_password_hash

    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?", ("demo@sheintel.in",)
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
                ("demo@sheintel.in", get_password_hash("demo123"), "Demo User"),
            )
            print("Demo user created: demo@sheintel.in / demo123")


# Request models
class HealthAnalysisRequest(BaseModel):
    age: Optional[str] = None
    state: str
    symptoms: str
    period_start: Optional[str] = None
    period_end: Optional[str] = None


class HealthAnalysisResponse(BaseModel):
    success: bool
    predictions: List[dict]
    top_risk: Optional[dict]
    symptoms_detected: List[str]
    india_context: dict
    gender_bias: dict
    recommended_actions: List[str]
    aqi: dict
    community_data: dict
    lab_tests: dict
    government_schemes: List[str]
    analysis_summary: str


@app.get("/")
async def root():
    return {
        "name": "SHE-INTEL INDIA API",
        "version": "1.0.0",
        "description": "Context-Aware Health Intelligence for Indian Women",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None if model else False}


@app.get("/app")
async def serve_app():
    frontend_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "index.html"
    )
    return FileResponse(frontend_path)


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    frontend_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "index.html"
    )
    return FileResponse(frontend_path)


@app.post("/analyze", response_model=HealthAnalysisResponse)
async def analyze_health(request: HealthAnalysisRequest):
    global model
    if model is None:
        from ml_analyzer import HealthRiskModel

        model = HealthRiskModel()
        if not model.is_trained:
            model.train()

    try:
        result = model.predict(
            symptoms_text=request.symptoms, state=request.state, age=request.age
        )

        if "error" in result:
            return HealthAnalysisResponse(
                success=False,
                predictions=[],
                top_risk=None,
                symptoms_detected=[],
                india_context={},
                gender_bias={},
                recommended_actions=[],
                analysis_summary=result["error"],
            )

        india_context = get_india_context(request.state)
        aqi_data = get_aqi(request.state)
        gender_bias = {}
        if result["top_risk"]:
            gender_bias = get_gender_bias(result["top_risk"]["condition"])

        if result["top_risk"]:
            recommended_actions = get_recommended_actions(
                result["top_risk"]["condition"]
            )
        else:
            recommended_actions = get_recommended_actions("normal")

        community_data = {
            "state": request.state,
            "prevalence": india_context.get("community_prevalence", 45),
        }
        lab_tests = india_context.get("test_cost", {})
        government_schemes = india_context.get("govt_schemes", [])

        if result["top_risk"]:
            top = result["top_risk"]
            summary = f"Based on your symptoms in {request.state}, there is a {top['confidence']}% probability of {top['condition']}."
            if top["confidence"] > 60:
                summary += (
                    " We recommend consulting a healthcare provider for proper testing."
                )
            elif top["confidence"] > 40:
                summary += " Consider discussing this with your doctor."
        else:
            summary = "No significant health risks identified based on your symptoms."

        return HealthAnalysisResponse(
            success=True,
            predictions=result["predictions"],
            top_risk=result["top_risk"],
            symptoms_detected=result["symptoms_detected"],
            india_context=india_context,
            gender_bias=gender_bias,
            recommended_actions=recommended_actions,
            aqi=aqi_data,
            community_data=community_data,
            lab_tests=lab_tests,
            government_schemes=government_schemes,
            analysis_summary=summary,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/states")
async def get_states():
    return [
        "Andhra Pradesh",
        "Arunachal Pradesh",
        "Assam",
        "Bihar",
        "Chhattisgarh",
        "Goa",
        "Gujarat",
        "Haryana",
        "Himachal Pradesh",
        "Jharkhand",
        "Karnataka",
        "Kerala",
        "Madhya Pradesh",
        "Maharashtra",
        "Manipur",
        "Meghalaya",
        "Mizoram",
        "Nagaland",
        "Odisha",
        "Punjab",
        "Rajasthan",
        "Sikkim",
        "Tamil Nadu",
        "Telangana",
        "Tripura",
        "Uttar Pradesh",
        "Uttarakhand",
        "West Bengal",
        "Delhi",
    ]


@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?", (user.email,)
        ).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        password_hash = get_password_hash(user.password)
        cursor = conn.execute(
            "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
            (user.email, password_hash, user.name),
        )
        user_id = cursor.lastrowid

    return {"id": user_id, "email": user.email, "name": user.name}


@app.post("/auth/login", response_model=Token)
async def login(email: str, password: str):
    with get_db() as conn:
        user = conn.execute(
            "SELECT id, email, password_hash, name FROM users WHERE email = ?", (email,)
        ).fetchone()

    if not user or not verify_password(password, user[2]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user[0], "email": user[1]})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        user = conn.execute(
            "SELECT id, email, name FROM users WHERE id = ?", (current_user["user_id"],)
        ).fetchone()
    return {"id": user[0], "email": user[1], "name": user[2]}


@app.get("/periods", response_model=List[PeriodResponse])
async def get_periods(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        periods = conn.execute(
            "SELECT id, start_date, end_date, flow_level, symptoms FROM periods WHERE user_id = ? ORDER BY start_date DESC",
            (current_user["user_id"],),
        ).fetchall()
    return [
        {
            "id": p[0],
            "start_date": p[1],
            "end_date": p[2],
            "flow_level": p[3],
            "symptoms": p[4],
        }
        for p in periods
    ]


@app.post("/periods", response_model=PeriodResponse)
async def create_period(
    period: PeriodCreate, current_user: dict = Depends(get_current_user)
):
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO periods (user_id, start_date, end_date, flow_level, symptoms) VALUES (?, ?, ?, ?, ?)",
            (
                current_user["user_id"],
                period.start_date,
                period.end_date,
                period.flow_level,
                period.symptoms,
            ),
        )
        period_id = cursor.lastrowid
    return {"id": period_id, **period.dict()}


@app.get("/periods/prediction")
async def get_prediction(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        periods = conn.execute(
            "SELECT start_date FROM periods WHERE user_id = ? ORDER BY start_date DESC LIMIT 6",
            (current_user["user_id"],),
        ).fetchall()

    if len(periods) < 3:
        return {
            "message": "Need at least 3 periods to predict",
            "next_period": None,
            "ovulation_window": None,
        }

    dates = [p[0] for p in periods]
    cycles = []
    for i in range(len(dates) - 1):
        from datetime import datetime

        d1 = datetime.strptime(dates[i], "%Y-%m-%d")
        d2 = datetime.strptime(dates[i + 1], "%Y-%m-%d")
        cycles.append((d1 - d2).days)

    avg_cycle = sum(cycles) / len(cycles)
    last_period = datetime.strptime(dates[0], "%Y-%m-%d")
    next_period = last_period.replace(day=last_period.day + int(avg_cycle))
    ovulation = next_period.replace(day=next_period.day - 14)

    return {
        "avg_cycle_length": round(avg_cycle),
        "next_period": next_period.strftime("%Y-%m-%d"),
        "ovulation_window": f"{ovulation.strftime('%Y-%m-%d')} - {(ovulation.replace(day=ovulation.day + 2)).strftime('%Y-%m-%d')}",
    }


@app.get("/translations/{lang}")
async def get_translations(lang: str):
    if lang in TRANSLATIONS:
        return TRANSLATIONS[lang]
    return TRANSLATIONS.get("en", {})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
