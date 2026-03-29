from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Enum as SQLEnum, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base
from app.enums import LightRequirement, SoilCondition


class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)

    user_plants = relationship("UserPlant", back_populates="plant")


class CareTemplate(Base):
    __tablename__ = "care_templates"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False)
    template_version = Column(Integer, nullable=False, default=1)
    species = Column(String, nullable=False)
    hardiness_zones = Column(JSON, default=list)  # list of HardinessZone
    light_requirements = Column(SQLEnum(LightRequirement), nullable=True)
    default_watering_interval_days = Column(Integer, nullable=True)
    soil_conditions = Column(SQLEnum(SoilCondition), nullable=True)

    # might need to use a join table later because a json column
    # can refer an issue id that doesn't exist
    issue_ids = Column(JSON, default=list)

    plant = relationship("Plant")


class WateringSchedule(Base):
    __tablename__ = "watering_schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_plant_id = Column(Integer, ForeignKey("user_plants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    watering_interval_days = Column(Integer, nullable=False)
    next_watering_date = Column(DateTime, nullable=False)
    is_custom = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user_plant = relationship("UserPlant", back_populates="watering_schedules")
    
    __table_args__ = (
        UniqueConstraint('user_plant_id', name='uq_watering_schedule_user_plant'),
    )