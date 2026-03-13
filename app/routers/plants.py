
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.plant import Plant
from app.schemas.auth import User
from app.schemas.plants import PlantResponse

router = APIRouter(prefix="/api/v1/plants")

@router.get("/{plant_id}", response_model=PlantResponse)
def get_plant_info(
    plant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plant: Plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested plant not found",
        )
    
    return plant
    



