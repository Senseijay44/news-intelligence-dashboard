from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ArticleRead(BaseModel):
    id: int
    title: str
    url: str
    author: Optional[str] = None
    description: Optional[str] = None
    published_at: Optional[datetime] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ArticleMapPoint(BaseModel):
    id: int
    title: str
    source_name: Optional[str] = None
    published_at: Optional[datetime] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None