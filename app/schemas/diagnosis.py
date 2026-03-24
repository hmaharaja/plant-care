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
    