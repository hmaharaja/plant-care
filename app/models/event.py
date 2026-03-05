from enum import Enum
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class EventType(str, Enum):
    WATERED = "watered"
    FERTILIZED = "fertilized"
    REPOTTED = "repotted"
    PRUNED = "pruned"


class EventSource(str, Enum):
    USER = "user"
    SYSTEM = "system"


class Event(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    user_plant_id = Column(Integer, ForeignKey("user_plants.id"), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    event_type = Column(SQLEnum(EventType), nullable=False)
    scheduled = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)
    notes = Column(String, nullable=True)
    source = Column(SQLEnum(EventSource), default=EventSource.USER)

    user = relationship("User")
    user_plant = relationship("UserPlant", back_populates="events")
