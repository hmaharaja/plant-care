
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.auth import get_current_user
from app.database import get_db
from app.enums import DiagnosisSource
from app.models.plant import Plant
from app.models.user import UserPlant
from app.models.diagnosis import DiagnosisLog
from app.schemas.auth import User
from app.schemas.diagnosis import DiagnosisResponse, DiagnosisResult, DiagnosisRequest, PublicDiagnosisRequest, DiagnosisVerifyRequest, DiagnosisLogResponse
from app.services.diagnosis_service import diagnose

router = APIRouter(prefix="/api/v1/diagnoses", tags=["diagnoses"])

@router.post("/mine", response_model=DiagnosisResponse)
def diagnose_my_plant(
    diagnosis_request: DiagnosisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Look up the user's plant
    user_plant = db.query(UserPlant).filter(
        UserPlant.id == diagnosis_request.user_plant_id,
        UserPlant.user_id == current_user.user_id
    ).first()

    if not user_plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User plant not found"
        )

    plant = user_plant.plant

    # Call the diagnosis service
    results = diagnose(
        plant_id=plant.id,
        plant_name=plant.name,
        species=plant.species,
        symptoms=diagnosis_request.symptoms,
        db=db,
        additional_notes=diagnosis_request.additional_notes
    )

    # Convert to response schema
    diagnosis_results = [
        DiagnosisResult(
            name=r["name"],
            likelihood=int(r["likelihood"] * 100),
            description=r["description"],
            source=r["source"],
            verified=r["verified"],
            treatments=r["treatments"]
        )
        for r in results
    ]

    # Save diagnosis log
    diagnosis_log = DiagnosisLog(
        user_plant_id=user_plant.id,
        user_id=current_user.user_id,
        symptoms_submitted=diagnosis_request.symptoms,
        results=[{**r, "source": r["source"].value} for r in results]
    )
    db.add(diagnosis_log)
    db.commit()

    return DiagnosisResponse(response=diagnosis_results)


@router.post("/public", response_model=DiagnosisResponse)
def diagnose_public_plant(
    public_diagnosis_request: PublicDiagnosisRequest,
    db: Session = Depends(get_db),
):
    # Look up the plant
    plant = db.query(Plant).filter(Plant.id == public_diagnosis_request.plant_id).first()

    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant not found"
        )

    # Call the diagnosis service
    results = diagnose(
        plant_id=plant.id,
        plant_name=plant.name,
        species=plant.species,
        symptoms=public_diagnosis_request.symptoms,
        db=db,
        additional_notes=public_diagnosis_request.additional_notes
    )

    # Convert to response schema
    diagnosis_results = [
        DiagnosisResult(
            name=r["name"],
            likelihood=int(r["likelihood"] * 100),
            description=r["description"],
            source=r["source"],
            verified=r["verified"],
            treatments=r["treatments"]
        )
        for r in results
    ]

    return DiagnosisResponse(response=diagnosis_results)


@router.patch("/{log_id}/verify", response_model=DiagnosisLogResponse)
def verify_diagnosis(
    log_id: int,
    verify_request: DiagnosisVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Look up the diagnosis log
    diagnosis_log = db.query(DiagnosisLog).filter(DiagnosisLog.id == log_id).first()

    if not diagnosis_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnosis log not found"
        )

    # Check user owns the diagnosis log
    if diagnosis_log.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to verify this diagnosis"
        )

    # Update matching results to set verified: true
    results = diagnosis_log.results or []
    for result in results:
        if result.get("name") in verify_request.diagnosis_names:
            result["verified"] = True

    flag_modified(diagnosis_log, "results")
    db.commit()
    db.refresh(diagnosis_log)

    # Convert to response schema
    diagnosis_results = [
        DiagnosisResult(
            name=r.get("name", ""),
            likelihood=r.get("likelihood", 0),
            description=r.get("description", ""),
            source=DiagnosisSource(r.get("source", "rule")),
            verified=r.get("verified", False),
            treatments=r.get("treatments", [])
        )
        for r in results
    ]

    return DiagnosisLogResponse(
        id=diagnosis_log.id,
        user_plant_id=diagnosis_log.user_plant_id,
        user_id=diagnosis_log.user_id,
        requested_at=diagnosis_log.requested_at.isoformat(),
        symptoms_submitted=diagnosis_log.symptoms_submitted or [],
        results=diagnosis_results
    )
