from datetime import datetime

from app.db.models import Article, Event
from app.services.event import build_event_neutral_summary


def _article(article_id: int, title: str, description: str, url_suffix: str) -> Article:
    return Article(
        id=article_id,
        title=title,
        description=description,
        url=f"https://example.com/{url_suffix}",
        published_at=datetime(2026, 3, 25, 12, 0, 0),
        event_id=1,
    )


def test_builds_core_facts_with_source_links():
    event = Event(id=1, canonical_title="Test event")
    a1 = _article(1, "Bridge collapses in central city", "Police said two lanes are closed", "a1")
    a2 = _article(2, "Bridge collapses in central city", "Witnesses reported major traffic delays", "a2")

    summary = build_event_neutral_summary(event, [a1, a2])

    assert summary["source_count"] == 2
    assert any(claim["text"] == "Bridge collapses in central city" for claim in summary["core_facts"])

    matching = [claim for claim in summary["core_facts"] if claim["text"] == "Bridge collapses in central city"][0]
    assert matching["source_count"] == 2
    assert {source["url"] for source in matching["sources"]} == {a1.url, a2.url}


def test_captures_uncertainty_for_predictions_and_single_source_claims():
    event = Event(id=1, canonical_title="Test event")
    a1 = _article(1, "Officials say inflation will fall next quarter", "Analysts suggest demand is cooling", "a1")

    summary = build_event_neutral_summary(event, [a1])

    assert summary["source_count"] == 1
    assert any("prediction" in item for item in summary["uncertainty"])
