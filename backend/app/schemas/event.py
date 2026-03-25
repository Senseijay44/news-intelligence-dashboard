from datetime import datetime
from typing import Literal, Optional
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
    source_count: int = 0
    confidence_score: float
    first_seen_at: datetime
    last_updated_at: datetime


ClaimType = Literal[
    "reported fact",
    "attributed statement",
    "analysis/inference",
    "opinion/framing",
    "prediction",
]


class ClaimSource(BaseModel):
    article_id: int
    title: str
    url: str
    published_at: Optional[datetime] = None


class EventClaim(BaseModel):
    text: str
    claim_type: ClaimType
    source_count: int
    sources: list[ClaimSource]


class EventNeutralSummary(BaseModel):
    event_id: int
    core_facts: list[EventClaim]
    disputed_points: list[EventClaim]
    uncertainty: list[str]
    source_count: int
