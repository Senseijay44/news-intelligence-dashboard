# News Intelligence Dashboard

A map-first news dashboard that ingests articles, extracts likely locations, and displays them on a world map.

## MVP features
- scheduled article ingestion
- normalized article storage
- geolocation extraction
- world map visualization
- API for future event clustering and fact extraction

## Quick start

```bash
git clone <your-repo-url>
cd news-intelligence-dashboard
cp backend/.env.example backend/.env
# add your NEWSAPI_KEY

docker compose up --build