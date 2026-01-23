from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from domain.enums import RegimeLabel
from domain.models import FeatureVector, NewsEvent, PriceSeries, ReactionRecord
from features.market_calendar import MarketCalendar
from features.news_features import NewsFeatures
from features.reaction_engine import ReactionEngine
from features.technical_indicators import TechnicalIndicators


class FeaturePipeline:
    def __init__(
        self,
        calendar: Optional[MarketCalendar] = None,
        reaction_engine: Optional[ReactionEngine] = None,
    ):
        self.calendar = calendar or MarketCalendar()
        self.reaction_engine = reaction_engine or ReactionEngine(calendar=self.calendar)

    def build_feature_vector(
        self,
        ticker: str,
        price_series: PriceSeries,
        news_events: List[NewsEvent],
        benchmark_series: Optional[PriceSeries] = None,
        asof: Optional[datetime] = None,
    ) -> FeatureVector:
        asof = asof or datetime.now()
        
        technical = self._compute_technical_features(price_series)
        
        enriched_events = NewsFeatures.enrich_events(news_events)
        news = NewsFeatures.aggregate_features(enriched_events)
        
        reactions = self.reaction_engine.compute_reactions(
            enriched_events, price_series, benchmark_series
        )
        
        regime = self._classify_regime(technical)
        
        return FeatureVector(
            ticker=ticker,
            asof=asof,
            regime=regime,
            technical=technical,
            news=news,
            reactions=reactions,
            metadata={
                "price_series_length": len(price_series.df),
                "news_events_count": len(news_events),
                "reactions_count": len(reactions),
            },
        )

    def _compute_technical_features(self, price_series: PriceSeries) -> Dict[str, float]:
        if price_series.df.empty:
            return {}
        
        return TechnicalIndicators.calculate_all_indicators(price_series.df)

    def _classify_regime(self, technical: Dict[str, float]) -> RegimeLabel:
        vol_20d = technical.get("volatility_20d", 0.0)
        
        if vol_20d < 0.2:
            return RegimeLabel.LOW
        elif vol_20d < 0.35:
            return RegimeLabel.NORMAL
        elif vol_20d < 0.5:
            return RegimeLabel.ELEVATED
        else:
            return RegimeLabel.HIGH
