from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
import math
import re
from typing import Iterable, Sequence

from sqlmodel import Session, select

from app.db.models import Article, Event

TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")
ENTITY_RE = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b")


@dataclass
class ArticleSignal:
    article: Article
    vector: Counter[str]
    entities: set[str]


@dataclass
class ClusterConfig:
    embedding_weight: float = 0.55
    time_weight: float = 0.25
    entity_weight: float = 0.20
    similarity_threshold: float = 0.45
    time_window_hours: int = 72


def _tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def _build_vector(title: str | None, description: str | None) -> Counter[str]:
    text = f"{title or ''} {description or ''}".strip()
    return Counter(_tokenize(text))


def _extract_entities(title: str | None, description: str | None) -> set[str]:
    text = f"{title or ''}. {description or ''}"
    return {m.group(0).strip().lower() for m in ENTITY_RE.finditer(text)}


def _cosine_similarity(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0

    dot = sum(left[token] * right[token] for token in set(left) & set(right))
    left_norm = math.sqrt(sum(v * v for v in left.values()))
    right_norm = math.sqrt(sum(v * v for v in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def _time_similarity(left: datetime | None, right: datetime | None, window_hours: int) -> float:
    if not left or not right:
        return 0.0
    delta_hours = abs((left - right).total_seconds()) / 3600
    return max(0.0, 1.0 - (delta_hours / window_hours))


def _entity_overlap(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def article_similarity(left: ArticleSignal, right: ArticleSignal, config: ClusterConfig) -> float:
    embedding_score = _cosine_similarity(left.vector, right.vector)
    time_score = _time_similarity(left.article.published_at, right.article.published_at, config.time_window_hours)
    entity_score = _entity_overlap(left.entities, right.entities)

    return (
        embedding_score * config.embedding_weight
        + time_score * config.time_weight
        + entity_score * config.entity_weight
    )


def cluster_article_signals(
    signals: Sequence[ArticleSignal], config: ClusterConfig | None = None
) -> list[list[ArticleSignal]]:
    cfg = config or ClusterConfig()
    clusters: list[list[ArticleSignal]] = []

    for signal in signals:
        best_cluster_idx = -1
        best_similarity = 0.0

        for idx, cluster in enumerate(clusters):
            similarities = [article_similarity(signal, existing, cfg) for existing in cluster]
            cluster_similarity = sum(similarities) / len(similarities)
            if cluster_similarity > best_similarity:
                best_similarity = cluster_similarity
                best_cluster_idx = idx

        if best_cluster_idx >= 0 and best_similarity >= cfg.similarity_threshold:
            clusters[best_cluster_idx].append(signal)
        else:
            clusters.append([signal])

    return clusters


def _to_signal(article: Article) -> ArticleSignal:
    return ArticleSignal(
        article=article,
        vector=_build_vector(article.title, article.description),
        entities=_extract_entities(article.title, article.description),
    )


def _cluster_centroid_location(articles: Iterable[Article]) -> tuple[float | None, float | None, str | None]:
    geolocated = [a for a in articles if a.latitude is not None and a.longitude is not None]
    if not geolocated:
        return None, None, None

    lat = sum(a.latitude for a in geolocated if a.latitude is not None) / len(geolocated)
    lon = sum(a.longitude for a in geolocated if a.longitude is not None) / len(geolocated)
    location = geolocated[0].location_name
    return lat, lon, location


def rebuild_events(session: Session, lookback_hours: int = 120) -> dict:
    cutoff = datetime.utcnow() - timedelta(hours=lookback_hours)
    statement = select(Article).where(Article.published_at.is_not(None)).where(Article.published_at >= cutoff)
    articles = session.exec(statement).all()

    if not articles:
        return {"events": 0, "linked_articles": 0}

    signals = [_to_signal(article) for article in articles]
    clusters = cluster_article_signals(signals)

    for article in articles:
        article.event_id = None

    session.query(Event).delete()

    linked_articles = 0
    for cluster in clusters:
        cluster_articles = [s.article for s in cluster]
        sorted_articles = sorted(cluster_articles, key=lambda a: a.published_at or datetime.utcnow())
        canonical = sorted_articles[0]
        lat, lon, location_name = _cluster_centroid_location(cluster_articles)
        event = Event(
            canonical_title=canonical.title,
            summary=canonical.description,
            location_name=location_name,
            latitude=lat,
            longitude=lon,
            confidence_score=min(1.0, 0.4 + (len(cluster_articles) * 0.1)),
            first_seen_at=sorted_articles[0].published_at or datetime.utcnow(),
            last_updated_at=sorted_articles[-1].published_at or datetime.utcnow(),
        )
        session.add(event)
        session.flush()

        for article in cluster_articles:
            article.event_id = event.id
            linked_articles += 1

    session.commit()
    return {"events": len(clusters), "linked_articles": linked_articles}
