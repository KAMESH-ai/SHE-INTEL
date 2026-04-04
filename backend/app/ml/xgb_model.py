from __future__ import annotations

import ctypes
import os
import random
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import joblib
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier


LABELS = [
    "iron_deficiency_anemia",
    "pcos",
    "thyroid_disorder",
    "vitamin_d_deficiency",
    "diabetes_risk",
    "normal",
]


KEYWORDS = {
    "iron_deficiency_anemia": ["fatigue", "dizzy", "dizziness", "weak", "pale", "heavy bleeding", "craving", "shortness of breath"],
    "pcos": ["irregular period", "irregular cycle", "acne", "weight gain", "excess hair", "hair growth", "missed period"],
    "thyroid_disorder": ["hair loss", "cold", "constipation", "weight gain", "fatigue", "slow", "swelling"],
    "vitamin_d_deficiency": ["bone pain", "muscle pain", "joint pain", "low sunlight", "sunlight", "tired", "weak bones"],
    "diabetes_risk": ["thirst", "frequent urination", "urination", "hunger", "blurred vision", "weight loss", "sugar"],
    "normal": ["regular cycle", "normal", "fine", "ok", "good sleep", "no issues", "healthy"],
}


RECOMMENDATIONS = {
    "iron_deficiency_anemia": [
        "Consider CBC and ferritin tests.",
        "Include iron-rich foods such as ragi, lentils, spinach, and jaggery.",
    ],
    "pcos": [
        "Track cycle regularity and consider hormonal evaluation.",
        "A balanced diet with regular activity can help with symptom control.",
    ],
    "thyroid_disorder": [
        "Consider TSH and thyroid profile testing.",
        "Monitor fatigue, hair loss, and weight changes over time.",
    ],
    "vitamin_d_deficiency": [
        "Consider vitamin D testing and safe sunlight exposure.",
        "Protein-rich foods and supplements may be discussed with a clinician.",
    ],
    "diabetes_risk": [
        "Consider fasting blood sugar and HbA1c tests.",
        "Watch for persistent thirst, frequent urination, and fatigue patterns.",
    ],
    "normal": [
        "No strong risk pattern detected from the current input.",
        "Continue logging symptoms to improve future personalization.",
    ],
}


ARTIFACT_PATH = Path(
    os.getenv(
        "XGB_MODEL_ARTIFACT_PATH",
        str(Path(__file__).with_name("artifacts") / "xgb_model.joblib"),
    )
)

_LIBOMP_PATH = Path("/opt/homebrew/opt/libomp/lib/libomp.dylib")
if _LIBOMP_PATH.exists():
    os.environ["DYLD_LIBRARY_PATH"] = f"{_LIBOMP_PATH.parent}:{os.environ.get('DYLD_LIBRARY_PATH', '')}".strip(":")
    try:
        ctypes.CDLL(str(_LIBOMP_PATH))
    except OSError:
        pass


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _count_keywords(text: str, keywords: Sequence[str]) -> int:
    normalized = _normalize_text(text)
    return sum(1 for keyword in keywords if keyword in normalized)


