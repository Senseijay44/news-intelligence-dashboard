import httpx
from sqlmodel import Session, select

from app.core.config import settings
from app.db.models import Article, Source
from app.services.geocode import extract_location_candidate, geocode_location
from app.services.normalize import normalize_newsapi_article

NEWSAPI_URL = "https://newsapi.org/v2/everything"


def ingest_newsapi(session: Session, query: str | None = None, page_size: int = 25) -> dict:
    params = {
        "q": query or settings.default_news_query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": settings.newsapi_key,
    }

    with httpx.Client(timeout=30) as client:
        response = client.get(NEWSAPI_URL, params=params)
        response.raise_for_status()
        payload = response.json()

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
    return {"created": created, "skipped": skipped}