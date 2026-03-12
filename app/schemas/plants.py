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


class CareTemplate(BaseModel):
    id: int
    plant_id: int
    template_version: int = 1
    species: str
    hardiness_zone: Optional[str] = None
    light_requirements: Optional[str] = None
    watering_interval_days: Optional[int] = None
    soil_conditions: Optional[str] = None
    issue_ids: list = []

    class Config:
        from_attributes = True


class CareTemplateCreate(BaseModel):
    plant_id: int
    template_version: int = 1
    species: str
    hardiness_zone: Optional[str] = None
    light_requirements: Optional[str] = None
    watering_interval_days: Optional[int] = None
    soil_conditions: Optional[str] = None
    issue_ids: list = []


class CareTemplateResponse(CareTemplate):
    pass