def _feature_dict(
    description: str,
    fatigue_level: float | None,
    sleep_quality: float | None,
    age: float | None,
    avg_cycle_length: float,
    cycle_variation: float,
    recent_fatigue_avg: float,
    recent_sleep_avg: float,
) -> Dict[str, float]:
    text = _normalize_text(description)
    fatigue = float(fatigue_level if fatigue_level is not None else 5.0)
    sleep = float(sleep_quality if sleep_quality is not None else 5.0)
    return {
        "fatigue_level": fatigue,
        "sleep_quality": sleep,
        "age": float(age if age is not None else 28.0),
        "avg_cycle_length": float(avg_cycle_length),
        "cycle_variation": float(cycle_variation),
        "recent_fatigue_avg": float(recent_fatigue_avg),
        "recent_sleep_avg": float(recent_sleep_avg),
        "fatigue_delta": fatigue - float(recent_fatigue_avg),
        "sleep_delta": sleep - float(recent_sleep_avg),
        "text_length": float(len(text)),
        "iron_kw": float(_count_keywords(text, KEYWORDS["iron_deficiency_anemia"])),
        "pcos_kw": float(_count_keywords(text, KEYWORDS["pcos"])),
        "thyroid_kw": float(_count_keywords(text, KEYWORDS["thyroid_disorder"])),
        "vitamin_d_kw": float(_count_keywords(text, KEYWORDS["vitamin_d_deficiency"])),
        "diabetes_kw": float(_count_keywords(text, KEYWORDS["diabetes_risk"])),
        "normal_kw": float(_count_keywords(text, KEYWORDS["normal"])),
        "dizziness_kw": float(sum(keyword in text for keyword in ["dizzy", "dizziness", "lightheaded"])),
        "bleeding_kw": float(sum(keyword in text for keyword in ["heavy bleeding", "bleeding", "heavy periods"])),
        "acne_kw": float(sum(keyword in text for keyword in ["acne", "pimples"])),
        "hair_loss_kw": float(sum(keyword in text for keyword in ["hair loss", "hair fall"])),
        "weight_gain_kw": float(sum(keyword in text for keyword in ["weight gain", "gaining weight"])),
        "cold_kw": float(sum(keyword in text for keyword in ["cold", "cold intolerance"])),
        "constipation_kw": float(sum(keyword in text for keyword in ["constipation"])),
        "thirst_kw": float(sum(keyword in text for keyword in ["thirst", "very thirsty"])),
        "urination_kw": float(sum(keyword in text for keyword in ["frequent urination", "urination"])),
        "bone_pain_kw": float(sum(keyword in text for keyword in ["bone pain", "joint pain"])),
        "muscle_pain_kw": float(sum(keyword in text for keyword in ["muscle pain", "body ache"])),
    }


def build_features(
    description: str,
    fatigue_level: float | None,
    sleep_quality: float | None,
    age: float | None,
    avg_cycle_length: float,
    cycle_variation: float,
    recent_fatigue_avg: float,
    recent_sleep_avg: float,
) -> Dict[str, float]:
    return _feature_dict(
        description=description,
        fatigue_level=fatigue_level,
        sleep_quality=sleep_quality,
        age=age,
        avg_cycle_length=avg_cycle_length,
        cycle_variation=cycle_variation,
        recent_fatigue_avg=recent_fatigue_avg,
        recent_sleep_avg=recent_sleep_avg,
    )


def _synthetic_templates() -> Dict[str, List[Dict[str, float]]]:
    return {
        "iron_deficiency_anemia": [
            {"fatigue_level": 9, "sleep_quality": 4, "iron_kw": 3, "dizziness_kw": 1, "bleeding_kw": 1, "text_length": 90},
            {"fatigue_level": 8, "sleep_quality": 5, "iron_kw": 2, "dizziness_kw": 1, "bleeding_kw": 1, "text_length": 85},
            {"fatigue_level": 7, "sleep_quality": 4, "iron_kw": 2, "dizziness_kw": 1, "bleeding_kw": 1, "text_length": 80},
            {"fatigue_level": 10, "sleep_quality": 3, "iron_kw": 3, "dizziness_kw": 1, "bleeding_kw": 1, "text_length": 100},
        ],
        "pcos": [
            {"fatigue_level": 6, "sleep_quality": 5, "pcos_kw": 3, "acne_kw": 1, "weight_gain_kw": 1, "text_length": 88},
            {"fatigue_level": 5, "sleep_quality": 6, "pcos_kw": 3, "acne_kw": 1, "weight_gain_kw": 1, "text_length": 82},
            {"fatigue_level": 7, "sleep_quality": 5, "pcos_kw": 2, "acne_kw": 1, "weight_gain_kw": 1, "text_length": 90},
            {"fatigue_level": 6, "sleep_quality": 5, "pcos_kw": 3, "acne_kw": 1, "weight_gain_kw": 2, "text_length": 92},
        ],
        "thyroid_disorder": [
            {"fatigue_level": 8, "sleep_quality": 4, "thyroid_kw": 3, "hair_loss_kw": 1, "cold_kw": 1, "text_length": 95},
            {"fatigue_level": 9, "sleep_quality": 4, "thyroid_kw": 2, "hair_loss_kw": 1, "constipation_kw": 1, "text_length": 90},
            {"fatigue_level": 7, "sleep_quality": 5, "thyroid_kw": 3, "cold_kw": 1, "weight_gain_kw": 1, "text_length": 88},
            {"fatigue_level": 8, "sleep_quality": 3, "thyroid_kw": 2, "hair_loss_kw": 1, "weight_gain_kw": 1, "text_length": 94},
        ],
        "vitamin_d_deficiency": [
            {"fatigue_level": 7, "sleep_quality": 5, "vitamin_d_kw": 3, "bone_pain_kw": 1, "muscle_pain_kw": 1, "text_length": 93},
            {"fatigue_level": 6, "sleep_quality": 6, "vitamin_d_kw": 2, "bone_pain_kw": 1, "muscle_pain_kw": 1, "text_length": 89},
            {"fatigue_level": 8, "sleep_quality": 4, "vitamin_d_kw": 3, "bone_pain_kw": 1, "muscle_pain_kw": 1, "text_length": 86},
            {"fatigue_level": 7, "sleep_quality": 5, "vitamin_d_kw": 2, "bone_pain_kw": 1, "muscle_pain_kw": 2, "text_length": 91},
        ],
        "diabetes_risk": [
            {"fatigue_level": 7, "sleep_quality": 5, "diabetes_kw": 3, "thirst_kw": 1, "urination_kw": 1, "text_length": 96},
            {"fatigue_level": 8, "sleep_quality": 4, "diabetes_kw": 2, "thirst_kw": 1, "urination_kw": 1, "text_length": 91},
            {"fatigue_level": 6, "sleep_quality": 5, "diabetes_kw": 3, "thirst_kw": 1, "urination_kw": 2, "text_length": 98},
            {"fatigue_level": 7, "sleep_quality": 4, "diabetes_kw": 2, "thirst_kw": 2, "urination_kw": 1, "text_length": 95},
        ],
        "normal": [
            {"fatigue_level": 4, "sleep_quality": 7, "normal_kw": 3, "text_length": 70},
            {"fatigue_level": 5, "sleep_quality": 7, "normal_kw": 3, "text_length": 68},
            {"fatigue_level": 3, "sleep_quality": 8, "normal_kw": 2, "text_length": 65},
            {"fatigue_level": 4, "sleep_quality": 6, "normal_kw": 2, "text_length": 72},
        ],
    }


