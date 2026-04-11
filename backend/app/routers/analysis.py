from __future__ import annotations

from datetime import datetime, timedelta, UTC
from statistics import median
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator, ConfigDict
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..ml.xgb_model import (
    build_features,
    confidence_label,
    predict_from_features,
    recommendations_for,
)
from ..models.models import HealthAnalysis, Period, Symptom, User
from ..services.india_context import (
    get_aqi_enrichment,
    get_diet_recommendations,
    get_gender_bias_awareness,
    get_government_schemes,
)

router = APIRouter(prefix="/analysis", tags=["Analysis"])

CONDITION_SYMPTOMS: Dict[str, List[str]] = {
    "Iron Deficiency Anemia": [
        "fatigue",
        "dizziness",
        "weakness",
        "pale",
        "heavy bleeding",
        "shortness of breath",
    ],
    "PCOS": [
        "irregular period",
        "missed period",
        "acne",
        "weight gain",
        "excess hair",
    ],
    "Thyroid Disorder": [
        "hair loss",
        "fatigue",
        "weight gain",
        "cold intolerance",
        "constipation",
    ],
    "Vitamin D Deficiency": [
        "bone pain",
        "muscle pain",
        "joint pain",
        "weakness",
    ],
    "Diabetes Risk": [
        "thirst",
        "frequent urination",
        "hunger",
        "blurred vision",
        "weight loss",
    ],
}


def _normalize_text(text: str) -> str:
    return (text or "").lower().strip()


def _compute_condition_scores(
    description: str,
    fatigue_level: Optional[int],
    cycle_context: Dict[str, float | int | str | bool | None],
) -> tuple[Dict[str, float], Dict[str, List[str]]]:
    text = _normalize_text(description)
    matched: Dict[str, List[str]] = {}
    scores: Dict[str, float] = {}

    for condition, symptoms in CONDITION_SYMPTOMS.items():
        condition_matches = [symptom for symptom in symptoms if symptom in text]
        matched[condition] = condition_matches
        base_score = len(condition_matches) / len(symptoms)
        scores[condition] = base_score

    if fatigue_level is not None and fatigue_level >= 7:
        scores["Iron Deficiency Anemia"] += 0.08
        scores["Thyroid Disorder"] += 0.08

    if bool(cycle_context.get("irregular_cycle")):
        scores["PCOS"] += 0.1

    if "thirst" in text and "frequent urination" in text:
        scores["Diabetes Risk"] += 0.1

    normalized = {condition: max(0.0, min(1.0, score)) for condition, score in scores.items()}
    return normalized, matched


def _top_risk_indicators(
    condition_scores: Dict[str, float],
    matched: Dict[str, List[str]],
) -> List[TopRiskIndicator]:
    ranked = sorted(condition_scores.items(), key=lambda item: item[1], reverse=True)

    # Only surface indicators that have meaningful evidence:
    # either explicit symptom matches or a non-trivial score.
    meaningful_items = [
        (condition, score)
        for condition, score in ranked
        if matched.get(condition) or float(score) >= 0.2
    ]
    top_items = meaningful_items[:3]

    indicators: List[TopRiskIndicator] = []
    for condition, score in top_items:
        matched_items = matched.get(condition, [])
        reason = (
            f"Matched symptoms: {', '.join(matched_items)}"
            if matched_items
            else "No direct symptom match; score influenced by contextual factors"
        )
        indicators.append(
            TopRiskIndicator(
                condition=condition,
                score=round(float(score), 2),
                reason=reason,
            )
        )
    return indicators


def _confidence_inputs_count(symptoms: List[Symptom], periods: List[Period]) -> int:
    # Count only user-entered health logs (not prior analyses) to avoid confidence inflation.
    return min(len(symptoms), 5) + min(len(periods), 6)


class AnalysisRequest(BaseModel):
    symptom_id: Optional[int] = Field(default=None, ge=1)
    symptom_date: Optional[datetime] = None


class AnalysisResponse(BaseModel):
    analyzed_symptom_id: int
    analyzed_symptom_date: datetime
    risk_type: str
    confidence_score: float
    confidence_label: str
    probabilities: Dict[str, float]
    top_risk_indicators: List["TopRiskIndicator"]
    baseline_deviation: str
    india_context: str
    recommendations: List[str]
    diet_recommendations: List[str]
    aqi_enrichment: "AQIEnrichment"
    government_schemes: List[str]
    bias_awareness: str
    cycle_insight: str
    cycle_metrics: Dict[str, float | int | str | bool | None]
    risk_level: str
    confidence_level: str
    detected_pattern: str
    environmental_insight: str
    diet_recommendation_reasoning: str
    health_insight_report: str
    medical_disclaimer: str


