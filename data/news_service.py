from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import List, Optional

import feedparser
import requests

from domain.enums import NewsCategory
from domain.models import NewsEvent


class NewsService:
    def __init__(self, timeout: int = 20):
        self.timeout = timeout

    def fetch_news_events(
        self,
        ticker: str,
        max_items: int = 25,
        extra_queries: Optional[List[str]] = None,
        as_of_date: Optional[datetime] = None,
    ) -> List[NewsEvent]:
        queries = [ticker]
        if extra_queries:
            queries.extend(extra_queries)

        events: List[NewsEvent] = []
        seen_titles = set()

        for q in queries:
            url = self._google_news_rss_url(q)
            feed = feedparser.parse(url)

            for entry in feed.entries[: max_items * 2]:
                title = getattr(entry, "title", "").strip()
                if not title or title in seen_titles:
                    continue
                seen_titles.add(title)

                link = getattr(entry, "link", "")
                published_ts = self._parse_published_timestamp(entry)
                source = self._extract_source(entry)

                events.append(
                    NewsEvent(
                        ticker=ticker,
                        title=title,
                        url=link,
                        source=source,
                        published_ts=published_ts,
                        sentiment=0.0,
                        categories=None,
                        quality=0.0,
                        impact=0,
                        entities=None,
                        raw={
                            "published_raw": getattr(entry, "published", ""),
                        },
                    )
                )

        # Filter out news published after as_of_date (prevent future data leakage)
        if as_of_date:
            cutoff_date = as_of_date
            if cutoff_date.tzinfo is None:
                cutoff_date = cutoff_date.replace(tzinfo=timezone.utc)
            events = [e for e in events if e.published_ts <= cutoff_date]
        
        events.sort(key=lambda e: e.published_ts, reverse=True)
        return events[:max_items]

    def _google_news_rss_url(self, ticker_or_query: str) -> str:
        q = requests.utils.quote(ticker_or_query)
        return f"https://news.google.com/rss/search?q={q}%20when:7d&hl=en-US&gl=US&ceid=US:en"

    def _parse_published_timestamp(self, entry) -> datetime:
        if getattr(entry, "published_parsed", None):
            return datetime.fromtimestamp(
                time.mktime(entry.published_parsed), tz=timezone.utc
            )
        if getattr(entry, "updated_parsed", None):
            return datetime.fromtimestamp(
                time.mktime(entry.updated_parsed), tz=timezone.utc
            )
        return datetime.now(timezone.utc)

    def _extract_source(self, entry) -> Optional[str]:
        if hasattr(entry, "source") and entry.source:
            return getattr(entry.source, "title", None)
        return None
