from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session

from app.db.session import engine
from app.services.ingest_newsapi import ingest_newsapi

scheduler = BackgroundScheduler()


def scheduled_ingest():
    with Session(engine) as session:
        ingest_newsapi(session=session)


def start_scheduler(interval_minutes: int):
    scheduler.add_job(scheduled_ingest, "interval", minutes=interval_minutes, id="news_ingest", replace_existing=True)
    scheduler.start()