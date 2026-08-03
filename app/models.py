from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Integer, String
from sqlalchemy.sql import func

from .database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20), nullable=False)
    phone_number = Column(String(20), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    blood_group = Column(String(5), nullable=True)
    admission_date = Column(Date, nullable=True)
    diagnosis = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
