from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.enums import DiagnosisSource


class DiagnosisRequest(BaseModel):
    user_plant_id: int
    symptoms: list[str]
    additional_notes: Optional[str] = None


class PublicDiagnosisRequest(BaseModel):
    plant_id: int
    symptoms: list[str]
    additional_notes: Optional[str] = None


class DiagnosisResult(BaseModel):
    name: str
    likelihood: float
    description: str
    source: DiagnosisSource
    verified: bool
    treatments: list[str]


class DiagnosisResponse(BaseModel):
    response: list[DiagnosisResult] = []


class DiagnosisVerifyRequest(BaseModel):
    diagnosis_names: list[str]


class DiagnosisLogResponse(BaseModel):
    id: int
    user_plant_id: int
    user_id: int
    requested_at: datetime
    symptoms_submitted: list[str]
    results: list[DiagnosisResult]

    class Config:
        from_attributes = True
    