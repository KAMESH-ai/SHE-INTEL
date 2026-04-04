import json
from datetime import datetime, timedelta, UTC
from random import choice, randint
from uuid import uuid4

import requests


API_URL = "http://localhost:8002"


USERS = [
    {"name": "Asha Menon", "age": 26, "state": "Tamil Nadu"},
    {"name": "Riya Sharma", "age": 31, "state": "Delhi"},
    {"name": "Neha Kulkarni", "age": 29, "state": "Maharashtra"},
    {"name": "Priya Patel", "age": 24, "state": "Gujarat"},
    {"name": "Ananya Das", "age": 27, "state": "West Bengal"},
    {"name": "Kavya Nair", "age": 30, "state": "Kerala"},
    {"name": "Meera Singh", "age": 25, "state": "Rajasthan"},
]

SYMPTOM_TEMPLATES = [
    "Feeling very tired with occasional dizziness and heavy flow this month.",
    "Noticing irregular cycles, acne, and mood swings over the last weeks.",
    "Experiencing hair fall, fatigue, and cold sensitivity.",
    "Mild cramps and low energy after poor sleep.",
    "Severe fatigue with pale skin and shortness of breath during periods.",
    "Weight gain, irregular periods, and excessive hair growth on face.",
    "Feeling extremely tired, hair falling out, and feeling cold all the time.",
    "Increased thirst, frequent urination, and unexplained weight loss.",
    "Feeling exhausted even after sleeping, joint pain, and brain fog.",
    "Dizziness, weakness, and pale complexion especially during periods.",
]

MOODS = ["calm", "anxious", "irritable", "sad", "happy"]


def post(path, payload, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.post(
        f"{API_URL}{path}", headers=headers, data=json.dumps(payload), timeout=10
    )
    response.raise_for_status()
    return response.json()


def get(path, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}{path}", headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()


def seed_user(profile):
    email = f"demo_{uuid4().hex[:8]}@example.com"
    password = "secret123"

    post(
        "/auth/register",
        {
            "email": email,
            "password": password,
            "name": profile["name"],
            "age": profile["age"],
            "state": profile["state"],
        },
    )

    login = post("/auth/login", {"email": email, "password": password})
    token = login["access_token"]

    start = datetime.now(UTC) - timedelta(days=90)
    for index in range(4):
        period_start = (start + timedelta(days=index * 28)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        period_end = period_start + timedelta(days=4)
        post(
            "/periods/",
            {
                "start_date": period_start.isoformat(),
                "end_date": period_end.isoformat(),
                "flow_level": choice(["Light", "Medium", "Heavy"]),
                "symptoms": choice(SYMPTOM_TEMPLATES),
            },
            token=token,
        )

    for _ in range(6):
        post(
            "/symptoms/",
            {
                "description": choice(SYMPTOM_TEMPLATES),
                "fatigue_level": randint(4, 9),
                "sleep_quality": randint(3, 8),
                "mood": choice(MOODS),
            },
            token=token,
        )

    analysis = post(
        "/analysis/analyze",
        {
            "description": choice(SYMPTOM_TEMPLATES),
            "fatigue_level": randint(5, 9),
            "sleep_quality": randint(3, 8),
            "mood": choice(MOODS),
        },
        token=token,
    )

    return {
        "email": email,
        "password": password,
        "name": profile["name"],
        "state": profile["state"],
        "risk_type": analysis["risk_type"],
        "confidence": analysis["confidence_score"],
        "history_count": len(get("/analysis/history", token=token)),
    }


def main():
    results = []
    for profile in USERS:
        results.append(seed_user(profile))

    print("Seed complete. Demo accounts:")
    for item in results:
        print(
            f"- {item['name']} ({item['state']}): {item['email']} / {item['password']} | "
            f"risk={item['risk_type']} conf={item['confidence']:.2f} history={item['history_count']}"
        )


if __name__ == "__main__":
    main()
