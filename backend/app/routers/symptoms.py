from datetime import datetime, UTC
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.models import Symptom, User
from ..auth import get_current_user
from pydantic import BaseModel, Field, field_validator, ConfigDict

router = APIRouter(prefix="/symptoms", tags=["Symptoms"])


class SymptomCreate(BaseModel):
    description: str = Field(min_length=3, max_length=2000)
    fatigue_level: Optional[int] = Field(default=None, ge=1, le=10)
    sleep_quality: Optional[int] = Field(default=None, ge=1, le=10)
    mood: Optional[str] = Field(default=None, max_length=50)
    date: Optional[datetime] = None

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("description cannot be empty")
        return text


class SymptomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    fatigue_level: Optional[int]
    sleep_quality: Optional[int]
    mood: Optional[str]
    date: datetime
    created_at: datetime


@router.post("/", response_model=SymptomResponse)
def create_symptom(
    symptom: SymptomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_symptom = Symptom(
        user_id=current_user.id,
        description=symptom.description,
        fatigue_level=symptom.fatigue_level,
        sleep_quality=symptom.sleep_quality,
        mood=symptom.mood,
        date=symptom.date or datetime.now(UTC),
    )
    db.add(db_symptom)
    db.commit()
    db.refresh(db_symptom)
    return db_symptom


@router.get("/", response_model=List[SymptomResponse])
def get_symptoms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=30, ge=1, le=365),
):
    return (
        db.query(Symptom)
        .filter(Symptom.user_id == current_user.id)
        .order_by(Symptom.date.desc())
        .limit(limit)
        .all()
    )
