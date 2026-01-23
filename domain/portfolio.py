from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Position:
    ticker: str
    shares: float
    cost_basis: float


@dataclass(frozen=True)
class Portfolio:
    name: str
    positions: List[Position]


@dataclass(frozen=True)
class PortfolioContext:
    asof: Optional[datetime] = None
    cash: Optional[float] = None
    total_value: Optional[float] = None
    sector_weights: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, Any]] = None
