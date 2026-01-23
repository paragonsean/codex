from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Config:
    lookback_days: int = 180
    max_headlines: int = 100  # Increased to populate 8 weeks of news metrics
    benchmark_ticker: str = "SOXX"
    
    opportunity_buy_threshold: float = 60.0
    sell_risk_trim_threshold: float = 60.0
    sell_risk_sell_threshold: float = 80.0
    
    max_position_pct: float = 0.15
    max_sector_pct: float = 0.40
    min_cash_buffer: float = 0.10
    
    output_dir: str = "reports"
    enable_alerts: bool = True
    as_of_date: Optional[datetime] = None  # For historical analysis - only use data up to this date
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> Config:
        return cls(**{k: v for k, v in config_dict.items() if k in cls.__annotations__})
