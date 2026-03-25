from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.models import Article
from app.db.session import get_session

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("")
def list_articles(limit: int = 100, session: Session = Depends(get_session)):
    statement = select(Article).order_by(Article.published_at.desc()).limit(limit)
    return session.exec(statement).all()


@router.get("/map")
def list_article_map_points(limit: int = 200, session: Session = Depends(get_session)):
    statement = (
        select(Article)
        .where(Article.latitude.is_not(None))
        .where(Article.longitude.is_not(None))
        .order_by(Article.published_at.desc())
        .limit(limit)
    )
    return session.exec(statement).all()