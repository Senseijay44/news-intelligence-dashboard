import httpx
from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import Session, select

from app.core.config import settings
from app.db.models import Article, Source
from app.services.event import rebuild_events
from app.services.geocode import extract_location_candidate, geocode_location
from app.services.normalize import normalize_newsapi_article

NEWSAPI_URL = "https://newsapi.org/v2/everything"


def _ensure_newsapi_key_configured() -> None:
    if not settings.has_valid_newsapi_key():
        raise HTTPException(
            status_code=400,
            detail=(
                "NEWSAPI_KEY is not configured. Set a real key in backend/.env "
                "(do not use 'replace_me')."
            ),
        )


def ingest_newsapi(session: Session, query: str | None = None, page_size: int = 25) -> dict:
    _ensure_newsapi_key_configured()

    params = {
        "q": query or settings.default_news_query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": settings.newsapi_key,
    }

    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(NEWSAPI_URL, params=params)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code in (401, 403):
            raise HTTPException(
                status_code=400,
                detail="NewsAPI rejected the API key. Update NEWSAPI_KEY in backend/.env with a valid key.",
            ) from exc

        raise HTTPException(
            status_code=502,
            detail=f"NewsAPI request failed with status {exc.response.status_code}.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Failed to reach NewsAPI.") from exc

    created = 0
    skipped = 0

    for item in payload.get("articles", []):
        normalized = normalize_newsapi_article(item)
        if not normalized.get("url"):
            skipped += 1
            continue

        existing = session.exec(select(Article).where(Article.url == normalized["url"])).first()
        if existing:
            skipped += 1
            continue

        source_name = normalized.pop("source_name") or "Unknown"
        source = session.exec(select(Source).where(Source.name == source_name)).first()
        if not source:
            source = Source(name=source_name)
            session.add(source)
            session.commit()
            session.refresh(source)

        location_name = extract_location_candidate(
            f"{normalized.get('title', '')}. {normalized.get('description', '')}"
        )
        lat, lon = geocode_location(session, location_name)

        article = Article(
            source_id=source.id,
            location_name=location_name,
            latitude=lat,
            longitude=lon,
            **normalized,
        )
        session.add(article)
        created += 1

    session.commit()

    total_articles = session.exec(select(func.count(Article.id))).one()
    geolocated_articles = session.exec(
        select(func.count(Article.id))
        .where(Article.latitude.is_not(None))
        .where(Article.longitude.is_not(None))
    ).one()

    clustering = rebuild_events(session) if created else {"events": 0, "linked_articles": 0}

    return {
        "created": created,
        "skipped": skipped,
        "totals": {
            "articles": int(total_articles or 0),
            "geolocated_articles": int(geolocated_articles or 0),
        },
        "clustering": clustering,
    }
