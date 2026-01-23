from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd

from domain.models import NewsEvent, PriceSeries, ReactionRecord
from features.market_calendar import MarketCalendar


class ReactionEngine:
    def __init__(
        self,
        calendar: Optional[MarketCalendar] = None,
        windows: Optional[List[str]] = None,
    ):
        self.calendar = calendar or MarketCalendar()
        self.windows = windows or ["0_close", "1d", "3d", "5d"]

    def compute_reactions(
        self,
        events: List[NewsEvent],
        price_series: PriceSeries,
        benchmark_series: Optional[PriceSeries] = None,
    ) -> List[ReactionRecord]:
        records = []
        
        for event in events:
            record = self._compute_single_reaction(
                event, price_series, benchmark_series
            )
            records.append(record)
        
        return records

    def _compute_single_reaction(
        self,
        event: NewsEvent,
        price_series: PriceSeries,
        benchmark_series: Optional[PriceSeries],
    ) -> ReactionRecord:
        session = self.calendar.classify_session(event.published_ts)
        anchor_date = self.calendar.get_anchor_date(event.published_ts)
        
        forward_returns = self._compute_forward_returns(
            anchor_date, price_series.df
        )
        
        excess_returns = None
        if benchmark_series is not None and not benchmark_series.df.empty:
            excess_returns = self._compute_excess_returns(
                anchor_date, price_series.df, benchmark_series.df
            )
        
        verdict = self._compute_verdict(forward_returns, event.sentiment)
        mapping_reason = self._get_mapping_reason(forward_returns)
        
        return ReactionRecord(
            event=event,
            session=session,
            anchor_date=anchor_date,
            forward_returns=forward_returns,
            excess_returns=excess_returns,
            verdict=verdict,
            mapping_reason=mapping_reason,
        )

    def _compute_forward_returns(
        self, anchor_date: datetime, df: pd.DataFrame
    ) -> Dict[str, Optional[float]]:
        if df.empty:
            return {w: None for w in self.windows}
        
        df_sorted = df.sort_index()
        anchor_date_only = anchor_date.date()
        
        returns = {}
        
        for window in self.windows:
            if window == "0_close":
                returns[window] = self._get_same_day_return(
                    anchor_date_only, df_sorted
                )
            elif window.endswith("d"):
                try:
                    days = int(window[:-1])
                    returns[window] = self._get_n_day_return(
                        anchor_date_only, days, df_sorted
                    )
                except ValueError:
                    returns[window] = None
            else:
                returns[window] = None
        
        return returns

    def _get_same_day_return(
        self, anchor_date, df: pd.DataFrame
    ) -> Optional[float]:
        try:
            anchor_idx = pd.Timestamp(anchor_date)
            if anchor_idx not in df.index:
                return None
            
            close_price = df.loc[anchor_idx, "Close"]
            open_price = df.loc[anchor_idx, "Open"]
            
            if pd.isna(close_price) or pd.isna(open_price) or open_price == 0:
                return None
            
            return float((close_price - open_price) / open_price)
        except (KeyError, IndexError, TypeError):
            return None

    def _get_n_day_return(
        self, anchor_date, days: int, df: pd.DataFrame
    ) -> Optional[float]:
        try:
            anchor_idx = pd.Timestamp(anchor_date)
            if anchor_idx not in df.index:
                return None
            
            anchor_loc = df.index.get_loc(anchor_idx)
            target_loc = anchor_loc + days
            
            if target_loc >= len(df):
                return None
            
            anchor_close = df.iloc[anchor_loc]["Close"]
            target_close = df.iloc[target_loc]["Close"]
            
            if pd.isna(anchor_close) or pd.isna(target_close) or anchor_close == 0:
                return None
            
            return float((target_close - anchor_close) / anchor_close)
        except (KeyError, IndexError, TypeError):
            return None

    def _compute_excess_returns(
        self, anchor_date: datetime, df: pd.DataFrame, benchmark_df: pd.DataFrame
    ) -> Dict[str, Optional[float]]:
        stock_returns = self._compute_forward_returns(anchor_date, df)
        benchmark_returns = self._compute_forward_returns(anchor_date, benchmark_df)
        
        excess = {}
        for window in self.windows:
            stock_ret = stock_returns.get(window)
            bench_ret = benchmark_returns.get(window)
            
            if stock_ret is not None and bench_ret is not None:
                excess[window] = stock_ret - bench_ret
            else:
                excess[window] = None
        
        return excess

    def _compute_verdict(
        self, forward_returns: Dict[str, Optional[float]], sentiment: float
    ) -> Optional[str]:
        one_day = forward_returns.get("1d")
        
        if one_day is None:
            return None
        
        threshold = 0.02
        
        if sentiment > 0.5:
            return "Worked" if one_day > threshold else "Failed"
        elif sentiment < -0.5:
            return "Worked" if one_day < -threshold else "Failed"
        else:
            return "Absorbed" if abs(one_day) < threshold else "Reacted"

    def _get_mapping_reason(
        self, forward_returns: Dict[str, Optional[float]]
    ) -> Optional[str]:
        if all(v is None for v in forward_returns.values()):
            return "No price data available for anchor date"
        
        missing = [w for w, v in forward_returns.items() if v is None]
        if missing:
            return f"Incomplete data for windows: {', '.join(missing)}"
        
        return None
