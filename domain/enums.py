from __future__ import annotations

from enum import Enum


class NewsCategory(str, Enum):
    EARNINGS = "earnings"
    GUIDANCE = "guidance"
    FINANCIAL = "financial"
    LEGAL = "legal"
    MERGERS = "mergers"
    OPERATIONS = "operations"
    PRODUCTS = "products"
    MARKET = "market"
    OTHER = "other"


class ActionType(str, Enum):
    BUY = "buy"
    HOLD = "hold"
    TRIM = "trim"
    SELL = "sell"
    HEDGE = "hedge"
    WATCH = "watch"


class RegimeLabel(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    ELEVATED = "elevated"
    UNKNOWN = "unknown"


class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
