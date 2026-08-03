from typing import List, Optional

from sqlalchemy.orm import Session

from . import models, schemas


def get_patient(db: Session, patient_id: int) -> Optional[models.Patient]:
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()


def get_patients(
    db: Session, skip: int = 0, limit: int = 50, search: Optional[str] = None
) -> List[models.Patient]:
    query = db.query(models.Patient)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (models.Patient.first_name.ilike(like))
            | (models.Patient.last_name.ilike(like))
        )
    return query.order_by(models.Patient.id).offset(skip).limit(limit).all()


def count_patients(db: Session, search: Optional[str] = None) -> int:
    query = db.query(models.Patient)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (models.Patient.first_name.ilike(like))
            | (models.Patient.last_name.ilike(like))
        )
    return query.count()


def create_patient(db: Session, patient: schemas.PatientCreate) -> models.Patient:
    db_patient = models.Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


def update_patient(
    db: Session, db_patient: models.Patient, patient_update: schemas.PatientUpdate
) -> models.Patient:
    update_data = patient_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_patient, field, value)
    db.commit()
    db.refresh(db_patient)
    return db_patient


def delete_patient(db: Session, db_patient: models.Patient) -> None:
    db.delete(db_patient)
    db.commit()
