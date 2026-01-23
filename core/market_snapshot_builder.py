from __future__ import annotations

from datetime import datetime, timezone

from core.market_snapshot import MarketSnapshot
from features.market_feature_engineer import MarketFeatureEngineer
from services.market_data_service import MarketDataService


class MarketSnapshotBuilder:
    def __init__(self):
        self.fetcher = MarketDataService()
        self.engineer = MarketFeatureEngineer()

    def build(self, ticker: str, days: int):
        df = self.fetcher.fetch_ohlcv(ticker, days)
        return self.build_from_df(ticker, df)

    def build_from_df(self, ticker: str, df):
        features = self.engineer.compute(ticker, df)
        if features is None:
            raise ValueError(f"No market data for ticker {ticker}")

        asof = df.index[-1]
        if not isinstance(asof, datetime):
            asof = datetime.now(timezone.utc)

        return MarketSnapshot(
            ticker=ticker,
            asof=asof.to_pydatetime() if hasattr(asof, "to_pydatetime") else asof,
            df=df,
            features=features,
        )
