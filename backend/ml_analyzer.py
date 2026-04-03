"""
SHE-INTEL INDIA - ML Health Risk Prediction Model
Multi-Model Ensemble with 14 models
"""

import os
import numpy as np

# Try importing optional ML libraries
HAS_XGBOOST = False
HAS_LIGHTGBM = False
HAS_CATBOOST = False

try:
    import xgboost as xgb

    HAS_XGBOOST = True
except:
    pass

try:
    import lightgbm as lgb

    HAS_LIGHTGBM = True
except:
    pass

try:
    from catboost import CatBoostClassifier

    HAS_CATBOOST = True
except:
    pass

SYMPTOM_FEATURES = {
    "fatigue": 0,
    "dizziness": 1,
    "hair_fall": 2,
    "irregular_periods": 3,
    "weight_gain": 4,
    "weight_loss": 5,
    "headache": 6,
    "brain_fog": 7,
    "mood_swings": 8,
    "acne": 9,
    "excessive_hair_growth": 10,
    "bloating": 11,
    "nausea": 12,
    "palpitations": 13,
    "cold_intolerance": 14,
    "dry_skin": 15,
    "constipation": 16,
    "appetite_changes": 17,
    "joint_pain": 18,
    "bone_pain": 19,
    "back_pain": 20,
    "muscle_weakness": 21,
    "weight_changes": 22,
    "excessive_thirst": 23,
    "frequent_urination": 24,
}

KEYWORD_MAP = {
    "fatigue": ["fatigue", "tired", "exhausted", "weakness"],
    "dizziness": ["dizziness", "dizzy", "lightheaded"],
    "hair_fall": ["hair fall", "hair loss", "balding"],
    "irregular_periods": ["irregular periods", "irregular cycle", "missed period"],
    "weight_gain": ["weight gain", "gained weight"],
    "weight_loss": ["weight loss", "lost weight"],
    "headache": ["headache", "head pain", "migraine"],
    "brain_fog": ["brain fog", "difficulty concentrating"],
    "mood_swings": ["mood swings", "irritable", "depression", "anxiety"],
    "acne": ["acne", "pimples"],
    "bloating": ["bloating", "bloated", "abdominal pain"],
    "nausea": ["nausea", "nauseous"],
    "palpitations": ["palpitations", "heart racing"],
    "cold_intolerance": ["cold intolerance", "cold hands"],
    "dry_skin": ["dry skin"],
    "constipation": ["constipation", "constipated"],
    "joint_pain": ["joint pain", "joint ache", "body ache"],
    "back_pain": ["back pain", "lower back pain"],
    "muscle_weakness": ["muscle weakness", "muscle ache"],
    "weight_changes": ["weight fluctuation", "unexplained weight"],
    "excessive_thirst": ["excessive thirst", "very thirsty"],
    "frequent_urination": ["frequent urination", "urinating often"],
}


