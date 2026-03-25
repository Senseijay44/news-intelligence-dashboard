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
NEWSAPI_MAX_PAGE_SIZE = 100


def _ensure_newsapi_key_configured() -> None:
    if not settings.has_valid_newsapi_key():
        raise HTTPException(
            status_code=400,
            detail=(
                "NEWSAPI_KEY is not configured. Set a real key in backend/.env "
                "(do not use 'replace_me')."
            ),
        )


def ingest_newsapi(session: Session, query: str | None = None) -> dict:
    _ensure_newsapi_key_configured()

    configured_page_size = max(1, settings.ingest_page_size)
    page_size = min(configured_page_size, NEWSAPI_MAX_PAGE_SIZE)
    max_pages = max(1, settings.ingest_max_pages)
    max_articles_per_run = max(1, settings.ingest_max_articles_per_run)

    created = 0
    skipped = 0
    fetched = 0
    pages_processed = 0
    distinct_sources_seen: set[str] = set()
    seen_urls: set[str] = set()

    try:
        with httpx.Client(timeout=30) as client:
            for page in range(1, max_pages + 1):
                if fetched >= max_articles_per_run:
                    break

                remaining = max_articles_per_run - fetched
                request_page_size = min(page_size, remaining)
                params = {
                    "q": query or settings.default_news_query,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": request_page_size,
                    "page": page,
                    "apiKey": settings.newsapi_key,
                }

                response = client.get(NEWSAPI_URL, params=params)
                response.raise_for_status()
                payload = response.json()

                raw_articles = payload.get("articles", [])
                pages_processed += 1

                if not raw_articles:
                    break

                fetched += len(raw_articles)

                normalized_items = []
                page_urls = set()
                for item in raw_articles:
                    normalized = normalize_newsapi_article(item)
                    source_name = (normalized.pop("source_name", None) or "Unknown").strip() or "Unknown"
                    distinct_sources_seen.add(source_name)

                    url = normalized.get("url")
                    if not url:
                        skipped += 1
                        continue

                    if url in seen_urls:
                        skipped += 1
                        continue

                    seen_urls.add(url)
                    page_urls.add(url)
                    normalized_items.append((normalized, source_name))

                existing_urls = set()
                if page_urls:
                    existing_urls = set(
                        session.exec(select(Article.url).where(Article.url.in_(page_urls))).all()
                    )

                for normalized, source_name in normalized_items:
                    if normalized["url"] in existing_urls:
                        skipped += 1
                        continue

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

                if len(raw_articles) < request_page_size:
                    break

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

    total_articles = session.exec(select(func.count(Article.id))).one()
    geolocated_articles = session.exec(
        select(func.count(Article.id))
        .where(Article.latitude.is_not(None))
        .where(Article.longitude.is_not(None))
    ).one()

    clustering = rebuild_events(session) if created else {"events": 0, "linked_articles": 0}

    return {
        "fetched": fetched,
        "created": created,
        "skipped": skipped,
        "pages_processed": pages_processed,
        "distinct_sources_seen": len(distinct_sources_seen),
        "effective_page_size": page_size,
        "max_page_size_supported": NEWSAPI_MAX_PAGE_SIZE,
        "totals": {
            "articles": int(total_articles or 0),
            "geolocated_articles": int(geolocated_articles or 0),
        },
        "clustering": clustering,
    }
