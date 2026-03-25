from pydantic import BaseModel
from typing import Optional


class CareTemplateCreate(BaseModel):
    plant_id: int
    template_version: int = 1
    species: str
    hardiness_zone: Optional[str] = None
    light_requirements: Optional[str] = None
    default_watering_interval_days: Optional[int] = None
    soil_conditions: Optional[str] = None
    issue_ids: list[int] = []


class CareTemplateResponse(BaseModel):
    id: int
    plant_id: int
    template_version: int
    species: str
    hardiness_zone: Optional[str] = None
    light_requirements: Optional[str] = None
    default_watering_interval_days: Optional[int] = None
    soil_conditions: Optional[str] = None
    issue_ids: list[int] = []

    class Config:
        from_attributes = True


class CareTemplatePatch(BaseModel):
    template_version: Optional[int] = None
    species: Optional[str] = None
    hardiness_zone: Optional[str] = None
    light_requirements: Optional[str] = None
    default_watering_interval_days: Optional[int] = None
    soil_conditions: Optional[str] = None
    issue_ids: Optional[list[int]] = None