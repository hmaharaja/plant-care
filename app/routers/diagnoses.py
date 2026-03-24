
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.plant import Plant
from app.models.user import UserPlant
from app.models.diagnosis import DiagnosisLog
from app.schemas.auth import User
from app.schemas.diagnosis import DiagnosisResponse, DiagnosisResult, DiagnosisRequest, PublicDiagnosisRequest
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


    



