from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.database import Base
from app.enums import HardinessZone, LightRequirement, SoilCondition


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