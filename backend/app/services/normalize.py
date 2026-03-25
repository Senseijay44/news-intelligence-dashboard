from datetime import datetime
from dateutil.parser import parse


def normalize_newsapi_article(item: dict) -> dict:
    return {
        "source_name": item.get("source", {}).get("name"),
        "title": item.get("title") or "Untitled",
        "url": item.get("url"),
        "author": item.get("author"),
        "description": item.get("description"),
        "body": item.get("content"),
        "published_at": parse(item["publishedAt"]) if item.get("publishedAt") else None,
        "language": None,
        "raw_payload": item,
    }