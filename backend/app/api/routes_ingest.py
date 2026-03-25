from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.services.ingest_newsapi import ingest_newsapi

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/run")
def run_ingest(session: Session = Depends(get_session)):
    return ingest_newsapi(session=session)