from datetime import datetime, timedelta, UTC
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Period, User
from app.auth import get_current_user
from pydantic import BaseModel, Field, model_validator, ConfigDict

router = APIRouter(prefix="/periods", tags=["Periods"])


class PeriodCreate(BaseModel):
    start_date: datetime
    end_date: Optional[datetime] = None
    flow_level: Optional[str] = Field(default=None, max_length=20)
    symptoms: Optional[str] = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class PeriodResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    start_date: datetime
    end_date: Optional[datetime]
    flow_level: Optional[str]
    symptoms: Optional[str]
    created_at: datetime


@router.post("/", response_model=PeriodResponse)
def create_period(
    period: PeriodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_period = Period(user_id=current_user.id, **period.model_dump())
    db.add(db_period)
    db.commit()
    db.refresh(db_period)
    return db_period


@router.get("/", response_model=List[PeriodResponse])
def get_periods(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Period)
        .filter(Period.user_id == current_user.id)
        .order_by(Period.start_date.desc())
        .all()
    )


@router.get("/calendar", response_model=dict)
def get_calendar_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    periods = (
        db.query(Period)
        .filter(Period.user_id == current_user.id)
        .order_by(Period.start_date.desc())
        .all()
    )

    if len(periods) < 2:
        return {
            "periods": [PeriodResponse.model_validate(p) for p in periods],
            "prediction": None,
        }

    cycle_lengths = []
    for i in range(len(periods) - 1):
        diff = (periods[i].start_date - periods[i + 1].start_date).days
        if 20 <= diff <= 45:
            cycle_lengths.append(diff)

    avg_cycle = sum(cycle_lengths) / len(cycle_lengths) if cycle_lengths else 28
    last_period = periods[0]
    next_period = last_period.start_date + timedelta(days=int(round(avg_cycle)))
    ovulation_estimate = next_period - timedelta(days=14)

    return {
        "periods": [PeriodResponse.model_validate(p) for p in periods],
        "prediction": {
            "avg_cycle_length": round(avg_cycle, 1),
            "next_period_estimate": next_period.isoformat(),
            "ovulation_window_estimate": {
                "start": (ovulation_estimate - timedelta(days=2)).isoformat(),
                "end": (ovulation_estimate + timedelta(days=2)).isoformat(),
            },
        },
    }
