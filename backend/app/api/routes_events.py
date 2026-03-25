from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, or_
from sqlmodel import Session, select

from app.db.models import Article, Event, Source
from app.db.session import get_session
from app.schemas.event import EventMapPoint, EventNeutralSummary
from app.services.event import build_event_neutral_summary, compute_confidence_score, rebuild_events

router = APIRouter(prefix="/events", tags=["events"])


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

    return statement.where(Event.last_updated_at >= cutoff)


@router.get("")
def list_events(limit: int = 100, session: Session = Depends(get_session)):
    statement = select(Event).order_by(Event.last_updated_at.desc()).limit(limit)
    return session.exec(statement).all()


@router.get("/map", response_model=list[EventMapPoint])
def list_event_map_points(
    limit: int = 200,
    query: str | None = None,
    topic: str | None = None,
    source: str | None = None,
    time_window: str | None = None,
    session: Session = Depends(get_session),
):
    statement = (
        select(
            Event.id,
            Event.canonical_title,
            Event.summary,
            Event.location_name,
            Event.latitude,
            Event.longitude,
            Event.first_seen_at,
            Event.last_updated_at,
            func.count(Article.id).label("article_count"),
            func.count(func.distinct(Source.id)).label("source_count"),
        )
        .join(Article, Article.event_id == Event.id)
        .join(Source, Source.id == Article.source_id, isouter=True)
        .where(Event.latitude.is_not(None))
        .where(Event.longitude.is_not(None))
    )

    if query:
        like_query = f"%{query.strip()}%"
        statement = statement.where(
            or_(
                Event.canonical_title.ilike(like_query),
                Event.summary.ilike(like_query),
                Event.location_name.ilike(like_query),
                Article.title.ilike(like_query),
            )
        )

    if topic and topic in TOPIC_KEYWORDS:
        topic_filters = [
            Event.canonical_title.ilike(f"%{keyword}%")
            | Event.summary.ilike(f"%{keyword}%")
            | Article.title.ilike(f"%{keyword}%")
            for keyword in TOPIC_KEYWORDS[topic]
        ]
        statement = statement.where(or_(*topic_filters))

    if source:
        statement = statement.where(Source.name == source)

    statement = _apply_time_window(statement, time_window)

    statement = statement.group_by(
        Event.id,
        Event.canonical_title,
        Event.summary,
        Event.location_name,
        Event.latitude,
        Event.longitude,
        Event.first_seen_at,
        Event.last_updated_at,
    ).order_by(Event.last_updated_at.desc()).limit(limit)

    rows = session.exec(statement).all()
    return [
        EventMapPoint(
            id=row.id,
            title=row.canonical_title,
            summary=row.summary,
            location_name=row.location_name,
            latitude=row.latitude,
            longitude=row.longitude,
            article_count=row.article_count,
            confidence_score=compute_confidence_score(
                article_count=row.article_count,
                source_count=row.source_count,
                newest_article_at=row.last_updated_at,
                oldest_article_at=row.first_seen_at,
            ),
            source_count=row.source_count,
            first_seen_at=row.first_seen_at,
            last_updated_at=row.last_updated_at,
        )
        for row in rows
    ]


@router.post("/rebuild")
def rebuild_event_clusters(session: Session = Depends(get_session)):
    return rebuild_events(session)


@router.get("/{event_id}/neutral-summary", response_model=EventNeutralSummary)
def get_event_neutral_summary(event_id: int, session: Session = Depends(get_session)):
    event = session.get(Event, event_id)
    if not event:
        return {
            "event_id": event_id,
            "core_facts": [],
            "disputed_points": [],
            "uncertainty": ["event not found"],
            "source_count": 0,
        }

    articles = session.exec(
        select(Article).where(Article.event_id == event_id).order_by(Article.published_at.desc())
    ).all()
    return build_event_neutral_summary(event, articles)
