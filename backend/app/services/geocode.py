from __future__ import annotations

from typing import Optional, Tuple

import spacy
from geopy.geocoders import Nominatim
from sqlmodel import Session, select

from app.db.models import GeocodeCache

geolocator = Nominatim(user_agent="news-intelligence-dashboard")
_NLP = spacy.load("en_core_web_sm")
_GPE_ENTITY_TYPES = {"GPE", "LOC", "FAC"}


def _normalize_query(value: str) -> str:
    return " ".join(value.lower().split())


def extract_location_candidate(text: str) -> Optional[str]:
    if not text or not text.strip():
        return None

    doc = _NLP(text)
    for ent in doc.ents:
        if ent.label_ in _GPE_ENTITY_TYPES:
            candidate = ent.text.strip(" .,;:\n\t")
            if len(candidate) > 2:
                return candidate

    return None


def geocode_location(session: Session, location_name: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
    if not location_name:
        return None, None

    normalized = _normalize_query(location_name)
    cached = session.exec(
        select(GeocodeCache).where(GeocodeCache.query_normalized == normalized)
    ).first()
    if cached:
        return cached.latitude, cached.longitude

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    try:
        result = geolocator.geocode(location_name, timeout=10)
        if result:
            latitude = result.latitude
            longitude = result.longitude
    except Exception:
        latitude = None
        longitude = None

    session.add(
        GeocodeCache(
            query=location_name,
            query_normalized=normalized,
            latitude=latitude,
            longitude=longitude,
        )
    )
    session.commit()
    return latitude, longitude