def _sample_text(label: str, rng: random.Random) -> str:
    text_map = {
        "iron_deficiency_anemia": [
            "Feeling dizzy, pale, and tired with heavy bleeding during periods.",
            "Low energy, weakness, and cravings after heavy menstrual loss.",
            "Fatigue, dizziness, and shortness of breath are getting worse.",
        ],
        "pcos": [
            "My periods are irregular and I have acne and weight gain.",
            "Missed periods, excess hair growth, and acne are becoming frequent.",
            "Cycle is irregular with weight gain and acne flare-ups.",
        ],
        "thyroid_disorder": [
            "I have hair loss, fatigue, constipation, and feel cold often.",
            "Weight gain, tiredness, and hair fall are happening together.",
            "Cold intolerance and hair loss have increased with fatigue.",
        ],
        "vitamin_d_deficiency": [
            "Bone pain, muscle pain, and low sunlight exposure are bothering me.",
            "I feel tired with joint pain and very little sunlight.",
            "Muscle pain and bone pain are worse after staying indoors.",
        ],
        "diabetes_risk": [
            "I have constant thirst, frequent urination, and fatigue.",
            "Frequent urination, thirst, and blurred vision are present.",
            "Feeling hungry often with thirst and tiredness.",
        ],
        "normal": [
            "No major issues, regular cycle, and good sleep.",
            "Feeling normal with no strong symptoms or cycle concerns.",
            "Healthy pattern overall with regular periods and no issues.",
        ],
    }
    return rng.choice(text_map[label])


