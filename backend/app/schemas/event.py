from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class EventRead(BaseModel):
    id: int
    canonical_title: str
    summary: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    confidence_score: float
    first_seen_at: datetime
    last_updated_at: datetime


class EventMapPoint(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    location_name: Optional[str] = None
    latitude: float
    longitude: float
    article_count: int
    confidence_score: float
    first_seen_at: datetime
    last_updated_at: datetime
