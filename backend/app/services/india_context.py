from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from time import time
from typing import Dict, List, Optional, Tuple

import requests


DATA_FILE = Path(__file__).with_name("india_context_data.json")
AQI_CACHE_TTL_SECONDS = 30 * 60
_AQI_CACHE: Dict[str, Tuple[float, Dict[str, object]]] = {}


def _load_data() -> Dict[str, object]:
    if DATA_FILE.exists():
        with DATA_FILE.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    return {
        "state_profiles": {},
        "national_schemes": [],
        "state_schemes": {},
        "lab_base_costs": {},
        "bias_notes": {},
    }


@lru_cache(maxsize=1)
def get_context_data() -> Dict[str, object]:
    return _load_data()


def _state_key(state: Optional[str]) -> str:
    return (state or "").strip().lower()


def get_state_profile(state: Optional[str]) -> Dict[str, object]:
    data = get_context_data()
    state_profiles = data.get("state_profiles", {})
    return state_profiles.get(
        _state_key(state),
        {
            "city": "India",
            "latitude": None,
            "longitude": None,
            "diet": ["leafy greens", "lentils", "seasonal vegetables", "fruits"],
            "aqi_note": "Use local AQI data when available for city-level enrichment.",
        },
    )


def _estimate_aqi_category(aqi_value: Optional[int]) -> str:
    if aqi_value is None:
        return "moderate"
    if aqi_value <= 50:
        return "good"
    if aqi_value <= 100:
        return "satisfactory"
    if aqi_value <= 200:
        return "moderate"
    if aqi_value <= 300:
        return "poor"
    if aqi_value <= 400:
        return "very poor"
    return "severe"


def _cached_aqi(state: Optional[str]) -> Optional[Dict[str, object]]:
    cache_entry = _AQI_CACHE.get(_state_key(state))
    if not cache_entry:
        return None
    cached_at, payload = cache_entry
    if time() - cached_at > AQI_CACHE_TTL_SECONDS:
        _AQI_CACHE.pop(_state_key(state), None)
        return None
    return payload


def _store_aqi(state: Optional[str], payload: Dict[str, object]) -> None:
    _AQI_CACHE[_state_key(state)] = (time(), payload)


def get_aqi_enrichment(state: Optional[str]) -> Dict[str, object]:
    cached = _cached_aqi(state)
    if cached is not None:
        return cached

    profile = get_state_profile(state)
    latitude = profile.get("latitude")
    longitude = profile.get("longitude")

    if latitude is not None and longitude is not None:
        try:
            response = requests.get(
                "https://air-quality-api.open-meteo.com/v1/air-quality",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "us_aqi,pm2_5",
                },
                timeout=5,
            )
            response.raise_for_status()
            payload = response.json()
            current = payload.get("current", {})
            aqi_value = current.get("us_aqi") or current.get("us_aqi_index")
            if isinstance(aqi_value, (int, float)):
                aqi_value = int(round(aqi_value))
            result = {
                "city": profile.get("city"),
                "aqi_value": aqi_value,
                "aqi_category": _estimate_aqi_category(aqi_value if isinstance(aqi_value, int) else None),
                "pm2_5": current.get("pm2_5"),
                "source": "open-meteo",
                "advisory": profile.get("aqi_note"),
            }
            _store_aqi(state, result)
            return result
        except Exception:
            pass

    fallback_value = 85 if _state_key(state) in {"tamil nadu", "kerala"} else 120 if _state_key(state) in {"delhi", "maharashtra"} else 95
    result = {
        "city": profile.get("city"),
        "aqi_value": fallback_value,
        "aqi_category": _estimate_aqi_category(fallback_value),
        "pm2_5": None,
        "source": "local_estimate",
        "advisory": profile.get("aqi_note"),
    }
    _store_aqi(state, result)
    return result


def get_diet_recommendations(state: Optional[str], risk_type: str) -> List[str]:
    profile = get_state_profile(state)
    foods = profile.get("diet", [])
    food_text = ", ".join(str(item) for item in foods)
    if risk_type == "iron_deficiency_anemia":
        return [
            "Prioritize iron-rich meals across the week.",
            f"State-specific foods: {food_text}.",
        ]
    if risk_type == "pcos":
        return [
            "Keep meals balanced with protein, fiber, and regular timing.",
            f"Helpful local foods: {food_text}.",
        ]
    if risk_type == "thyroid_disorder":
        return [
            "Keep meals consistent and track fatigue or weight changes.",
            f"Helpful local foods: {food_text}.",
        ]
    if risk_type == "vitamin_d_deficiency":
        return [
            "Include calcium-rich foods and safe sunlight exposure.",
            f"Helpful local foods: {food_text}.",
        ]
    if risk_type == "diabetes_risk":
        return [
            "Reduce refined sugar spikes and watch meal timing.",
            f"Helpful local foods: {food_text}.",
        ]
    return [
        "Continue a balanced diet and keep symptom logs updated.",
        f"Local healthy options: {food_text}.",
    ]


def get_government_schemes(state: Optional[str]) -> List[str]:
    data = get_context_data()
    schemes = list(data.get("national_schemes", []))
    schemes.extend(data.get("state_schemes", {}).get(_state_key(state), []))
    return schemes


def get_lab_cost_estimates(risk_type: str, state: Optional[str]) -> List[Dict[str, object]]:
    data = get_context_data()
    profile = get_state_profile(state)
    city = str(profile.get("city", "India"))
    state_key = _state_key(state)
    city_factor = 1.15 if state_key in {"delhi", "maharashtra"} else 1.0 if state_key in {"tamil nadu", "karnataka"} else 1.05
    estimates: List[Dict[str, object]] = []
    base_costs = data.get("lab_base_costs", {}).get(risk_type, data.get("lab_base_costs", {}).get("normal", []))
    for item in base_costs:
        low = int(round(float(item["low"]) * city_factor))
        high = int(round(float(item["high"]) * city_factor))
        estimates.append(
            {
                "test": item["test"],
                "estimated_low_inr": low,
                "estimated_high_inr": high,
                "city": city,
            }
        )
    return estimates


def get_gender_bias_awareness(risk_type: str) -> str:
    data = get_context_data()
    bias_notes = data.get("bias_notes", {})
    return bias_notes.get(
        risk_type,
        bias_notes.get("normal", "No strong bias-sensitive risk signal detected from the current input."),
    )
