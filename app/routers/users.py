
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.user import UserPlant as UserPlantModel
from app.models.plant import Plant as PlantModel
from app.schemas.auth import User
from app.schemas.plants import UserPlantCreate, UserPlantResponse

router = APIRouter(prefix="/api/v1/users")

@router.get("/plants", response_model=list[UserPlantResponse])
def get_users_plants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UserPlantResponse]:
    """Gets the saved plants for a given user"""
    return db.query(UserPlantModel).filter(UserPlantModel.user_id == current_user.user_id).all()


@router.post("/plants", response_model=UserPlantModel)
def post_users_plants(
    user_plant_obj: UserPlantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # verify the user
    if user_plant_obj.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current user is not authorized to add plants to the requested user"
        )
    
    # verify the plant exists
    plant = db.query(PlantModel).filter(PlantModel.id == user_plant_obj.plant_id).first()
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant not found"
        )

    existing = db.query(UserPlantModel).filter(
        UserPlantModel.user_id == current_user.user_id,
        UserPlantModel.plant_id == user_plant_obj.plant_id).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plant already saved"
        )

    new_plant = UserPlantModel(
        user_id=user_plant_obj.user_id,
        plant_id=user_plant_obj.plant_id,
        acquired_at=user_plant_obj.acquired_at,
        nickname=user_plant_obj.nickname
    )
    
    db.add(new_plant)
    db.commit()
    db.refresh(new_plant)

    return new_plant
    
    

    



