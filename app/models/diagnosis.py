from sqlalchemy import Column, String, Integer, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    symptoms = Column(JSON, default=list)
    treatments = Column(JSON, default=list)


class DiagnosisLog(Base):
    __tablename__ = "diagnosis_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_plant_id = Column(Integer, ForeignKey("user_plants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    requested_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    symptoms_submitted = Column(JSON, default=list)
    results = Column(JSON, default=list)

    user_plant = relationship("UserPlant")
    user = relationship("User")
