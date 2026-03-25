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
CLAUSE_SPLIT_RE = re.compile(r"\s*(?:[.;!?]|\s+-\s+|\s+and\s+)\s*")

ATTRIBUTION_RE = re.compile(
    r"\b(said|says|according to|told|announced|reported by|claimed|stated)\b",
    flags=re.IGNORECASE,
)
ANALYSIS_RE = re.compile(
    r"\b(suggests|suggested|indicates|appears|likely|because|therefore|signals|implies)\b",
    flags=re.IGNORECASE,
)
OPINION_RE = re.compile(
    r"\b(criticized|praised|outrageous|unacceptable|disaster|success|failure|bias|propaganda)\b",
    flags=re.IGNORECASE,
)
PREDICTION_RE = re.compile(
    r"\b(will|would|expected|forecast|projected|could|may|might|anticipates)\b",
    flags=re.IGNORECASE,
)


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


@dataclass
class ExtractedClaim:
    text: str
    claim_type: str
    article: Article


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


def _extract_atomic_claims(article: Article) -> list[str]:
    fragments: list[str] = []
    for text in (article.title, article.description, article.body):
        if not text:
            continue
        for raw in CLAUSE_SPLIT_RE.split(text):
            claim = raw.strip()
            if len(claim) >= 25:
                fragments.append(claim)
    deduped = list(dict.fromkeys(fragments))
    return deduped


def _classify_claim(claim: str) -> str:
    if ATTRIBUTION_RE.search(claim):
        return "attributed statement"
    if PREDICTION_RE.search(claim):
        return "prediction"
    if ANALYSIS_RE.search(claim):
        return "analysis/inference"
    if OPINION_RE.search(claim):
        return "opinion/framing"
    return "reported fact"


def _normalize_claim_text(claim: str) -> str:
    return " ".join(_tokenize(claim))


def _group_claims_by_text(claims: list[ExtractedClaim]) -> dict[str, list[ExtractedClaim]]:
    grouped: dict[str, list[ExtractedClaim]] = {}
    for claim in claims:
        key = _normalize_claim_text(claim.text)
        grouped.setdefault(key, []).append(claim)
    return grouped


def build_event_neutral_summary(event: Event, articles: Sequence[Article]) -> dict:
    extracted: list[ExtractedClaim] = []
    for article in articles:
        for claim in _extract_atomic_claims(article):
            extracted.append(ExtractedClaim(text=claim, claim_type=_classify_claim(claim), article=article))

    grouped = _group_claims_by_text(extracted)
    core_facts: list[dict] = []
    disputed_points: list[dict] = []
    uncertainty: list[str] = []

    for group in grouped.values():
        if not group:
            continue
        first = group[0]
        unique_sources = {
            item.article.id: item.article
            for item in group
            if item.article.id is not None
        }
        source_items = [
            {
                "article_id": article.id,
                "title": article.title,
                "url": article.url,
                "published_at": article.published_at,
            }
            for article in unique_sources.values()
            if article.id is not None
        ]
        claim_payload = {
            "text": first.text,
            "claim_type": first.claim_type,
            "source_count": len(unique_sources),
            "sources": source_items,
        }

        claim_types = {item.claim_type for item in group}
        if len(claim_types) > 1:
            disputed_points.append(claim_payload)
        elif first.claim_type in {"reported fact", "attributed statement"} and len(unique_sources) >= 2:
            core_facts.append(claim_payload)
        elif first.claim_type in {"analysis/inference", "opinion/framing", "prediction"}:
            uncertainty.append(f"{first.claim_type}: {first.text}")
        elif len(unique_sources) == 1:
            uncertainty.append(f"single source: {first.text}")

    core_facts = sorted(core_facts, key=lambda c: (-c["source_count"], c["text"]))[:10]
    disputed_points = sorted(disputed_points, key=lambda c: (-c["source_count"], c["text"]))[:10]
    uncertainty = uncertainty[:10]

    return {
        "event_id": event.id,
        "core_facts": core_facts,
        "disputed_points": disputed_points,
        "uncertainty": uncertainty,
        "source_count": len({a.id for a in articles if a.id is not None}),
    }




def compute_confidence_score(
    *,
    article_count: int,
    source_count: int,
    newest_article_at: datetime | None,
    oldest_article_at: datetime | None = None,
) -> float:
    article_signal = min(1.0, article_count / 6)
    source_signal = min(1.0, source_count / 4)

    recency_signal = 0.0
    if newest_article_at:
        hours_old = max(0.0, (datetime.utcnow() - newest_article_at).total_seconds() / 3600)
        recency_signal = max(0.0, 1.0 - (hours_old / 72))

    consistency_signal = 0.5
    if oldest_article_at and newest_article_at and newest_article_at >= oldest_article_at:
        span_hours = (newest_article_at - oldest_article_at).total_seconds() / 3600
        consistency_signal = max(0.0, 1.0 - min(span_hours, 168) / 168)

    score = (
        (article_signal * 0.35)
        + (source_signal * 0.35)
        + (recency_signal * 0.2)
        + (consistency_signal * 0.1)
    )
    return max(0.05, min(0.99, round(score, 3)))

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
            confidence_score=compute_confidence_score(
                article_count=len(cluster_articles),
                source_count=len({a.source_id for a in cluster_articles if a.source_id is not None}),
                newest_article_at=sorted_articles[-1].published_at,
                oldest_article_at=sorted_articles[0].published_at,
            ),
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
