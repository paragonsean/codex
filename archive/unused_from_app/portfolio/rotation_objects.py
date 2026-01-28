"""
Rotation Planning Objects

Objects for managing month-by-month portfolio rotation plans and post-peak watchlists.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class RotationActionType(Enum):
    """Types of rotation actions."""
    TRIM = "TRIM"
    EXIT = "EXIT"
    ADD = "ADD"
    REBALANCE = "REBALANCE"
    MONITOR = "MONITOR"


class RotationUrgency(Enum):
    """Urgency levels for rotation actions."""
    IMMEDIATE = "IMMEDIATE"  # Execute within 1 week
    HIGH = "HIGH"  # Execute within 2 weeks
    MEDIUM = "MEDIUM"  # Execute within 1 month
    LOW = "LOW"  # Execute within 2 months
    OPPORTUNISTIC = "OPPORTUNISTIC"  # Execute when favorable


class ExecutionStatus(Enum):
    """Status of rotation step execution."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    DEFERRED = "DEFERRED"


class WatchlistReason(Enum):
    """Reasons for adding to post-peak watchlist."""
    POST_PEAK_EXIT = "POST_PEAK_EXIT"  # Exited due to peaking
    CYCLE_DOWNTURN = "CYCLE_DOWNTURN"  # Exited during downturn
    RISK_REDUCTION = "RISK_REDUCTION"  # Trimmed for risk management
    REBALANCE = "REBALANCE"  # Reduced for portfolio balance


class ReentryCondition(Enum):
    """Conditions for re-entering a watchlist position."""
    CYCLE_RESET = "CYCLE_RESET"  # New cycle begins (RSI < 30, fresh base)
    PHASE_EARLY = "PHASE_EARLY"  # Returns to EARLY phase
    RELATIVE_STRENGTH_RECOVERY = "RELATIVE_STRENGTH_RECOVERY"  # RS vs SOX improves
    GOOD_NEWS_WORKS = "GOOD_NEWS_WORKS"  # Good news effectiveness restored
    PRICE_RESET = "PRICE_RESET"  # 20%+ correction from peak
    TIME_ELAPSED = "TIME_ELAPSED"  # 3+ months since exit


@dataclass
class RotationStep:
    """A single step in the rotation plan."""
    step_id: str
    month: int  # 1-based month number (1 = first month)
    week_in_month: int  # 1-4
    action_type: RotationActionType
    ticker: str
    bucket: str  # Bucket name
    
    # Position sizing
    current_weight: float
    target_weight: float
    delta_weight: float  # target - current
    dollar_amount: Optional[float] = None
    
    # Execution details
    urgency: RotationUrgency = RotationUrgency.MEDIUM
    status: ExecutionStatus = ExecutionStatus.PENDING
    
    # Rationale
    reason: str = ""
    risk_contribution: float = 0.0
    
    # Execution tracking
    executed_date: Optional[datetime] = None
    executed_weight: Optional[float] = None
    execution_notes: str = ""
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # List of step_ids that must complete first
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MonthlyRotationPlan:
    """Complete rotation plan broken down by month."""
    plan_id: str
    created_date: datetime
    portfolio_name: str
    total_value: float
    
    # Plan horizon
    total_months: int  # Typically 2-4 months
    
    # Steps organized by month
    steps: List[RotationStep]
    
    # Summary metrics
    total_trims: int = 0
    total_adds: int = 0
    total_exits: int = 0
    total_dollar_rotation: float = 0.0
    
    # Target end state
    target_bucket_weights: Dict[str, float] = field(default_factory=dict)
    target_mode: str = "BALANCED"  # Target portfolio mode
    
    # Progress tracking
    completed_steps: int = 0
    in_progress_steps: int = 0
    
    # Metadata
    assumptions: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)


@dataclass
class WatchlistEntry:
    """Entry in the post-peak watchlist for potential re-entry."""
    ticker: str
    bucket: str
    
    # Exit details
    exit_date: datetime
    exit_price: float
    exit_weight: float
    exit_reason: WatchlistReason
    
    # Cycle state at exit
    exit_phase: str
    exit_risk_score: float
    exit_critical_signals: List[str]
    
    # Re-entry conditions
    reentry_conditions: List[ReentryCondition]
    conditions_met: List[ReentryCondition] = field(default_factory=list)
    
    # Current monitoring
    current_price: Optional[float] = None
    current_phase: Optional[str] = None
    current_risk_score: Optional[float] = None
    price_change_from_exit: Optional[float] = None  # Percentage
    
    # Re-entry readiness
    ready_for_reentry: bool = False
    reentry_score: float = 0.0  # 0-100, higher = more ready
    
    # Notes
    monitoring_notes: str = ""
    last_updated: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RotationExecution:
    """Tracks execution of a rotation plan."""
    plan_id: str
    execution_start_date: datetime
    current_month: int
    
    # Execution progress
    steps_completed: List[str]  # step_ids
    steps_in_progress: List[str]
    steps_deferred: List[str]
    
    # Performance tracking
    portfolio_value_at_start: float
    current_portfolio_value: float
    
    # Deviation from plan
    ahead_of_schedule: List[str]  # step_ids completed early
    behind_schedule: List[str]  # step_ids delayed
    
    # Market conditions
    market_conditions_changed: bool = False
    condition_change_notes: str = ""
    
    # Adjustments made
    plan_adjustments: List[Dict[str, Any]] = field(default_factory=list)
    
    # Next actions
    next_week_actions: List[str] = field(default_factory=list)  # step_ids
    
    # Metadata
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None


@dataclass
class RotationOpportunity:
    """Identifies an opportunity to add/increase a position."""
    ticker: str
    bucket: str
    
    # Opportunity metrics
    opportunity_score: float  # From cycle analysis
    phase: str
    risk_score: float
    
    # Sizing recommendation
    recommended_weight: float
    max_weight: float  # Based on bucket limits
    
    # Timing
    urgency: RotationUrgency
    ideal_entry_window: str  # e.g., "Next 2-4 weeks"
    
    # Rationale
    opportunity_drivers: List[str]  # e.g., ["Early cycle", "Strong RS vs SOX"]
    fits_rotation_plan: bool
    
    # Constraints
    requires_capital_from: List[str] = field(default_factory=list)  # Tickers to trim first
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
