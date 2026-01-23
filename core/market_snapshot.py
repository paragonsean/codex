from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from features.market_feature_engineer import MarketFeatures


@dataclass(frozen=True)
class MarketSnapshot:
    ticker: str
    asof: datetime
    df: pd.DataFrame
    features: MarketFeatures
