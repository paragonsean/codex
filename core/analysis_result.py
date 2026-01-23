from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from core.market_snapshot import MarketSnapshot


@dataclass(frozen=True)
class AnalysisResult:
    ticker: str
    timestamp: str
    market_snapshot: MarketSnapshot
    market_data: Any
    dual_scores: Any
    cycle_analysis: Any
    good_news_analysis: Any
    recommendation: Any
    news_catalysts: Optional[List[Any]] = None
    news_catalysts_data: Optional[Dict[str, Any]] = None
    data_gates: Optional[Dict[str, Any]] = None
    news_gates: Optional[Dict[str, Any]] = None
