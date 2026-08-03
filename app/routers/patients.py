from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/patients", tags=["Patients"])


@router.post(
    "",
    response_model=schemas.PatientOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new patient",
)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_patient(db, patient)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A patient with this email already exists.",
        )


@router.get("", response_model=List[schemas.PatientOut], summary="List patients")
def list_patients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    search: Optional[str] = Query(
        None, description="Case-insensitive match on first or last name"
    ),
    db: Session = Depends(get_db),
):
    return crud.get_patients(db, skip=skip, limit=limit, search=search)


@router.get(
    "/{patient_id}", response_model=schemas.PatientOut, summary="Get a patient by ID"
)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id)
    if db_patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {patient_id} not found.",
        )
    return db_patient


@router.put(
    "/{patient_id}",
    response_model=schemas.PatientOut,
    summary="Update a patient (partial update supported)",
)
def update_patient(
    patient_id: int, patient: schemas.PatientUpdate, db: Session = Depends(get_db)
):
    db_patient = crud.get_patient(db, patient_id)
    if db_patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {patient_id} not found.",
        )
    try:
        return crud.update_patient(db, db_patient, patient)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A patient with this email already exists.",
        )


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a patient",
)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id)
    if db_patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {patient_id} not found.",
        )
    crud.delete_patient(db, db_patient)
    return None
