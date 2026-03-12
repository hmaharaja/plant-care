
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from app.models.plant import Plant

router = APIRouter(prefix="api/v1/plants")

@router.get("/{plant_id}")
def get_plant_info(
    plant_id: int,
    db: Session,
):
    plant = db.query(Plant).filter(plant_id == Plant.id)
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested plant not found",
        )
    



