"""
AQI Service - Air Quality Index for Indian States
"""

AQI_DATA = {
    "Delhi": {
        "aqi_value": 180,
        "aqi_level": "Unhealthy",
        "pm25": 95,
        "health_advisory": "Avoid outdoor activities.",
    },
    "Maharashtra": {
        "aqi_value": 120,
        "aqi_level": "Moderate",
        "pm25": 45,
        "health_advisory": "Sensitive individuals should limit prolonged outdoor exposure.",
    },
    "Tamil Nadu": {
        "aqi_value": 85,
        "aqi_level": "Moderate",
        "pm25": 30,
        "health_advisory": "Air quality is acceptable.",
    },
    "Karnataka": {
        "aqi_value": 75,
        "aqi_level": "Good",
        "pm25": 25,
        "health_advisory": "Air quality is good.",
    },
    "Kerala": {
        "aqi_value": 60,
        "aqi_level": "Good",
        "pm25": 20,
        "health_advisory": "Air quality is good.",
    },
    "West Bengal": {
        "aqi_value": 140,
        "aqi_level": "Unhealthy",
        "pm25": 55,
        "health_advisory": "Everyone may begin to experience health effects.",
    },
    "Uttar Pradesh": {
        "aqi_value": 160,
        "aqi_level": "Unhealthy",
        "pm25": 75,
        "health_advisory": "Avoid outdoor activities.",
    },
    "default": {
        "aqi_value": 90,
        "aqi_level": "Moderate",
        "pm25": 32,
        "health_advisory": "Air quality is acceptable.",
    },
}


def get_aqi(state):
    return AQI_DATA.get(state, AQI_DATA["default"])
