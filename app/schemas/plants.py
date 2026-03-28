from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class Plant(BaseModel):
    id: int
    name: str
    species: str

    class Config:
        from_attributes = True


class PlantCreate(BaseModel):
    name: str
    species: str


class PlantResponse(Plant):
    pass


class UserPlantCreate(BaseModel):
    plant_id: int
    acquired_at: Optional[datetime] = None
    nickname: Optional[str] = None


class UserPlantResponse(BaseModel):
    id: int
    user_id: int
    plant_id: int
    acquired_at: Optional[datetime] = None
    nickname: Optional[str] = None
