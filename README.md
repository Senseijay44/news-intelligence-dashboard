# News Intelligence Dashboard

A map-first news dashboard that ingests articles from NewsAPI, extracts place names, geocodes them, and renders the results on a Leaflet world map.

This version keeps the starter architecture but makes it production-clean for local development:
- Alembic-backed schema migrations
- spaCy NER for location extraction (instead of regex)
- geocode result caching in Postgres
- Docker Compose health-checked startup for Postgres/backend
- Next.js + Leaflet marker fixes

---

## Prerequisites

- Docker + Docker Compose
- NewsAPI key: https://newsapi.org/

---

## 1) Configure environment

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and set:

```env
NEWSAPI_KEY=your_real_key_here
```

> Keep `DATABASE_URL` set to the Docker hostname (`...@db:5432/...`) when running via Compose.

---

## 2) Start the stack

```bash
docker compose up --build
```

Corrected startup flow:
1. Postgres/PostGIS starts and must pass `pg_isready` healthcheck.
2. Backend waits for an actual SQL connection (`python scripts/wait_for_db.py`).
3. Backend runs `alembic upgrade head`.
4. Backend starts FastAPI (`uvicorn`).
5. Frontend starts Next.js and uses:
   - `INTERNAL_API_BASE_URL=http://backend:8000` for server-side fetches inside the container.
   - `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` for browser requests.

---

## 3) Verify services

- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs
- Health endpoint: http://localhost:8000/api/v1/health

You can also verify from Compose logs:

```bash
docker compose logs -f db backend frontend
```

Expected signs of success:
- backend logs `Database is ready`
- alembic upgrade completes
- no `sqlalchemy.exc.ArgumentError` in backend logs
- frontend no longer errors with `EAI_AGAIN backend`

---

## 4) Run ingestion

Trigger ingestion once:

```bash
curl -X POST http://localhost:8000/api/v1/ingest/run
```

Then open the frontend map and sidebar to view new articles.

---

## 5) Alembic migration workflow

All migration commands run from `backend/`.

### Create a new migration

```bash
cd backend
alembic revision -m "describe_change"
```

### Apply migrations

```bash
cd backend
alembic upgrade head
```

### Roll back one migration

```bash
cd backend
alembic downgrade -1
```

---

## 6) Running backend locally without Docker (optional)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
alembic upgrade head
uvicorn app.main:app --reload
```

If you run backend outside Docker, update `DATABASE_URL` to point at your reachable Postgres host.

---

## Notes

- Location extraction now uses spaCy NER labels (`GPE`, `LOC`, `FAC`).
- Geocoding checks `geocodecache` first and stores successful/empty lookups to avoid repeated external geocoding calls.
- Leaflet marker icons are explicitly configured so markers render correctly in Next.js.
