from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


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
    hardiness_zone = Column(String)
    light_requirements = Column(String)  # enum later
    watering_interval_days = Column(Integer)
    soil_conditions = Column(String)     # enum later

    # might need to use a join table later because a json column
    # can refer an issue id that doesn't exist
    issue_ids = Column(JSON, default=list)

    plant = relationship("Plant")