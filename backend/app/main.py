from fastapi import FastAPI

from app.api.routes_articles import router as articles_router
from app.api.routes_events import router as events_router
from app.api.routes_health import router as health_router
from app.api.routes_ingest import router as ingest_router
from app.core.config import settings
from app.services.scheduler import start_scheduler

app = FastAPI(title=settings.app_name)

app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(articles_router, prefix=settings.api_v1_prefix)
app.include_router(events_router, prefix=settings.api_v1_prefix)
app.include_router(ingest_router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
def on_startup():
    start_scheduler(settings.ingest_interval_minutes)
