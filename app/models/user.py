from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    # oidc_provider = Column(String, nullable=True)
    # oidc_subect = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_timezone = Column(String, default="UTC")

    user_plants = relationship("UserPlant", back_populates="user")


class UserPlant(Base):
    __tablename__ = "user_plants"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False)
    acquired_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    nickname = Column(String, nullable=True)

    user = relationship("User", back_populates="user_plants")
    plant = relationship("Plant", back_populates="user_plants")
    events = relationship("Event", back_populates="user_plant")
