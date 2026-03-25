from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class Source(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    homepage: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), nullable=False),
    )


class Article(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: Optional[int] = Field(default=None, foreign_key="source.id")
    title: str = Field(index=True)
    url: str = Field(index=True, unique=True)
    author: Optional[str] = None
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    body: Optional[str] = Field(default=None, sa_column=Column(Text))
    published_at: Optional[datetime] = Field(default=None, index=True)
    language: Optional[str] = None
    location_name: Optional[str] = Field(default=None, index=True)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    raw_payload: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    ingested_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), nullable=False),
    )


class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    canonical_title: str = Field(index=True)
    summary: Optional[str] = Field(default=None, sa_column=Column(Text))
    location_name: Optional[str] = Field(default=None, index=True)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    confidence_score: float = 0.5
    first_seen_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated_at: datetime = Field(default_factory=datetime.utcnow)


class GeocodeCache(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    query: str
    query_normalized: str = Field(index=True, unique=True)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), nullable=False),
    )
