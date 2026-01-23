from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Literal, Optional
import pytz


SessionType = Literal["pre", "regular", "after", "weekend", "holiday"]


class MarketCalendar:
    def __init__(self, timezone: str = "America/New_York"):
        self.tz = pytz.timezone(timezone)
        self.market_open = time(9, 30)
        self.market_close = time(16, 0)
        self.pre_market_start = time(4, 0)
        self.after_market_end = time(20, 0)

    def to_et(self, dt: datetime) -> datetime:
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        return dt.astimezone(self.tz)

    def classify_session(self, dt: datetime) -> SessionType:
        et_dt = self.to_et(dt)
        
        if et_dt.weekday() >= 5:
            return "weekend"
        
        t = et_dt.time()
        
        if self.pre_market_start <= t < self.market_open:
            return "pre"
        elif self.market_open <= t < self.market_close:
            return "regular"
        elif self.market_close <= t < self.after_market_end:
            return "after"
        else:
            return "weekend"

    def get_anchor_date(self, dt: datetime) -> datetime:
        et_dt = self.to_et(dt)
        session = self.classify_session(dt)
        
        if session == "pre":
            return et_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        elif session in ("regular", "after"):
            return et_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        elif session == "weekend":
            days_until_monday = (7 - et_dt.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 1
            next_trading_day = et_dt + timedelta(days=days_until_monday)
            return next_trading_day.replace(hour=0, minute=0, second=0, microsecond=0)
        
        return et_dt.replace(hour=0, minute=0, second=0, microsecond=0)

    def next_trading_day(self, dt: datetime, days: int = 1) -> Optional[datetime]:
        current = self.to_et(dt).replace(hour=0, minute=0, second=0, microsecond=0)
        count = 0
        
        while count < days:
            current += timedelta(days=1)
            if current.weekday() < 5:
                count += 1
        
        return current if count == days else None
