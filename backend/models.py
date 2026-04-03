from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    created_at: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PeriodCreate(BaseModel):
    start_date: str
    end_date: Optional[str] = None
    flow_level: str = "medium"
    symptoms: Optional[str] = None


class PeriodResponse(BaseModel):
    id: int
    start_date: str
    end_date: Optional[str]
    flow_level: str
    symptoms: Optional[str]
    created_at: str