def _build_training_frame() -> Tuple[List[Dict[str, float]], np.ndarray]:
    rng = random.Random(42)
    templates = _synthetic_templates()
    rows: List[Dict[str, float]] = []
    labels: List[int] = []

    for label_index, label in enumerate(LABELS):
        for template in templates[label]:
            for _ in range(35):
                sample = dict(template)
                sample.setdefault("fatigue_level", float(rng.randint(3, 10)))
                sample.setdefault("sleep_quality", float(rng.randint(3, 8)))
                sample.setdefault("age", float(rng.randint(18, 45)))
                sample.setdefault("avg_cycle_length", float(rng.randint(26, 34)))
                sample.setdefault("cycle_variation", float(rng.randint(0, 6)))
                sample.setdefault("recent_fatigue_avg", float(rng.randint(3, 7)))
                sample.setdefault("recent_sleep_avg", float(rng.randint(4, 8)))
                sample.setdefault("iron_kw", 0.0)
                sample.setdefault("pcos_kw", 0.0)
                sample.setdefault("thyroid_kw", 0.0)
                sample.setdefault("vitamin_d_kw", 0.0)
                sample.setdefault("diabetes_kw", 0.0)
                sample.setdefault("normal_kw", 0.0)
                sample.setdefault("dizziness_kw", 0.0)
                sample.setdefault("bleeding_kw", 0.0)
                sample.setdefault("acne_kw", 0.0)
                sample.setdefault("hair_loss_kw", 0.0)
                sample.setdefault("weight_gain_kw", 0.0)
                sample.setdefault("cold_kw", 0.0)
                sample.setdefault("constipation_kw", 0.0)
                sample.setdefault("thirst_kw", 0.0)
                sample.setdefault("urination_kw", 0.0)
                sample.setdefault("bone_pain_kw", 0.0)
                sample.setdefault("muscle_pain_kw", 0.0)
                sample["fatigue_delta"] = sample["fatigue_level"] - sample["recent_fatigue_avg"]
                sample["sleep_delta"] = sample["sleep_quality"] - sample["recent_sleep_avg"]
                sample["text_length"] = float(sample.get("text_length", 80) + rng.randint(-8, 8))
                sample["label_text"] = _sample_text(label, rng)
                rows.append(sample)
                labels.append(label_index)

    return rows, np.asarray(labels)


def _fit_model() -> Dict[str, object]:
    rows, target = _build_training_frame()
    vectorizer = DictVectorizer(sparse=True)
    feature_rows = [dict((k, v) for k, v in row.items() if k != "label_text") for row in rows]
    matrix = vectorizer.fit_transform(feature_rows)
    train_matrix, test_matrix, train_target, test_target = train_test_split(
        matrix, target, test_size=0.2, random_state=42, stratify=target
    )

    model = XGBClassifier(
        objective="multi:softprob",
        num_class=len(LABELS),
        n_estimators=180,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        min_child_weight=1,
        tree_method="hist",
        random_state=42,
        eval_metric="mlogloss",
    )
    model.fit(train_matrix, train_target)
    predictions = model.predict(test_matrix)
    metrics = {
        "accuracy": float(accuracy_score(test_target, predictions)),
        "macro_f1": float(f1_score(test_target, predictions, average="macro")),
    }
    return {
        "vectorizer": vectorizer,
        "model": model,
        "labels": LABELS,
        "metrics": metrics,
    }


def _save_artifact(artifact: Dict[str, object]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, ARTIFACT_PATH)


@lru_cache(maxsize=1)
def load_model() -> Tuple[DictVectorizer, XGBClassifier, List[str], Dict[str, float]]:
    if ARTIFACT_PATH.exists():
        artifact = joblib.load(ARTIFACT_PATH)
    else:
        artifact = _fit_model()
        _save_artifact(artifact)
    return artifact["vectorizer"], artifact["model"], artifact["labels"], artifact["metrics"]


def get_model_metadata() -> Dict[str, float]:
    _, _, _, metrics = load_model()
    return metrics


def predict_from_features(feature_row: Dict[str, float]) -> Dict[str, object]:
    vectorizer, model, labels, _ = load_model()
    matrix = vectorizer.transform([feature_row])
    probabilities = model.predict_proba(matrix)[0]
    best_index = int(np.argmax(probabilities))
    best_label = labels[best_index]
    confidence = float(probabilities[best_index])
    probability_map = {labels[index]: float(probabilities[index]) for index in range(len(labels))}
    return {
        "risk_type": best_label,
        "confidence_score": confidence,
        "confidence_label": confidence_label(confidence),
        "probabilities": probability_map,
    }


def confidence_label(confidence: float) -> str:
    if confidence >= 0.85:
        return "high"
    if confidence >= 0.65:
        return "medium"
    return "low"


def recommendations_for(label: str, state: str | None = None) -> List[str]:
    state_foods = {
        "tamil nadu": ["ragi", "spinach", "lentils"],
        "karnataka": ["ragi", "millets", "greens"],
        "maharashtra": ["sprouts", "dal", "leafy greens"],
        "delhi": ["spinach", "lentils", "seasonal fruits"],
    }
    recs = list(RECOMMENDATIONS.get(label, RECOMMENDATIONS["normal"]))
    foods = state_foods.get((state or "").strip().lower())
    if foods and label == "iron_deficiency_anemia":
        recs.append(f"State-friendly iron-rich foods: {', '.join(foods)}.")
    return recs
