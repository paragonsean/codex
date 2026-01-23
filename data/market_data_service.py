from __future__ import annotations

from dataclasses import dataclass
from datetime import timezone
from typing import Optional

import pandas as pd

from domain.models import PriceSeries
from services.market_data_service import MarketDataFetchConfig as LegacyMarketDataFetchConfig
from services.market_data_service import MarketDataService as LegacyMarketDataService


@dataclass(frozen=True)
class MarketDataFetchConfig:
    interval: str = "1d"
    auto_adjust: bool = False
    progress: bool = False
    threads: bool = False


class MarketDataService:
    """Domain-facing market data service.

    Phase 2 scaffolding: thin wrapper around existing services.market_data_service.MarketDataService.
    Returns domain.models.PriceSeries.
    """

    def __init__(self, config: Optional[MarketDataFetchConfig] = None):
        cfg = config or MarketDataFetchConfig()
        legacy_cfg = LegacyMarketDataFetchConfig(
            interval=cfg.interval,
            auto_adjust=cfg.auto_adjust,
            progress=cfg.progress,
            threads=cfg.threads,
        )
        self._legacy = LegacyMarketDataService(config=legacy_cfg)
        self.config = cfg

    def get_price_series(self, ticker: str, days: int, buffer_days: int = 10) -> PriceSeries:
        df = self._legacy.fetch_ohlcv(ticker, days, buffer_days=buffer_days)
        if df is None:
            df = pd.DataFrame()

        if not df.empty and hasattr(df.index, "tz") and df.index.tz is None:
            try:
                df.index = df.index.tz_localize(timezone.utc)
            except Exception:
                pass

        return PriceSeries(
            ticker=ticker,
            df=df,
            timezone="UTC" if (not df.empty and getattr(df.index, "tz", None) is not None) else None,
            interval=self.config.interval,
            metadata={"buffer_days": buffer_days},
        )
