
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.event import Event
from app.models.user import UserPlant as UserPlantModel
from app.models.plant import Plant as PlantModel
from app.schemas.auth import User
from app.schemas.events import EventCreate, EventResponse
from app.schemas.plants import UserPlantCreate, UserPlantResponse

router = APIRouter(prefix="/api/v1/users")


def verify_plant_exists(db: Session, plant_id: int) -> PlantModel:
    """Verify a plant exists by ID."""
    plant = db.query(PlantModel).filter(PlantModel.id == plant_id).first()
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant not found"
        )
    return plant


def verify_user_plant_exists(db: Session, user_id: int, plant_id: int) -> UserPlantModel:
    """Verify a user plant exists for the given user and plant ID."""
    user_plant = db.query(UserPlantModel).filter(
        UserPlantModel.user_id == user_id,
        UserPlantModel.plant_id == plant_id
    ).first()
    if user_plant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plant already saved"
        )
    return user_plant


@router.get("/plants", response_model=list[UserPlantResponse])
def get_users_plants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UserPlantResponse]:
    """Gets the saved plants for a given user"""
    return db.query(UserPlantModel).filter(UserPlantModel.user_id == current_user.user_id).all()


@router.post("/plants", response_model=UserPlantResponse)
def post_users_plants(
    user_plant_obj: UserPlantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Allow a user to save a plant to their collection"""

    verify_plant_exists(db, user_plant_obj.plant_id)
    verify_user_plant_exists(db, current_user.user_id, user_plant_obj.plant_id)

    new_plant = UserPlantModel(
        user_id=current_user.user_id,
        plant_id=user_plant_obj.plant_id,
        acquired_at=user_plant_obj.acquired_at,
        nickname=user_plant_obj.nickname
    )
    
    db.add(new_plant)
    db.commit()
    db.refresh(new_plant)

    return new_plant


@router.get("/events", response_model=list[EventResponse])
def get_scheduled_events_for_user(
    user_plant_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a given user's scheduled events"""
    query = db.query(Event).filter(Event.user_id == current_user.user_id)
    if user_plant_id:
        query = query.filter(Event.user_plant_id == user_plant_id)

    return query.all()


@router.post("/events", response_model=EventResponse)
def post_event_for_user(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a care event"""
    user_plant = db.query(UserPlantModel).filter(
        UserPlantModel.id == event_data.user_plant_id,
        UserPlantModel.user_id == current_user.user_id
    ).first()
    
    if not user_plant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plant not found saved to user",
        )

    new_event = Event(**event_data.model_dump(), user_id=current_user.user_id)
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    return new_event
    
    

    



