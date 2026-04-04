from __future__ import annotations

from datetime import datetime, UTC
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator, ConfigDict
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..ml.xgb_model import (
    build_features,
    confidence_label,
    get_model_metadata,
    predict_from_features,
    recommendations_for,
)
from ..models.models import HealthAnalysis, Period, Symptom, User
from ..services.india_context import (
    get_aqi_enrichment,
    get_diet_recommendations,
    get_gender_bias_awareness,
    get_government_schemes,
    get_lab_cost_estimates,
)

router = APIRouter(prefix="/analysis", tags=["Analysis"])


class AnalysisRequest(BaseModel):
    description: str = Field(min_length=3, max_length=2000)
    fatigue_level: Optional[int] = Field(default=None, ge=1, le=10)
    sleep_quality: Optional[int] = Field(default=None, ge=1, le=10)
    mood: Optional[str] = Field(default=None, max_length=50)

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("description cannot be empty")
        return cleaned


class AnalysisResponse(BaseModel):
    risk_type: str
    confidence_score: float
    confidence_label: str
    probabilities: Dict[str, float]
    baseline_deviation: str
    india_context: str
    recommendations: List[str]
    diet_recommendations: List[str]
    aqi_enrichment: "AQIEnrichment"
    government_schemes: List[str]
    lab_test_cost_estimates: List["LabTestCostEstimate"]
    bias_awareness: str
    model_metrics: Dict[str, float]
    medical_disclaimer: str


class AQIEnrichment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    city: str
    aqi_value: Optional[int]
    aqi_category: str
    pm2_5: Optional[float] = None
    source: str
    advisory: Optional[str] = None


class LabTestCostEstimate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    test: str
    estimated_low_inr: int
    estimated_high_inr: int
    city: str


def _cycle_stats(periods: List[Period]) -> tuple[float, float]:
    if len(periods) < 2:
        return 28.0, 0.0
    ordered = sorted(periods, key=lambda period: period.start_date, reverse=True)
    cycle_lengths = []
    for index in range(len(ordered) - 1):
        gap = (ordered[index].start_date - ordered[index + 1].start_date).days
        if 20 <= gap <= 45:
            cycle_lengths.append(gap)
    if not cycle_lengths:
        return 28.0, 0.0
    avg_cycle = sum(cycle_lengths) / len(cycle_lengths)
    variation = (
        max(cycle_lengths) - min(cycle_lengths) if len(cycle_lengths) > 1 else 0.0
    )
    return float(avg_cycle), float(variation)


def _recent_history(symptoms: List[Symptom]) -> tuple[float, float]:
    relevant = [
        symptom
        for symptom in symptoms
        if symptom.fatigue_level is not None and symptom.sleep_quality is not None
    ]
    if not relevant:
        return 5.0, 5.0
    recent = relevant[:5]
    fatigue_avg = sum(float(item.fatigue_level) for item in recent) / len(recent)
    sleep_avg = sum(float(item.sleep_quality) for item in recent) / len(recent)
    return fatigue_avg, sleep_avg


