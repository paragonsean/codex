from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd

from domain.enums import ActionType, Confidence, NewsCategory, RegimeLabel


@dataclass(frozen=True)
class NewsEvent:
    ticker: str
    title: str
    url: str
    source: Optional[str]
    published_ts: datetime
    sentiment: float = 0.0
    categories: Optional[Sequence[NewsCategory]] = None
    quality: float = 0.0
    impact: int = 0
    entities: Optional[Dict[str, Any]] = None
    raw: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class PriceSeries:
    ticker: str
    df: pd.DataFrame
    timezone: Optional[str] = None
    interval: str = "1d"
    metadata: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class ReactionRecord:
    event: NewsEvent
    session: str
    anchor_date: datetime
    forward_returns: Dict[str, Optional[float]]
    excess_returns: Optional[Dict[str, Optional[float]]] = None
    verdict: Optional[str] = None
    mapping_reason: Optional[str] = None


@dataclass(frozen=True)
class FeatureVector:
    """
    Immutable feature vector containing all computed features for a ticker.
    Separates feature computation from scoring logic.
    """
    ticker: str
    asof: datetime
    regime: RegimeLabel = RegimeLabel.UNKNOWN
    technical: Optional['TechnicalFeatures'] = None  # from features.technical_features
    news: Optional['NewsFeatures'] = None  # from features.news_features
    reactions: Optional[List[ReactionRecord]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class SignalScore:
    ticker: str
    opportunity: float
    sell_risk: float
    bias: str
    confidence: Confidence = Confidence.MEDIUM
    contributors: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class Recommendation:
    ticker: str
    action: ActionType
    confidence: float
    reasons: List[str]
    tier: Optional[str] = None
    urgency: Optional[str] = None
    key_levels: Optional[Dict[str, Any]] = None
    next_review_date: Optional[str] = None
    position_sizing: Optional[Dict[str, Any]] = None
    hedge_suggestions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class RunRequest:
    tickers: List[str]
    days: int = 180
    max_headlines: int = 25
    benchmark_ticker: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class RunResult:
    request: RunRequest
    created_at: datetime
    results: List[Any]
    errors: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None
