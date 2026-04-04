from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    age = Column(Integer)
    state = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    periods = relationship("Period", back_populates="user")
    symptoms = relationship("Symptom", back_populates="user")
    analyses = relationship("HealthAnalysis", back_populates="user")


class Period(Base):
    __tablename__ = "periods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    flow_level = Column(String)
    symptoms = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    user = relationship("User", back_populates="periods")


class Symptom(Base):
    __tablename__ = "symptoms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    description = Column(Text, nullable=False)
    fatigue_level = Column(Integer)
    sleep_quality = Column(Integer)
    mood = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    user = relationship("User", back_populates="symptoms")


class HealthAnalysis(Base):
    __tablename__ = "health_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    risk_type = Column(String, nullable=False)
    confidence_score = Column(Float)
    baseline_deviation = Column(Text)
    india_context = Column(Text)
    recommendations = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    user = relationship("User", back_populates="analyses")