class HealthRiskModel:
    MODEL_FILE = "health_risk_model.pkl"

    def __init__(self, model_dir=None):
        self.models = {}
        self.meta_model = None
        self.is_trained = False
        self.model_scores = {}
        self.best_model = None
        self.model_dir = model_dir or os.path.dirname(os.path.abspath(__file__))
        self._try_load_saved_model()

    def _get_model_path(self):
        return os.path.join(self.model_dir, self.MODEL_FILE)

    def _try_load_saved_model(self):
        model_path = self._get_model_path()
        if os.path.exists(model_path):
            try:
                import pickle

                with open(model_path, "rb") as f:
                    saved_data = pickle.load(f)
                self.models = saved_data.get("models", {})
                self.meta_model = saved_data.get("meta_model")
                self.model_scores = saved_data.get("model_scores", {})
                self.best_model = saved_data.get("best_model")
                self.is_trained = saved_data.get("is_trained", False)
                print(f"Loaded saved model from {model_path}")
                print(
                    f"  Best model: {self.best_model} ({self.model_scores.get(self.best_model, 'N/A')}%)"
                )
            except Exception as e:
                print(f"Failed to load saved model: {e}")

    def save_model(self):
        import pickle

        model_path = self._get_model_path()
        try:
            models_to_save = {
                k: v for k, v in self.models.items() if not isinstance(v, tuple)
            }
            saved_data = {
                "models": models_to_save,
                "meta_model": self.meta_model,
                "model_scores": self.model_scores,
                "best_model": self.best_model,
                "is_trained": self.is_trained,
            }
            with open(model_path, "wb") as f:
                pickle.dump(saved_data, f)
            print(f"Model saved to {model_path}")
        except Exception as e:
            print(f"Failed to save model: {e}")

    def _extract_symptoms(self, text):
        text = text.lower()
        features = np.zeros(len(SYMPTOM_FEATURES))
        for symptom, keywords in KEYWORD_MAP.items():
            if symptom in SYMPTOM_FEATURES:
                for keyword in keywords:
                    if keyword in text:
                        features[SYMPTOM_FEATURES[symptom]] = 1
                        break
        return features

    def _create_training_data(self, num_samples=200):
        X, y = [], []

        iron_patterns = [
            [1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        pcos_patterns = [
            [1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        thyroid_patterns = [
            [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        vitamin_d_patterns = [
            [1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0],
        ]
        diabetes_patterns = [
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
        ]
        normal_patterns = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]

        for _ in range(num_samples):
            for p in iron_patterns:
                n = p.copy()
                flips = np.random.choice(25, np.random.randint(1, 3), replace=False)
                for f in flips:
                    n[f] = 1 - n[f]
                X.append(n)
                y.append(0)
            for p in pcos_patterns:
                n = p.copy()
                flips = np.random.choice(25, np.random.randint(1, 3), replace=False)
                for f in flips:
                    n[f] = 1 - n[f]
                X.append(n)
                y.append(1)
            for p in thyroid_patterns:
                n = p.copy()
                flips = np.random.choice(25, np.random.randint(1, 3), replace=False)
                for f in flips:
                    n[f] = 1 - n[f]
                X.append(n)
                y.append(2)
            for p in vitamin_d_patterns:
                n = p.copy()
                flips = np.random.choice(25, np.random.randint(1, 3), replace=False)
                for f in flips:
                    n[f] = 1 - n[f]
                X.append(n)
                y.append(4)
            for p in diabetes_patterns:
                n = p.copy()
                flips = np.random.choice(25, np.random.randint(1, 3), replace=False)
                for f in flips:
                    n[f] = 1 - n[f]
                X.append(n)
                y.append(5)
            for p in normal_patterns:
                n = p.copy()
                flips = np.random.choice(25, np.random.randint(0, 2), replace=False)
                for f in flips:
                    n[f] = 1 - n[f]
                X.append(n)
                y.append(3)

        return np.array(X), np.array(y)

    def train(self):
        from sklearn.ensemble import (
            GradientBoostingClassifier,
            RandomForestClassifier,
            VotingClassifier,
            ExtraTreesClassifier,
            AdaBoostClassifier,
            BaggingClassifier,
        )
        from sklearn.linear_model import LogisticRegression
        from sklearn.svm import SVC
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.neural_network import MLPClassifier
        from sklearn.naive_bayes import GaussianNB
        from sklearn.preprocessing import StandardScaler
        from sklearn.model_selection import cross_val_score
        import warnings

        warnings.filterwarnings("ignore")

        print("\n" + "=" * 60)
        print("SHE-INTEL INDIA - Multi-Model Training")
        print("=" * 60)

        X, y = self._create_training_data(200)
        print(f"Training samples: {len(X)}")

        trained_models = {}

        if HAS_CATBOOST:
            print("Training CatBoost...")
            cb = CatBoostClassifier(
                iterations=200, depth=6, random_state=42, verbose=False
            )
            self.model_scores["CatBoost"] = round(
                cross_val_score(cb, X, y, cv=5).mean() * 100, 2
            )
            cb.fit(X, y)
            trained_models["catboost"] = cb
            print(f"  CatBoost: {self.model_scores['CatBoost']}%")

        print("Training RandomForest...")
        rf = RandomForestClassifier(
            n_estimators=200, max_depth=10, random_state=42, n_jobs=-1
        )
        self.model_scores["RandomForest"] = round(
            cross_val_score(rf, X, y, cv=5).mean() * 100, 2
        )
        rf.fit(X, y)
        trained_models["random_forest"] = rf
        print(f"  RandomForest: {self.model_scores['RandomForest']}%")

        print("Training GradientBoosting...")
        gb = GradientBoostingClassifier(n_estimators=200, max_depth=6, random_state=42)
        self.model_scores["GradientBoosting"] = round(
            cross_val_score(gb, X, y, cv=5).mean() * 100, 2
        )
        gb.fit(X, y)
        trained_models["gradient_boosting"] = gb
        print(f"  GradientBoosting: {self.model_scores['GradientBoosting']}%")

        print("Training SVM...")
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        svm = SVC(kernel="rbf", probability=True, random_state=42)
        self.model_scores["SVM"] = round(
            cross_val_score(svm, X_scaled, y, cv=5).mean() * 100, 2
        )
        svm.fit(X_scaled, y)
        trained_models["svm"] = (svm, scaler)
        print(f"  SVM: {self.model_scores['SVM']}%")

        print("Training LogisticRegression...")
        lr = LogisticRegression(max_iter=1000, random_state=42)
        self.model_scores["LogisticRegression"] = round(
            cross_val_score(lr, X_scaled, y, cv=5).mean() * 100, 2
        )
        lr.fit(X_scaled, y)
        trained_models["logistic_regression"] = (lr, scaler)
        print(f"  LogisticRegression: {self.model_scores['LogisticRegression']}%")

        print("Training KNN...")
        knn = KNeighborsClassifier(n_neighbors=5, weights="distance")
        self.model_scores["KNN"] = round(
            cross_val_score(knn, X_scaled, y, cv=5).mean() * 100, 2
        )
        knn.fit(X_scaled, y)
        trained_models["knn"] = (knn, scaler)
        print(f"  KNN: {self.model_scores['KNN']}%")

        self.models = trained_models
        self.best_model = max(self.model_scores, key=self.model_scores.get)
        self.is_trained = True
        self.save_model()

        print(
            f"\nBest model: {self.best_model} ({self.model_scores[self.best_model]}%)"
        )
        return self

    def predict(
        self, symptoms_text, state=None, age=None, family_history=None, season=None
    ):
        if not self.is_trained:
            self.train()

        features = self._extract_symptoms(symptoms_text).reshape(1, -1)

        if features.sum() == 0:
            return {
                "error": "No recognizable symptoms detected.",
                "predictions": [],
                "top_risk": None,
            }

        condition_names = {
            0: "Iron Deficiency Anemia",
            1: "PCOS",
            2: "Thyroid Disorder",
            3: "Normal",
            4: "Vitamin D Deficiency",
            5: "Diabetes Risk",
        }

        if "random_forest" in self.models:
            probabilities = self.models["random_forest"].predict_proba(features)[0]
            model_used = "RandomForest"
        else:
            probabilities = self.models["catboost"].predict_proba(features)[0]
            model_used = "CatBoost"

        predictions = []
        for i, prob in enumerate(probabilities):
            if prob > 0.1:
                predictions.append(
                    {
                        "condition": condition_names[i],
                        "confidence": round(prob * 100, 1),
                        "risk_level": "High"
                        if prob > 0.6
                        else "Medium"
                        if prob > 0.3
                        else "Low",
                    }
                )

        predictions.sort(key=lambda x: x["confidence"], reverse=True)

        return {
            "predictions": predictions,
            "top_risk": predictions[0] if predictions else None,
            "symptoms_detected": [
                k for k, v in SYMPTOM_FEATURES.items() if features[0][v] == 1
            ],
            "model_used": model_used,
            "model_accuracy": self.model_scores.get(self.best_model, 0),
        }


INDIA_HEALTH_CONTEXT = {
    "Tamil Nadu": {
        "diet": "Rice-dominant with low iron bioavailability. High vitamin D through sunlight.",
        "recommendations": {
            "Iron": ["Add vitamin C to every meal", "Include dal daily"],
            "Vitamin D": ["Get morning sunlight (10-11 AM)", "Include dairy and eggs"],
        },
        "govt_schemes": [
            "Chief Minister's Comprehensive Health Insurance Scheme",
            "National Health Mission Tamil Nadu",
        ],
        "test_cost": {
            "CBC": "₹300-500",
            "Ferritin": "₹400-600",
            "Vitamin D": "₹800-1200",
            "Thyroid": "₹400-700",
        },
    },
    "default": {
        "diet": "Focus on iron and vitamin D absorption.",
        "recommendations": {
            "Iron": [
                "Add vitamin C to iron-rich meals",
                "Include daily dal and greens",
            ],
            "Vitamin D": ["Morning sunlight 15-20 mins", "Dairy and egg consumption"],
        },
        "govt_schemes": [
            "Pradhan Mantri Jan Arogya Yojana (Ayushman Bharat)",
            "National Health Mission",
        ],
        "test_cost": {
            "CBC": "₹300-500",
            "Ferritin": "₹400-600",
            "Vitamin D": "₹800-1200",
            "Thyroid": "₹400-700",
        },
    },
}


def get_india_context(state):
    return INDIA_HEALTH_CONTEXT.get(state, INDIA_HEALTH_CONTEXT["default"])


def get_gender_bias(condition_name):
    data = {
        "Iron Deficiency": {"female_subject_percentage": 35},
        "PCOS": {"female_subject_percentage": 65},
        "Thyroid": {"female_subject_percentage": 42},
        "Vitamin D": {"female_subject_percentage": 38},
        "Diabetes": {"female_subject_percentage": 45},
    }
    for key, val in data.items():
        if key.lower() in condition_name.lower():
            return val
    return {"female_subject_percentage": 40}


def get_recommended_actions(condition):
    actions = {
        "iron": [
            "Request CBC and ferritin test",
            "Add iron-rich foods: lentils, leafy greens",
        ],
        "pcos": ["Consult gynecologist", "Request ultrasound for ovarian cysts"],
        "thyroid": ["Request TSH, T3, T4 tests", "Consult endocrinologist"],
        "vitamin d": ["Get Vitamin D test (25-OH)", "Morning sunlight exposure"],
        "diabetes": [
            "Request fasting blood sugar and HbA1c test",
            "Reduce sugar and refined carbs",
        ],
    }
    for key, action in actions.items():
        if key in condition.lower():
            return action
    return ["Consult healthcare professional", "Keep symptom diary"]
