from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
from app.models.plant import WateringSchedule


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    # oidc_provider = Column(String, nullable=True)
    # oidc_subect = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_timezone = Column(String, default="UTC")
    phone_number = Column(String, nullable=True)

    user_plants = relationship("UserPlant", back_populates="user")


class UserPlant(Base):
    __tablename__ = "user_plants"
    
    __table_args__ = (
        UniqueConstraint('user_id', 'plant_id', name='uq_user_plant'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False)
    acquired_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    nickname = Column(String, nullable=True)

    user = relationship("User", back_populates="user_plants")
    plant = relationship("Plant", back_populates="user_plants")
    events = relationship("Event", back_populates="user_plant")
    watering_schedules = relationship("WateringSchedule", back_populates="user_plant")
