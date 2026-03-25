from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlmodel import Session, select

from app.db.models import Article, Source
from app.db.session import get_session
from app.services.event import compute_confidence_score

router = APIRouter(prefix="/articles", tags=["articles"])


TOPIC_KEYWORDS: dict[str, list[str]] = {
    "conflict": ["war", "conflict", "strike", "military", "attack", "ceasefire"],
    "politics": ["election", "policy", "government", "parliament", "president", "minister"],
    "economy": ["economy", "market", "inflation", "trade", "jobs", "gdp"],
    "climate": ["climate", "weather", "wildfire", "flood", "storm", "heatwave"],
    "technology": ["technology", "ai", "software", "cyber", "chip", "startup"],
}


def _apply_time_window(statement, time_window: str | None):
    if not time_window:
        return statement

    now = datetime.utcnow()
    if time_window == "24h":
        cutoff = now - timedelta(hours=24)
    elif time_window == "7d":
        cutoff = now - timedelta(days=7)
    elif time_window == "30d":
        cutoff = now - timedelta(days=30)
    else:
        return statement

    return statement.where(Article.published_at.is_not(None)).where(Article.published_at >= cutoff)


@router.get("")
def list_articles(limit: int = 100, session: Session = Depends(get_session)):
    statement = select(Article).order_by(Article.published_at.desc()).limit(limit)
    return session.exec(statement).all()


@router.get("/sources")
def list_article_sources(session: Session = Depends(get_session)):
    statement = select(Source.name).order_by(Source.name.asc())
    return session.exec(statement).all()


@router.get("/map")
def list_article_map_points(
    limit: int = 200,
    query: str | None = None,
    topic: str | None = None,
    source: str | None = None,
    time_window: str | None = None,
    session: Session = Depends(get_session),
):
    statement = (
        select(
            Article.id,
            Article.title,
            Article.location_name,
            Article.latitude,
            Article.longitude,
            Article.published_at,
            Source.name.label("source_name"),
        )
        .join(Source, Source.id == Article.source_id, isouter=True)
        .where(Article.latitude.is_not(None))
        .where(Article.longitude.is_not(None))
    )

    if query:
        like_query = f"%{query.strip()}%"
        statement = statement.where(
            or_(
                Article.title.ilike(like_query),
                Article.description.ilike(like_query),
                Article.body.ilike(like_query),
                Article.location_name.ilike(like_query),
            )
        )

    if topic and topic in TOPIC_KEYWORDS:
        topic_filters = [
            Article.title.ilike(f"%{keyword}%") | Article.description.ilike(f"%{keyword}%")
            for keyword in TOPIC_KEYWORDS[topic]
        ]
        statement = statement.where(or_(*topic_filters))

    if source:
        statement = statement.where(Source.name == source)

    statement = _apply_time_window(statement, time_window)
    statement = statement.order_by(Article.published_at.desc()).limit(limit)

    rows = session.exec(statement).all()
    return [
        {
            "id": row.id,
            "title": row.title,
            "location_name": row.location_name,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "article_count": 1,
            "confidence_score": compute_confidence_score(
                article_count=1,
                source_count=1 if row.source_name else 0,
                newest_article_at=row.published_at,
            ),
            "source_name": row.source_name,
            "published_at": row.published_at,
        }
        for row in rows
    ]
