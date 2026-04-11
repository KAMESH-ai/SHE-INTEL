from datetime import datetime, timedelta, UTC
from statistics import median
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.models import Period, User
from ..auth import get_current_user
from pydantic import BaseModel, Field, model_validator, ConfigDict

router = APIRouter(prefix="/periods", tags=["Periods"])


def _is_valid_period_entry(period: Period) -> bool:
    period_end = period.end_date or period.start_date
    duration_days = (period_end.date() - period.start_date.date()).days + 1
    return duration_days >= 1


class PeriodCreate(BaseModel):
    start_date: datetime
    end_date: Optional[datetime] = None
    flow_level: Optional[str] = Field(default=None, max_length=20)
    symptoms: Optional[str] = None

    @model_validator(mode="after")
    def validate_date_range(self):
        today = datetime.now(UTC).date()
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        if self.start_date.date() > today:
            raise ValueError("start_date cannot be in the future")
        if self.end_date and self.end_date.date() > today:
            raise ValueError("end_date cannot be in the future")
        return self


class PeriodResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    start_date: datetime
    end_date: Optional[datetime]
    flow_level: Optional[str]
    symptoms: Optional[str]
    created_at: datetime


def _has_overlap(
    db: Session,
    user_id: int,
    start_date: datetime,
    end_date: Optional[datetime],
    exclude_period_id: Optional[int] = None,
) -> bool:
    new_end = end_date or start_date
    query = (
        db.query(Period)
        .filter(Period.user_id == user_id)
        .filter(Period.start_date <= new_end)
        .filter(func.coalesce(Period.end_date, Period.start_date) >= start_date)
    )
    if exclude_period_id is not None:
        query = query.filter(Period.id != exclude_period_id)
    return query.first() is not None


@router.post("/", response_model=PeriodResponse)
def create_period(
    period: PeriodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if _has_overlap(
        db=db,
        user_id=current_user.id,
        start_date=period.start_date,
        end_date=period.end_date,
    ):
        raise HTTPException(
            status_code=400,
            detail="Period date range overlaps with an existing entry. Please edit existing log instead.",
        )

    db_period = Period(user_id=current_user.id, **period.model_dump())
    db.add(db_period)
    db.commit()
    db.refresh(db_period)
    return db_period


@router.put("/{period_id}", response_model=PeriodResponse)
def update_period(
    period_id: int,
    period: PeriodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = (
        db.query(Period)
        .filter(Period.id == period_id, Period.user_id == current_user.id)
        .first()
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Period entry not found")

    if _has_overlap(
        db=db,
        user_id=current_user.id,
        start_date=period.start_date,
        end_date=period.end_date,
        exclude_period_id=period_id,
    ):
        raise HTTPException(
            status_code=400,
            detail="Updated period date range overlaps with another entry.",
        )

    existing.start_date = period.start_date
    existing.end_date = period.end_date
    existing.flow_level = period.flow_level
    existing.symptoms = period.symptoms

    db.commit()
    db.refresh(existing)
    return existing


@router.delete("/{period_id}")
def delete_period(
    period_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = (
        db.query(Period)
        .filter(Period.id == period_id, Period.user_id == current_user.id)
        .first()
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Period entry not found")

    db.delete(existing)
    db.commit()
    return {"status": "deleted", "id": period_id}


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

    valid_periods = [period for period in periods if _is_valid_period_entry(period)]

    if not valid_periods:
        return {
            "periods": [],
            "prediction": None,
        }

    cycle_lengths = []
    for i in range(len(valid_periods) - 1):
        diff = (valid_periods[i].start_date - valid_periods[i + 1].start_date).days
        if 1 <= diff <= 120:
            cycle_lengths.append(diff)

    avg_cycle = float(median(cycle_lengths)) if cycle_lengths else 28.0
    period_durations = []
    for period in valid_periods[:6]:
        period_end = period.end_date or period.start_date
        duration_days = (period_end.date() - period.start_date.date()).days + 1
        if duration_days >= 1:
            period_durations.append(duration_days)

    latest_duration = period_durations[0] if period_durations else None
    prolonged_period = bool(latest_duration is not None and latest_duration > 8)
    exceeds_cycle_span = bool(
        latest_duration is not None and avg_cycle and latest_duration > float(avg_cycle)
    )
    cycle_variation = (
        float(max(cycle_lengths) - min(cycle_lengths)) if len(cycle_lengths) > 1 else 0.0
    )

    has_short_cycles = any(length < 21 for length in cycle_lengths)
    has_long_cycles = any(length > 35 for length in cycle_lengths)
    sufficient_history = len(cycle_lengths) >= 2
    cycle_status = "regular"
    if prolonged_period or exceeds_cycle_span:
        cycle_status = "irregular"
    elif not sufficient_history:
        cycle_status = "insufficient_data"
    elif has_short_cycles or has_long_cycles or cycle_variation > 7:
        cycle_status = "irregular"

    if cycle_status == "insufficient_data":
        cycle_note = (
            "Not enough cycle history yet for a reliable regularity judgment. "
            "Log at least 3 consecutive cycles for trend confidence."
        )
    elif cycle_status == "irregular":
        detail_parts = []
        if has_short_cycles:
            detail_parts.append("some cycle gaps are shorter than 21 days")
        if has_long_cycles:
            detail_parts.append("some cycle gaps are longer than 35 days")
        if cycle_variation > 7:
            detail_parts.append("cycle-to-cycle variation is high")
        if prolonged_period:
            detail_parts.append("recent period duration is longer than typical (over 8 days)")
        if exceeds_cycle_span:
            detail_parts.append("period duration exceeds your recent cycle length")
        note_detail = "; ".join(detail_parts) if detail_parts else "pattern variation is outside expected range"
        cycle_note = (
            f"Your recent cycle pattern looks irregular: {note_detail}. "
            "Consider discussing this trend with a clinician."
        )
    else:
        cycle_note = "Your recent logged cycle pattern looks stable."

    last_period = valid_periods[0]
    next_period = last_period.start_date + timedelta(days=int(round(avg_cycle)))
    ovulation_estimate = next_period - timedelta(days=14)

    return {
        "periods": [PeriodResponse.model_validate(p) for p in valid_periods],
        "prediction": {
            "avg_cycle_length": round(avg_cycle, 1),
            "cycle_variation": round(cycle_variation, 1),
            "cycle_status": cycle_status,
            "cycle_note": cycle_note,
            "sufficient_history": sufficient_history,
            "latest_period_duration": latest_duration,
            "display_month": last_period.start_date.isoformat(),
            "next_period_estimate": next_period.isoformat(),
            "ovulation_window_estimate": {
                "start": (ovulation_estimate - timedelta(days=2)).isoformat(),
                "end": (ovulation_estimate + timedelta(days=2)).isoformat(),
            },
        },
    }
