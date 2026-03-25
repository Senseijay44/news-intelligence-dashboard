from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlmodel import Session, select

from app.db.models import Article, Event
from app.db.session import get_session
from app.schemas.event import EventMapPoint, EventNeutralSummary
from app.services.event import build_event_neutral_summary, rebuild_events

router = APIRouter(prefix="/events", tags=["events"])


@router.get("")
def list_events(limit: int = 100, session: Session = Depends(get_session)):
    statement = select(Event).order_by(Event.last_updated_at.desc()).limit(limit)
    return session.exec(statement).all()


@router.get("/map", response_model=list[EventMapPoint])
def list_event_map_points(limit: int = 200, session: Session = Depends(get_session)):
    statement = (
        select(
            Event.id,
            Event.canonical_title,
            Event.summary,
            Event.location_name,
            Event.latitude,
            Event.longitude,
            Event.confidence_score,
            Event.first_seen_at,
            Event.last_updated_at,
            func.count(Article.id).label("article_count"),
        )
        .join(Article, Article.event_id == Event.id)
        .where(Event.latitude.is_not(None))
        .where(Event.longitude.is_not(None))
        .group_by(
            Event.id,
            Event.canonical_title,
            Event.summary,
            Event.location_name,
            Event.latitude,
            Event.longitude,
            Event.confidence_score,
            Event.first_seen_at,
            Event.last_updated_at,
        )
        .order_by(Event.last_updated_at.desc())
        .limit(limit)
    )

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
            confidence_score=row.confidence_score,
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
