from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional, Sequence

from domain.enums import NewsCategory
from domain.models import NewsEvent
from news import Headline, fetch_headlines_for_ticker


def _parse_iso(ts: Optional[str]) -> datetime:
    if not ts:
        return datetime.now(timezone.utc)
    try:
        # `news.parse_published` produces ISO strings, typically with timezone
        return datetime.fromisoformat(ts)
    except Exception:
        return datetime.now(timezone.utc)


def _map_categories(cats) -> Sequence[NewsCategory]:
    out: List[NewsCategory] = []
    if isinstance(cats, dict):
        keys = cats.keys()
    elif isinstance(cats, (list, tuple, set)):
        keys = cats
    else:
        keys = []

    for k in keys:
        try:
            out.append(NewsCategory(str(k)))
        except Exception:
            out.append(NewsCategory.OTHER)
    return out


class NewsService:
    """Domain-facing news service.

    Phase 2 scaffolding: thin wrapper around existing `news.fetch_headlines_for_ticker`.
    Returns domain.models.NewsEvent.
    """

    def get_news_events(
        self,
        ticker: str,
        since_days: int = 7,
        max_items: int = 25,
        keywords: Optional[List[str]] = None,
        extra_queries: Optional[List[str]] = None,
    ) -> List[NewsEvent]:
        keywords = keywords or []
        headlines: List[Headline] = fetch_headlines_for_ticker(
            ticker=ticker,
            max_items=max_items,
            keywords=keywords,
            extra_queries=extra_queries,
        )

        events: List[NewsEvent] = []
        for h in headlines:
            events.append(
                NewsEvent(
                    ticker=h.ticker,
                    title=h.title,
                    url=h.link,
                    source=h.source,
                    published_ts=_parse_iso(h.published_ts),
                    sentiment=float(h.sentiment),
                    categories=_map_categories(h.categories),
                    quality=float(h.quality),
                    impact=int(h.impact),
                    entities=h.entities,
                    raw={
                        "published": h.published,
                        "published_ts": h.published_ts,
                        "keyword_score": h.keyword_score,
                    },
                )
            )

        return events