class AQIEnrichment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    city: str
    aqi_value: Optional[int]
    aqi_category: str
    pm2_5: Optional[float] = None
    source: str
    advisory: Optional[str] = None


class TopRiskIndicator(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    condition: str
    score: float
    reason: str


def _is_valid_period_entry(period: Period) -> bool:
    period_end = period.end_date or period.start_date
    duration_days = (period_end.date() - period.start_date.date()).days + 1
    return duration_days >= 1


def _cycle_stats(periods: List[Period]) -> tuple[float, float]:
    valid_periods = [period for period in periods if _is_valid_period_entry(period)]
    if len(valid_periods) < 2:
        return 28.0, 0.0
    ordered = sorted(valid_periods, key=lambda period: period.start_date, reverse=True)
    cycle_lengths = []
    for index in range(len(ordered) - 1):
        gap = (ordered[index].start_date - ordered[index + 1].start_date).days
        if 1 <= gap <= 120:
            cycle_lengths.append(gap)
    if not cycle_lengths:
        return 28.0, 0.0
    avg_cycle = float(median(cycle_lengths))
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


def _baseline_30d(symptoms: List[Symptom], reference_date: datetime) -> tuple[float, float]:
    window_start = reference_date - timedelta(days=30)
    relevant = [
        symptom
        for symptom in symptoms
        if window_start <= symptom.date <= reference_date
    ]
    fatigue_values = [float(item.fatigue_level) for item in relevant if item.fatigue_level is not None]
    sleep_values = [float(item.sleep_quality) for item in relevant if item.sleep_quality is not None]

    fatigue_avg = sum(fatigue_values) / len(fatigue_values) if fatigue_values else 5.0
    sleep_avg = sum(sleep_values) / len(sleep_values) if sleep_values else 5.0
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


def _cycle_context(
    periods: List[Period], avg_cycle_length: float, cycle_variation: float
) -> Dict[str, float | int | str | bool | None]:
    valid_periods = [period for period in periods if _is_valid_period_entry(period)]
    if not valid_periods:
        return {
            "cycle_day": None,
            "in_period_window": False,
            "avg_cycle_length": round(avg_cycle_length, 1),
            "cycle_variation": round(cycle_variation, 1),
            "irregular_cycle": False,
            "prolonged_bleeding": False,
            "delayed_period_signal": False,
            "insight": "No period history is available yet, so cycle-based trend analysis is limited.",
        }

    ordered = sorted(valid_periods, key=lambda period: period.start_date, reverse=True)
    latest = ordered[0]
    start = latest.start_date.date()
    end = (latest.end_date or latest.start_date).date()
    today = datetime.now(UTC).date()

    cycle_day = max((today - start).days + 1, 1)
    in_period_window = start <= today <= end

    durations = []
    for period in ordered[:6]:
        period_end = (period.end_date or period.start_date).date()
        duration_days = (period_end - period.start_date.date()).days + 1
        if duration_days >= 1:
            durations.append(duration_days)

    latest_duration = durations[0] if durations else None
    prolonged_bleeding = any(days > 8 for days in durations)
    cycle_lengths = []
    for index in range(len(ordered) - 1):
        gap = (ordered[index].start_date - ordered[index + 1].start_date).days
        if 1 <= gap <= 120:
            cycle_lengths.append(gap)

    sufficient_history = len(cycle_lengths) >= 2
    exceeds_cycle_span = bool(
        latest_duration is not None and avg_cycle_length and latest_duration > float(avg_cycle_length)
    )
    irregular_cycle = (
        prolonged_bleeding
        or exceeds_cycle_span
        or (
            sufficient_history
            and (
                avg_cycle_length < 21
                or avg_cycle_length > 35
                or cycle_variation > 7
            )
        )
    )
    delayed_period_signal = bool(
        avg_cycle_length and cycle_day > int(round(avg_cycle_length + 7)) and not in_period_window
    )

    notes = []
    if not sufficient_history:
        notes.append("there is not enough cycle history yet to classify regularity confidently")
    elif irregular_cycle:
        notes.append("Cycle intervals look irregular from your logged period history")
    else:
        notes.append("Cycle interval trend looks relatively stable")
    if prolonged_bleeding:
        notes.append("some recent period durations appear longer than expected")
    if exceeds_cycle_span:
        notes.append("current period duration is longer than your recent cycle length")
    if delayed_period_signal:
        notes.append("current cycle appears delayed compared with your recent average")
    if in_period_window:
        notes.append("you are currently in the logged period window")
    else:
        notes.append(f"you are around cycle day {cycle_day}")

    return {
        "cycle_day": cycle_day,
        "in_period_window": in_period_window,
        "avg_cycle_length": round(avg_cycle_length, 1),
        "cycle_variation": round(cycle_variation, 1),
        "sufficient_history": sufficient_history,
        "irregular_cycle": irregular_cycle,
        "prolonged_bleeding": prolonged_bleeding,
        "exceeds_cycle_span": exceeds_cycle_span,
        "latest_period_duration": latest_duration,
        "delayed_period_signal": delayed_period_signal,
        "insight": "; ".join(notes) + ".",
    }


def _apply_cycle_adjustments(
    probabilities: Dict[str, float],
    cycle_context: Dict[str, float | int | str | bool | None],
) -> Dict[str, float]:
    adjusted = {label: float(value) for label, value in probabilities.items()}

    if not adjusted:
        return adjusted

    if bool(cycle_context.get("irregular_cycle")):
        adjusted["pcos"] = adjusted.get("pcos", 0.0) + 0.08
        adjusted["thyroid_disorder"] = adjusted.get("thyroid_disorder", 0.0) + 0.05
        adjusted["normal"] = max(adjusted.get("normal", 0.0) - 0.08, 0.01)

    if bool(cycle_context.get("prolonged_bleeding")):
        adjusted["iron_deficiency_anemia"] = adjusted.get("iron_deficiency_anemia", 0.0) + 0.08
        adjusted["normal"] = max(adjusted.get("normal", 0.0) - 0.05, 0.01)

    if bool(cycle_context.get("delayed_period_signal")):
        adjusted["pcos"] = adjusted.get("pcos", 0.0) + 0.05
        adjusted["thyroid_disorder"] = adjusted.get("thyroid_disorder", 0.0) + 0.04

    total = sum(max(value, 0.0) for value in adjusted.values())
    if total <= 0:
        return probabilities
    return {label: max(value, 0.0) / total for label, value in adjusted.items()}


def _risk_level(score: float) -> str:
    if score <= 0.3:
        return "Low"
    if score <= 0.6:
        return "Moderate"
    return "High"


def _confidence_level(num_inputs: int) -> str:
    if num_inputs < 3:
        return "Low"
    if num_inputs <= 6:
        return "Medium"
    return "High"


def _pattern_insight(
    cycle_context: Dict[str, float | int | str | bool | None],
    symptoms: List[Symptom],
    analyses: List[HealthAnalysis],
) -> str:
    findings: List[str] = []

    if bool(cycle_context.get("irregular_cycle")):
        findings.append("Cycle pattern appears irregular based on logged period intervals")

    recent_symptoms = symptoms[:5]
    fatigue_values = [float(item.fatigue_level) for item in recent_symptoms if item.fatigue_level is not None]
    if fatigue_values and (sum(fatigue_values) / len(fatigue_values)) >= 7:
        findings.append("Recent symptom logs show a recurring high-fatigue trend")

    recent_risks = [item.risk_type for item in analyses[:5]]
    if len(recent_risks) >= 3:
        top_risk = max(set(recent_risks), key=recent_risks.count)
        if recent_risks.count(top_risk) >= 2:
            findings.append(f"Recent analyses repeatedly indicate {top_risk.replace('_', ' ')} risk")

    if findings:
        return "; ".join(findings) + "."

    return "No strong recurring pattern detected yet; insights are based on limited data and will improve as more logs are added."


def _sleep_fatigue_trend_insight(symptoms: List[Symptom], reference_date: datetime) -> str:
    relevant = [item for item in symptoms if item.date <= reference_date]
    recent = relevant[:6]
    if len(recent) < 4:
        return "No strong short-term sleep/fatigue trend detected yet."

    fatigue_series = [float(item.fatigue_level) for item in recent if item.fatigue_level is not None]
    sleep_series = [float(item.sleep_quality) for item in recent if item.sleep_quality is not None]

    notes: List[str] = []
    if len(fatigue_series) >= 4:
        split = max(2, len(fatigue_series) // 2)
        early_avg = sum(fatigue_series[split:]) / len(fatigue_series[split:])
        latest_avg = sum(fatigue_series[:split]) / len(fatigue_series[:split])
        if latest_avg - early_avg >= 1.0:
            notes.append("fatigue has increased over recent entries")

    if len(sleep_series) >= 4:
        split = max(2, len(sleep_series) // 2)
        early_avg = sum(sleep_series[split:]) / len(sleep_series[split:])
        latest_avg = sum(sleep_series[:split]) / len(sleep_series[:split])
        if early_avg - latest_avg >= 1.0:
            notes.append("sleep quality has declined over recent entries")

    if not notes:
        return "No strong short-term sleep/fatigue trend detected yet."
    return "; ".join(notes).capitalize() + "."


def _environmental_insight(city: str, aqi_value: Optional[int]) -> str:
    city_label = city or "your city"
    if aqi_value is None:
        return f"AQI data is currently unavailable for {city_label}, so environmental impact is estimated with lower certainty."
    if aqi_value <= 50:
        band = "Good air quality"
        impact = "air pollution is unlikely to significantly worsen current symptoms"
    elif aqi_value <= 100:
        band = "Moderate air quality"
        impact = "sensitive users may notice mild irritation or fatigue"
    elif aqi_value <= 150:
        band = "Unhealthy for sensitive groups"
        impact = "fatigue and breathing discomfort may increase if symptoms are already present"
    elif aqi_value <= 200:
        band = "Unhealthy"
        impact = "fatigue and respiratory strain can be amplified"
    else:
        band = "Very unhealthy"
        impact = "strong health caution is advised, especially with existing symptoms"
    return f"In {city_label}, AQI is {aqi_value} ({band}); {impact}."


def _diet_reasoning(
    risk_type: str,
    fatigue_level: Optional[int],
    sleep_quality: Optional[int],
) -> str:
    notes: List[str] = []
    if risk_type == "iron_deficiency_anemia":
        notes.append(
            "Prioritize iron-rich foods such as ragi, spinach, jaggery, lentils, and chickpeas to support hemoglobin and reduce anemia-linked fatigue"
        )

    fatigue_signal = (fatigue_level is not None and fatigue_level >= 7) or (sleep_quality is not None and sleep_quality <= 4)
    if risk_type == "normal" and fatigue_level is not None and fatigue_level <= 5 and not notes:
        notes.append("Maintain balanced meals and hydration to support energy stability")
    elif fatigue_signal:
        notes.append(
            "Add energy and hydration support with banana, dates, and groundnuts to improve sustained energy and recovery"
        )

    if not notes:
        notes.append("Continue nutrient-dense meals with adequate hydration while monitoring symptom trends")
    return "; ".join(notes) + "."


def _build_health_insight_report(
    city: str,
    top_indicators: List[TopRiskIndicator],
    risk_level: str,
    confidence_level: str,
    detected_pattern: str,
    environmental_insight: str,
    diet_reasoning: str,
    medical_disclaimer: str,
) -> str:
    top_section = []
    for index, item in enumerate(top_indicators, start=1):
        score_pct = round(item.score * 100)
        top_section.append(
            f"{index}. {item.condition} - {score_pct}%\n"
            f"   Reason: {item.reason}"
        )
    top_text = "\n\n".join(top_section) if top_section else "Insufficient evidence from current symptoms to rank top indicators reliably."

    return (
        "Health Insight Report\n\n"
        f"Location: {city or 'N/A'}\n\n"
        f"Top Risk Indicators:\n{top_text}\n\n"
        f"Overall Risk Level: {risk_level}\n"
        f"Confidence: {confidence_level} (confidence improves with more data)\n\n"
        f"Detected Pattern:\n{detected_pattern}\n\n"
        f"Environmental Insight:\n{environmental_insight}\n\n"
        f"Diet Recommendation:\n{diet_reasoning}\n\n"
        f"Note:\n{medical_disclaimer}"
    )


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
    analyses = (
        db.query(HealthAnalysis)
        .filter(HealthAnalysis.user_id == current_user.id)
        .order_by(HealthAnalysis.date.desc())
        .all()
    )
    if not symptoms:
        raise HTTPException(
            status_code=400,
            detail="No symptom logs found. Please log symptoms before running analysis.",
        )

    selected_symptom: Optional[Symptom] = None
    if payload.symptom_id is not None:
        selected_symptom = next((item for item in symptoms if item.id == payload.symptom_id), None)
        if selected_symptom is None:
            raise HTTPException(status_code=404, detail="Selected symptom entry was not found")
    elif payload.symptom_date is not None:
        selected_day = payload.symptom_date.date()
        selected_symptom = next((item for item in symptoms if item.date.date() == selected_day), None)
        if selected_symptom is None:
            raise HTTPException(status_code=404, detail="No symptom entry found for selected date")
    else:
        selected_symptom = symptoms[0]

    avg_cycle_length, cycle_variation = _cycle_stats(periods)
    recent_fatigue_avg, recent_sleep_avg = _baseline_30d(symptoms, selected_symptom.date)

    features = build_features(
        description=selected_symptom.description,
        fatigue_level=selected_symptom.fatigue_level,
        sleep_quality=selected_symptom.sleep_quality,
        age=current_user.age,
        avg_cycle_length=avg_cycle_length,
        cycle_variation=cycle_variation,
        recent_fatigue_avg=recent_fatigue_avg,
        recent_sleep_avg=recent_sleep_avg,
    )
    prediction = predict_from_features(features)
    cycle_context = _cycle_context(periods, avg_cycle_length, cycle_variation)
    adjusted_probabilities = _apply_cycle_adjustments(prediction["probabilities"], cycle_context)
    condition_scores, matched_conditions = _compute_condition_scores(
        description=selected_symptom.description,
        fatigue_level=selected_symptom.fatigue_level,
        cycle_context=cycle_context,
    )
    top_indicators = _top_risk_indicators(condition_scores, matched_conditions)

    if top_indicators:
        risk_type = top_indicators[0].condition.lower().replace(" ", "_")
        confidence_score = float(top_indicators[0].score)
    else:
        risk_type = str(prediction["risk_type"])
        confidence_score = float(prediction["confidence_score"])
    adjusted_probabilities = {
        condition.lower().replace(" ", "_"): score
        for condition, score in condition_scores.items()
    }
    baseline_text = _baseline_deviation(
        selected_symptom.fatigue_level,
        selected_symptom.sleep_quality,
        recent_fatigue_avg,
        recent_sleep_avg,
    )
    recommendations = recommendations_for(risk_type, current_user.state)
    diet_recommendations = get_diet_recommendations(current_user.state, risk_type)
    aqi_enrichment = get_aqi_enrichment(current_user.state)
    government_schemes = get_government_schemes(current_user.state)
    bias_awareness = get_gender_bias_awareness(risk_type)
    medical_disclaimer = (
        "This is not a diagnosis. These insights are based on patterns and available data. Please consult a healthcare professional for medical advice."
    )
    history_count = _confidence_inputs_count(symptoms, periods)
    risk_level = _risk_level(confidence_score)
    confidence_level = _confidence_level(history_count)
    detected_pattern = _pattern_insight(cycle_context, symptoms, analyses)
    trend_insight = _sleep_fatigue_trend_insight(symptoms, selected_symptom.date)
    if trend_insight != "No strong short-term sleep/fatigue trend detected yet.":
        detected_pattern = f"{detected_pattern.rstrip('.')} ; {trend_insight}"
    environmental_insight = _environmental_insight(
        str(aqi_enrichment.get("city", current_user.state or "")),
        aqi_enrichment.get("aqi_value"),
    )
    diet_reasoning = _diet_reasoning(
        risk_type,
        selected_symptom.fatigue_level,
        selected_symptom.sleep_quality,
    )
    health_report = _build_health_insight_report(
        city=str(aqi_enrichment.get("city", current_user.state or "N/A")),
        top_indicators=top_indicators,
        risk_level=risk_level,
        confidence_level=confidence_level,
        detected_pattern=detected_pattern,
        environmental_insight=environmental_insight,
        diet_reasoning=diet_reasoning,
        medical_disclaimer=medical_disclaimer,
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
    india_context = f"{india_context} {cycle_context['insight']}"
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
        analyzed_symptom_id=selected_symptom.id,
        analyzed_symptom_date=selected_symptom.date,
        risk_type=risk_type,
        confidence_score=confidence_score,
        confidence_label=confidence_label(confidence_score),
        probabilities=adjusted_probabilities,
        top_risk_indicators=top_indicators,
        baseline_deviation=baseline_text,
        india_context=india_context,
        recommendations=recommendations,
        diet_recommendations=diet_recommendations,
        aqi_enrichment=aqi_enrichment,
        government_schemes=government_schemes,
        bias_awareness=bias_awareness,
        cycle_insight=str(cycle_context["insight"]),
        cycle_metrics=cycle_context,
        risk_level=risk_level,
        confidence_level=confidence_level,
        detected_pattern=detected_pattern,
        environmental_insight=environmental_insight,
        diet_recommendation_reasoning=diet_reasoning,
        health_insight_report=health_report,
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
