from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PatientBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, examples=["John"])
    last_name: str = Field(..., min_length=1, max_length=100, examples=["Doe"])
    date_of_birth: date = Field(..., examples=["1990-05-12"])
    gender: Literal["Male", "Female", "Other"] = Field(..., examples=["Male"])
    phone_number: str = Field(..., min_length=7, max_length=20, examples=["+91-9876543210"])
    email: Optional[EmailStr] = Field(default=None, examples=["john.doe@example.com"])
    blood_group: Optional[
        Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    ] = Field(default=None, examples=["O+"])
    admission_date: Optional[date] = Field(default=None, examples=["2026-07-20"])
    diagnosis: Optional[str] = Field(default=None, max_length=500, examples=["Routine checkup"])


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    """All fields optional so PUT/PATCH can send a partial payload."""

    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[Literal["Male", "Female", "Other"]] = None
    phone_number: Optional[str] = Field(default=None, min_length=7, max_length=20)
    email: Optional[EmailStr] = None
    blood_group: Optional[
        Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    ] = None
    admission_date: Optional[date] = None
    diagnosis: Optional[str] = Field(default=None, max_length=500)


class PatientOut(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class HealthOut(BaseModel):
    status: str
    database: str