def _baseline_deviation(
    current_fatigue: Optional[int],
    current_sleep: Optional[int],
    fatigue_avg: float,
    sleep_avg: float,
) -> str:
    parts = []
    if current_fatigue is not None:
        delta = float(current_fatigue) - fatigue_avg
        if abs(delta) >= 1.0:
            parts.append(
                f"fatigue is {abs(delta):.1f} points {'above' if delta > 0 else 'below'} your recent baseline"
            )
    if current_sleep is not None:
        delta = float(current_sleep) - sleep_avg
        if abs(delta) >= 1.0:
            parts.append(
                f"sleep quality is {abs(delta):.1f} points {'above' if delta > 0 else 'below'} your recent baseline"
            )
    if not parts:
        return "current symptoms are close to your recent baseline"
    return "; ".join(parts)


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_symptoms(
    payload: AnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    periods = (
        db.query(Period)
        .filter(Period.user_id == current_user.id)
        .order_by(Period.start_date.desc())
        .all()
    )
    symptoms = (
        db.query(Symptom)
        .filter(Symptom.user_id == current_user.id)
        .order_by(Symptom.date.desc())
        .all()
    )
    avg_cycle_length, cycle_variation = _cycle_stats(periods)
    recent_fatigue_avg, recent_sleep_avg = _recent_history(symptoms)

    features = build_features(
        description=payload.description,
        fatigue_level=payload.fatigue_level,
        sleep_quality=payload.sleep_quality,
        age=current_user.age,
        avg_cycle_length=avg_cycle_length,
        cycle_variation=cycle_variation,
        recent_fatigue_avg=recent_fatigue_avg,
        recent_sleep_avg=recent_sleep_avg,
    )
    prediction = predict_from_features(features)
    risk_type = str(prediction["risk_type"])
    confidence_score = float(prediction["confidence_score"])
    baseline_text = _baseline_deviation(
        payload.fatigue_level,
        payload.sleep_quality,
        recent_fatigue_avg,
        recent_sleep_avg,
    )
    recommendations = recommendations_for(risk_type, current_user.state)
    diet_recommendations = get_diet_recommendations(current_user.state, risk_type)
    aqi_enrichment = get_aqi_enrichment(current_user.state)
    government_schemes = get_government_schemes(current_user.state)
    lab_test_cost_estimates = get_lab_cost_estimates(risk_type, current_user.state)
    bias_awareness = get_gender_bias_awareness(risk_type)
    model_metrics = get_model_metadata()
    medical_disclaimer = (
        "This is not a diagnosis. Please consult a doctor for confirmation."
    )

    if risk_type == "iron_deficiency_anemia":
        risk_context = "Low iron intake is common in many Indian diets. Monitor food intake and consider iron-rich meals."
    elif risk_type == "pcos":
        risk_context = "Cycle irregularity is easier to miss without regular tracking; continued logging helps spot patterns."
    elif risk_type == "thyroid_disorder":
        risk_context = "Persistent fatigue and hair loss can overlap with stress; structured tracking helps refine the signal."
    elif risk_type == "vitamin_d_deficiency":
        risk_context = "Indoor routines and low sunlight exposure can contribute to vitamin D concerns."
    elif risk_type == "diabetes_risk":
        risk_context = "Thirst and frequent urination patterns should be checked with basic glucose screening."
    else:
        risk_context = (
            "No strong abnormal pattern was detected from the current symptom profile."
        )

    india_context = (
        f"{risk_context} "
        f"AQI for {aqi_enrichment['city']}: {aqi_enrichment['aqi_value']} ({aqi_enrichment['aqi_category']})."
    )
    if aqi_enrichment.get("advisory"):
        india_context = f"{india_context} {aqi_enrichment['advisory']}"

    analysis_record = HealthAnalysis(
        user_id=current_user.id,
        date=datetime.now(UTC),
        risk_type=risk_type,
        confidence_score=confidence_score,
        baseline_deviation=baseline_text,
        india_context=india_context,
        recommendations=" | ".join(recommendations + diet_recommendations),
    )
    db.add(analysis_record)
    db.commit()
    db.refresh(analysis_record)

    return AnalysisResponse(
        risk_type=risk_type,
        confidence_score=confidence_score,
        confidence_label=confidence_label(confidence_score),
        probabilities=prediction["probabilities"],
        baseline_deviation=baseline_text,
        india_context=india_context,
        recommendations=recommendations,
        diet_recommendations=diet_recommendations,
        aqi_enrichment=aqi_enrichment,
        government_schemes=government_schemes,
        lab_test_cost_estimates=lab_test_cost_estimates,
        bias_awareness=bias_awareness,
        model_metrics=model_metrics,
        medical_disclaimer=medical_disclaimer,
    )


@router.get("/history")
def get_analysis_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analyses = (
        db.query(HealthAnalysis)
        .filter(HealthAnalysis.user_id == current_user.id)
        .order_by(HealthAnalysis.date.desc())
        .all()
    )
    return [
        {
            "id": item.id,
            "date": item.date,
            "risk_type": item.risk_type,
            "confidence_score": item.confidence_score,
            "baseline_deviation": item.baseline_deviation,
            "india_context": item.india_context,
            "recommendations": item.recommendations,
        }
        for item in analyses
    ]
