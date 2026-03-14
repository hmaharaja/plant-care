from datetime import datetime
from typing import Optional
from app.models.event import EventSource, EventType

from pydantic import BaseModel, Field


class EventBase(BaseModel):
    user_plant_id: int
    timestamp: datetime
    event_type: EventType
    source: EventSource
    scheduled: Optional[bool] = False
    completed: Optional[bool] = False
    notes: Optional[str] = Field(default=None, max_length=500)


class EventCreate(EventBase):
    pass


class EventResponse(EventBase):
    user_id: int
    event_id: int
    
    class Config:
        from_attributes = True