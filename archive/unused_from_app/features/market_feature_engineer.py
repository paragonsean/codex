from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class MarketFeatures:
    last_close: float
    ret_5d: float
    ret_21d: float
    ret_63d: float
    vol_21d_ann: float
    max_drawdown: float
    trend_50_200: str
    rsi_14: float
    volume_z_20: float


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.ewm(alpha=1 / period, adjust=False).mean()
    roll_down = down.ewm(alpha=1 / period, adjust=False).mean()
    rs = roll_up / (roll_down.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


def _max_drawdown(close: pd.Series) -> float:
    peak = close.cummax()
    dd = (close / peak) - 1.0
    return float(dd.min())


def _zscore_last(x: pd.Series, window: int) -> float:
    if len(x) < window + 1:
        return float("nan")
    w = x.iloc[-window:]
    mu = w.mean()
    sd = w.std(ddof=0)
    if sd == 0:
        return 0.0
    return float((x.iloc[-1] - mu) / sd)


class MarketFeatureEngineer:
    def compute(self, ticker: str, df: pd.DataFrame) -> Optional[MarketFeatures]:
        if df is None or df.empty:
            return None

        close = df["Close"].astype(float)
        vol = df["Volume"].astype(float) if "Volume" in df.columns else pd.Series(index=df.index, dtype=float)

        last_close = float(close.iloc[-1])

        def ret_n(n: int) -> float:
            if len(close) <= n:
                return float("nan")
            return float((close.iloc[-1] / close.iloc[-1 - n]) - 1.0)

        rets = close.pct_change().dropna()
        vol_21 = rets.tail(21).std(ddof=0) * math.sqrt(252) if len(rets) >= 21 else float("nan")

        ma50 = close.rolling(50).mean()
        ma200 = close.rolling(200).mean()

        trend = "unknown"
        if not np.isnan(ma50.iloc[-1]) and not np.isnan(ma200.iloc[-1]):
            trend = "bullish (50>200)" if ma50.iloc[-1] > ma200.iloc[-1] else "bearish (50<200)"

        rsi14 = float(_rsi(close, 14).iloc[-1])
        v_z = _zscore_last(vol, 20) if len(vol.dropna()) >= 21 else float("nan")

        return MarketFeatures(
            last_close=last_close,
            ret_5d=ret_n(5),
            ret_21d=ret_n(21),
            ret_63d=ret_n(63),
            vol_21d_ann=float(vol_21) if not np.isnan(vol_21) else float("nan"),
            max_drawdown=_max_drawdown(close),
            trend_50_200=trend,
            rsi_14=rsi14,
            volume_z_20=v_z,
        )
