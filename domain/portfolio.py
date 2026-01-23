from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class BucketType(Enum):
    """Semiconductor industry buckets for portfolio segmentation."""
    MEMORY = "Memory"
    EQUIPMENT = "Equipment"
    EDA = "EDA"
    ANALOG = "Analog"
    FOUNDRY = "Foundry"
    POWER = "Power"
    SPECULATIVE = "Speculative"
    CASH = "Cash"


class ProfileType(Enum):
    """Stock profile types for cycle behavior."""
    MEMORY = "memory"
    EQUIPMENT = "equipment"
    EDA = "eda"
    ANALOG = "analog"
    FOUNDRY = "foundry"
    POWER = "power"


class CyclePhase(Enum):
    """Cycle phase classifications."""
    EARLY = "EARLY"
    MID = "MID"
    LATE = "LATE"
    PEAKING = "PEAKING"
    DOWNTURN = "DOWNTURN"


class PortfolioMode(Enum):
    """Portfolio positioning modes based on cycle risk."""
    OFFENSE = "OFFENSE"
    BALANCED = "BALANCED"
    DEFENSE = "DEFENSE"


@dataclass(frozen=True)
class Position:
    ticker: str
    shares: float
    cost_basis: float


@dataclass(frozen=True)
class Portfolio:
    name: str
    positions: List[Position]


@dataclass(frozen=True)
class PortfolioContext:
    asof: Optional[datetime] = None
    cash: Optional[float] = None
    total_value: Optional[float] = None
    sector_weights: Optional[Dict[str, float]] = None


@dataclass
class PositionInput:
    """Input data for a portfolio position with cycle analysis."""
    ticker: str
    market_value: float
    weight: float  # market_value / total_portfolio_value
    bucket: BucketType
    profile: ProfileType
    story_tags: List[str]  # e.g., ["AI_Compute", "Memory_Pricing"]


@dataclass
class StockCycleAnalysis:
    """Cycle analysis results for an individual stock."""
    ticker: str
    risk_total: float  # 0-100
    opportunity_total: float  # 0-100
    cycle_pressure: float  # risk - opportunity
    phase: CyclePhase
    transition_risk: float  # 0-100
    data_quality_ok: bool
    critical_signals_fired: List[str]  # e.g., ["RELATIVE_STRENGTH_VS_SOX", "GOOD_NEWS_EFFECTIVENESS"]


@dataclass
class BucketAnalysis:
    """Aggregated cycle analysis for a portfolio bucket."""
    bucket: BucketType
    weight: float  # total weight in portfolio
    target_max: float  # policy limit
    overage: float  # max(0, weight - target_max)
    
    # Bucket-level metrics
    weighted_pressure: float  # sum(w_i * p_i)
    phase_score: float  # weighted average of phase scores
    phase: CyclePhase  # derived from phase_score
    
    # Risk components
    base_risk: float  # clip(2 * weighted_pressure, 0, 100)
    critical_breadth: float  # fraction of weight with critical signals
    risk_multiplier: float  # 1 + 0.8 * critical_breadth
    transition_risk: float  # clip(base_risk * multiplier, 0, 100)
    
    # Top contributors
    top_contributors: List[Dict[str, Any]]  # [{ticker, weight, pressure, contribution}]


@dataclass
class PortfolioRiskAnalysis:
    """Complete portfolio-level cycle risk analysis."""
    total_value: float
    
    # Portfolio cycle metrics
    portfolio_pressure: float  # weighted average cycle pressure
    portfolio_phase: CyclePhase
    
    # Risk components (0-100 each)
    pressure_risk: float  # clip(2 * portfolio_pressure, 0, 100)
    phase_concentration_risk: float  # clip(250 * peaking_weight, 0, 100)
    bucket_concentration_risk: float  # clip(200 * sum(overages), 0, 100)
    story_concentration_risk: float  # clip(200 * max_story_weight, 0, 100)
    
    # Final transition risk (0-100)
    transition_risk: float  # weighted blend of components
    
    # Portfolio mode
    mode: PortfolioMode
    
    # Bucket analyses
    buckets: Dict[BucketType, BucketAnalysis]
    
    # Story concentration
    story_weights: Dict[str, float]  # {story_tag: total_weight}
    max_story_concentration: float
    
    # Peaking metrics
    peaking_weight: float  # weight in PEAKING or DOWNTURN
    peaking_tickers: List[str]


@dataclass
class BucketAction:
    """Recommended action for a bucket."""
    bucket: BucketType
    action_type: str  # "REDUCE", "ROTATE", "HOLD", "ADD"
    current_weight: float
    target_weight: float
    urgency: str  # "HIGH", "MEDIUM", "LOW"
    reason: str
    timeframe: str  # e.g., "2-4 weeks"
    

@dataclass
class PositionAction:
    """Recommended action for an individual position."""
    ticker: str
    action_type: str  # "TRIM", "HOLD", "HEDGE", "ADD", "EXIT"
    current_weight: float
    target_weight: Optional[float]
    priority: int  # 1-5, 1 = highest
    reason: str
    contribution_to_risk: float  # weight * cycle_pressure
    metadata: Optional[Dict[str, Any]] = None


# Phase score mapping for numeric calculations
PHASE_SCORES = {
    CyclePhase.EARLY: -10,
    CyclePhase.MID: 0,
    CyclePhase.LATE: 15,
    CyclePhase.PEAKING: 30,
    CyclePhase.DOWNTURN: 45,
}

# Reverse mapping: score ranges to phases
PHASE_THRESHOLDS = [
    (-float('inf'), -5, CyclePhase.EARLY),
    (-5, 7.5, CyclePhase.MID),
    (7.5, 22.5, CyclePhase.LATE),
    (22.5, 37.5, CyclePhase.PEAKING),
    (37.5, float('inf'), CyclePhase.DOWNTURN),
]

# Default bucket limits (policy)
DEFAULT_BUCKET_LIMITS = {
    BucketType.MEMORY: 0.18,  # 18% max
    BucketType.EQUIPMENT: 0.25,  # 25% max
    BucketType.EDA: 0.15,  # 15% max
    BucketType.ANALOG: 0.20,  # 20% max
    BucketType.FOUNDRY: 0.15,  # 15% max
    BucketType.POWER: 0.10,  # 10% max
    BucketType.SPECULATIVE: 0.05,  # 5% max
    BucketType.CASH: 1.00,  # 100% max (no limit)
}
