from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import pandas as pd
import yfinance as yf
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
try:
    from pandas.errors import Pandas4Warning

    warnings.filterwarnings("ignore", category=Pandas4Warning)
except Exception:
    pass


@dataclass(frozen=True)
class MarketDataFetchConfig:
    interval: str = "1d"
    auto_adjust: bool = False
    progress: bool = False
    threads: bool = False


class MarketDataService:
    def __init__(self, config: Optional[MarketDataFetchConfig] = None):
        self.config = config or MarketDataFetchConfig()

    def fetch_ohlcv(self, ticker: str, days: int, buffer_days: int = 10) -> pd.DataFrame:
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days + buffer_days)

        df = yf.download(
            tickers=ticker,
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            interval=self.config.interval,
            auto_adjust=self.config.auto_adjust,
            progress=self.config.progress,
            threads=self.config.threads,
        )

        if df is None or df.empty:
            return pd.DataFrame()

        df = self._normalize_ohlcv_df(df, ticker)
        df = df.sort_index()
        df = df.dropna(how="all")
        return df

    def _normalize_ohlcv_df(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        if not isinstance(df.columns, pd.MultiIndex):
            return df

        try:
            level_values = df.columns.get_level_values(1)
            if ticker in level_values.tolist():
                df = df.xs(ticker, axis=1, level=1)
        except Exception:
            pass

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        return df
