from __future__ import annotations

from typing import Dict, List, Set

from domain.enums import NewsCategory
from domain.models import NewsEvent


POS_WORDS = {
    "beats", "beat", "surge", "soar", "record", "strong", "upgrade", "upgraded",
    "growth", "rally", "bullish", "profit", "profits", "margin", "margins",
    "accelerate", "accelerates", "expands", "expansion", "demand", "wins", "win",
    "partnership", "contract", "orders", "guidance raised", "raised guidance"
}

NEG_WORDS = {
    "miss", "misses", "plunge", "drop", "falls", "weak", "downgrade", "downgraded",
    "cut", "cuts", "lawsuit", "probe", "investigation", "warning", "bearish",
    "loss", "losses", "margin pressure", "inventory", "oversupply",
    "layoffs", "delay", "delays", "slowdown", "slows", "guidance cut"
}

CATEGORY_KEYWORDS = {
    NewsCategory.EARNINGS: {
        "earnings", "quarterly", "q1", "q2", "q3", "q4", "eps", "revenue", "profit",
        "loss", "beat", "miss", "guidance", "forecast", "estimate", "analyst"
    },
    NewsCategory.MERGERS: {
        "acquisition", "merger", "buyout", "takeover", "deal", "acquire", "purchase",
        "sell", "spinoff", "divest", "joint venture", "partnership"
    },
    NewsCategory.PRODUCTS: {
        "product", "launch", "release", "new", "chip", "processor", "gpu", "cpu",
        "memory", "storage", "hbm", "dram", "nand", "ssd", "datacenter", "ai", "ml"
    },
    NewsCategory.FINANCIAL: {
        "financing", "debt", "credit", "loan", "cash", "investment", "funding",
        "capital", "share", "stock", "dividend", "buyback", "offering"
    },
    NewsCategory.OPERATIONS: {
        "plant", "factory", "production", "manufacturing", "supply", "chain",
        "inventory", "operations", "facility", "expansion", "construction"
    },
    NewsCategory.LEGAL: {
        "lawsuit", "legal", "court", "judge", "ruling", "patent", "infringement",
        "settlement", "fine", "penalty", "regulation", "compliance"
    },
    NewsCategory.MARKET: {
        "market", "sector", "industry", "competition", "competitor", "share",
        "pricing", "demand", "supply", "trend", "outlook"
    },
}

HIGH_IMPACT_WORDS = {
    "breakthrough", "revolutionary", "landmark", "historic", "unprecedented",
    "major", "significant", "substantial", "massive", "huge", "blockbuster"
}


class NewsFeatures:
    @staticmethod
    def calculate_sentiment(text: str) -> float:
        text_lower = text.lower()
        pos_count = sum(1 for word in POS_WORDS if word in text_lower)
        neg_count = sum(1 for word in NEG_WORDS if word in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0
        
        return (pos_count - neg_count) / total

    @staticmethod
    def categorize_news(text: str) -> List[NewsCategory]:
        text_lower = text.lower()
        categories = []
        
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                categories.append(category)
        
        return categories if categories else [NewsCategory.OTHER]

    @staticmethod
    def calculate_impact(text: str) -> int:
        text_lower = text.lower()
        
        if any(word in text_lower for word in HIGH_IMPACT_WORDS):
            return 2
        
        earnings_keywords = ["earnings", "revenue", "guidance", "forecast"]
        if any(kw in text_lower for kw in earnings_keywords):
            return 1
        
        return 0

    @staticmethod
    def calculate_quality(text: str, source: str | None) -> float:
        score = 0.5
        
        if source:
            high_quality_sources = {
                "reuters", "bloomberg", "wall street journal", "financial times",
                "associated press", "cnbc", "marketwatch", "yahoo finance"
            }
            medium_quality_sources = {
                "seeking alpha", "investor's business daily", "the motley fool",
                "benzinga", "business wire"
            }
            
            source_lower = source.lower()
            if any(hqs in source_lower for hqs in high_quality_sources):
                score += 0.3
            elif any(mqs in source_lower for mqs in medium_quality_sources):
                score += 0.15
        
        if len(text.split()) >= 8:
            score += 0.1
        
        if any(fin_word in text.lower() for fin_word in ["earnings", "revenue", "profit", "guidance"]):
            score += 0.1
        
        clickbait_indicators = ["!", "??", "shocking", "you won't believe", "revealed"]
        if any(indicator in text.lower() for indicator in clickbait_indicators):
            score -= 0.2
        
        return max(0.0, min(1.0, score))

    @staticmethod
    def enrich_events(events: List[NewsEvent]) -> List[NewsEvent]:
        enriched = []
        
        for event in events:
            sentiment = NewsFeatures.calculate_sentiment(event.title)
            categories = NewsFeatures.categorize_news(event.title)
            impact = NewsFeatures.calculate_impact(event.title)
            quality = NewsFeatures.calculate_quality(event.title, event.source)
            
            enriched_event = NewsEvent(
                ticker=event.ticker,
                title=event.title,
                url=event.url,
                source=event.source,
                published_ts=event.published_ts,
                sentiment=sentiment,
                categories=categories,
                quality=quality,
                impact=impact,
                entities=event.entities,
                raw=event.raw,
            )
            enriched.append(enriched_event)
        
        return enriched

    @staticmethod
    def aggregate_features(events: List[NewsEvent]) -> Dict[str, float]:
        if not events:
            return {
                "total_count": 0,
                "avg_sentiment": 0.0,
                "avg_quality": 0.0,
                "avg_impact": 0.0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
            }
        
        sentiments = [e.sentiment for e in events]
        qualities = [e.quality for e in events]
        impacts = [e.impact for e in events]
        
        return {
            "total_count": len(events),
            "avg_sentiment": sum(sentiments) / len(sentiments),
            "avg_quality": sum(qualities) / len(qualities),
            "avg_impact": sum(impacts) / len(impacts),
            "positive_count": sum(1 for s in sentiments if s > 0.3),
            "negative_count": sum(1 for s in sentiments if s < -0.3),
            "neutral_count": sum(1 for s in sentiments if -0.3 <= s <= 0.3),
        }
