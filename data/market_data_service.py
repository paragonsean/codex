from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import pandas as pd
import yfinance as yf
import warnings

from domain.models import PriceSeries

warnings.filterwarnings("ignore", category=FutureWarning)
try:
    from pandas.errors import Pandas4Warning
    warnings.filterwarnings("ignore", category=Pandas4Warning)
except Exception:
    pass


class MarketDataService:
    def __init__(
        self,
        interval: str = "1d",
        auto_adjust: bool = False,
        progress: bool = False,
        threads: bool = False,
    ):
        self.interval = interval
        self.auto_adjust = auto_adjust
        self.progress = progress
        self.threads = threads

    def fetch_price_series(
        self,
        ticker: str,
        days: int,
        buffer_days: int = 10,
        as_of_date: Optional[datetime] = None,
    ) -> PriceSeries:
        # Use as_of_date if provided (for historical analysis), otherwise use current date
        end_date = as_of_date if as_of_date else datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days + buffer_days)

        df = yf.download(
            tickers=ticker,
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            interval=self.interval,
            auto_adjust=self.auto_adjust,
            progress=self.progress,
            threads=self.threads,
        )

        if df is None or df.empty:
            return PriceSeries(
                ticker=ticker,
                df=pd.DataFrame(),
                timezone="UTC",
                interval=self.interval,
            )

        df = self._normalize_ohlcv_df(df, ticker)
        df = df.sort_index()
        df = df.dropna(how="all")
        
        # Filter data to only include dates up to as_of_date (prevent future data leakage)
        if as_of_date:
            # Convert as_of_date to pandas Timestamp for proper comparison
            cutoff_date = pd.Timestamp(as_of_date)
            
            # Ensure timezone compatibility
            if df.index.tz is not None:
                # DataFrame has timezone, ensure cutoff_date matches
                if cutoff_date.tzinfo is None:
                    cutoff_date = cutoff_date.tz_localize(df.index.tz)
                else:
                    cutoff_date = cutoff_date.tz_convert(df.index.tz)
            else:
                # DataFrame has no timezone, remove timezone from cutoff_date
                if cutoff_date.tzinfo is not None:
                    cutoff_date = cutoff_date.tz_localize(None)
            
            df = df[df.index <= cutoff_date]

        tz_str = "UTC"
        if hasattr(df.index, "tz") and df.index.tz is not None:
            tz_str = str(df.index.tz)

        return PriceSeries(
            ticker=ticker,
            df=df,
            timezone=tz_str,
            interval=self.interval,
            metadata={"fetched_at": datetime.now(timezone.utc).isoformat()},
        )

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
