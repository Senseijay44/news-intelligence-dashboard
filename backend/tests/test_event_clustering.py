from datetime import datetime, timedelta

from app.db.models import Article
from app.services.event import ClusterConfig, _to_signal, cluster_article_signals


def _article(title: str, description: str, published_at: datetime, url_suffix: str) -> Article:
    return Article(
        title=title,
        description=description,
        url=f"https://example.com/{url_suffix}",
        published_at=published_at,
    )


def test_clusters_articles_with_similar_text_time_and_entities():
    now = datetime(2026, 3, 25, 12, 0, 0)
    a1 = _article(
        "Earthquake strikes San Francisco",
        "Officials in California report tremors near Bay Area",
        now,
        "a1",
    )
    a2 = _article(
        "San Francisco earthquake causes damage",
        "California emergency teams respond in the Bay Area",
        now + timedelta(hours=2),
        "a2",
    )

    clusters = cluster_article_signals([_to_signal(a1), _to_signal(a2)], ClusterConfig(similarity_threshold=0.35))

    assert len(clusters) == 1
    assert len(clusters[0]) == 2


def test_separates_articles_when_time_far_apart():
    now = datetime(2026, 3, 25, 12, 0, 0)
    a1 = _article(
        "Port workers strike in Marseille",
        "Union leaders announce week-long protest",
        now,
        "b1",
    )
    a2 = _article(
        "Port workers strike in Marseille",
        "Union leaders announce week-long protest",
        now + timedelta(days=8),
        "b2",
    )

    clusters = cluster_article_signals([_to_signal(a1), _to_signal(a2)], ClusterConfig(similarity_threshold=0.80))

    assert len(clusters) == 2


def test_separates_articles_with_no_entity_or_topic_overlap():
    now = datetime(2026, 3, 25, 12, 0, 0)
    a1 = _article(
        "NASA launches new weather satellite",
        "Mission control confirms successful deployment",
        now,
        "c1",
    )
    a2 = _article(
        "Central bank raises interest rates",
        "Investors react to policy shift",
        now + timedelta(hours=1),
        "c2",
    )

    clusters = cluster_article_signals([_to_signal(a1), _to_signal(a2)], ClusterConfig(similarity_threshold=0.30))

    assert len(clusters) == 2
