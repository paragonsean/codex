"""
Standardized IndicatorResult schema for all semiconductor cycle indicators.

This provides a consistent structure for all indicators to return results,
enabling generic report generation and driver selection logic.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class IndicatorCategory(Enum):
    """Category of indicator."""
    MOMENTUM = "momentum"
    TREND = "trend"
    VOLATILITY = "volatility"
    VOLUME = "volume"
    RELATIVE = "relative"
    NEWS = "news"


class IndicatorTimeframe(Enum):
    """Timeframe of indicator."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MULTI = "multi"


class IndicatorDirection(Enum):
    """Direction of indicator signal."""
    RISK = "risk"
    OPPORTUNITY = "opportunity"
    NEUTRAL = "neutral"


@dataclass
class IndicatorRule:
    """A single rule that can fire within an indicator."""
    name: str
    fired: bool
    points: int  # Positive for risk, negative for opportunity
    description: str


@dataclass
class IndicatorResult:
    """
    Standardized result structure for all semiconductor cycle indicators.
    
    This schema enables:
    - Generic report generation
    - Automatic driver selection (top risk/opportunity contributors)
    - Consistent alert formatting
    - Clear "why this matters" explanations
    """
    
    # Metadata
    name: str
    category: IndicatorCategory
    timeframe: IndicatorTimeframe
    direction: IndicatorDirection
    
    # Evidence fields (indicator-specific metrics)
    evidence: Dict[str, Any]
    
    # Rules that fired
    rules_fired: List[IndicatorRule] = field(default_factory=list)
    
    # Scoring
    risk_points: int = 0
    opportunity_points: int = 0
    
    # Human-readable output
    alert: Optional[str] = None
    why_it_matters: str = ""
    
    def get_net_points(self) -> int:
        """Calculate net points (risk - opportunity)."""
        return self.risk_points - self.opportunity_points
    
    def get_primary_rule(self) -> Optional[IndicatorRule]:
        """Get the highest-impact rule that fired."""
        if not self.rules_fired:
            return None
        return max(self.rules_fired, key=lambda r: abs(r.points))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "category": self.category.value,
            "timeframe": self.timeframe.value,
            "direction": self.direction.value,
            "evidence": self.evidence,
            "rules_fired": [
                {
                    "name": rule.name,
                    "fired": rule.fired,
                    "points": rule.points,
                    "description": rule.description,
                }
                for rule in self.rules_fired
            ],
            "risk_points": self.risk_points,
            "opportunity_points": self.opportunity_points,
            "alert": self.alert,
            "why_it_matters": self.why_it_matters,
        }


class DriverSelector:
    """
    Selects top drivers (primary reasons) from indicator results.
    
    Sorts by risk_points (descending) and picks top 3 risk drivers
    plus 1 opportunity driver if strong enough.
    """
    
    @staticmethod
    def select_drivers(
        results: List[IndicatorResult],
        max_risk_drivers: int = 3,
        max_opportunity_drivers: int = 1,
        min_opportunity_threshold: int = 10,
    ) -> Dict[str, List[IndicatorResult]]:
        """
        Select top drivers from indicator results.
        
        Args:
            results: List of IndicatorResult objects
            max_risk_drivers: Maximum risk drivers to select
            max_opportunity_drivers: Maximum opportunity drivers to select
            min_opportunity_threshold: Minimum opportunity points to qualify
            
        Returns:
            Dict with 'risk_drivers' and 'opportunity_drivers' lists
        """
        # Separate risk and opportunity indicators
        risk_indicators = [r for r in results if r.risk_points > 0]
        opportunity_indicators = [
            r for r in results 
            if r.opportunity_points >= min_opportunity_threshold
        ]
        
        # Sort by points (descending)
        risk_drivers = sorted(
            risk_indicators,
            key=lambda r: r.risk_points,
            reverse=True
        )[:max_risk_drivers]
        
        opportunity_drivers = sorted(
            opportunity_indicators,
            key=lambda r: r.opportunity_points,
            reverse=True
        )[:max_opportunity_drivers]
        
        return {
            "risk_drivers": risk_drivers,
            "opportunity_drivers": opportunity_drivers,
        }
    
    @staticmethod
    def format_driver_summary(drivers: Dict[str, List[IndicatorResult]]) -> str:
        """
        Format drivers into human-readable summary.
        
        Returns:
            String like "Primary drivers: First 50DMA failure, Good news effectiveness breakdown, Relative strength vs SOX rolling over."
        """
        parts = []
        
        if drivers["risk_drivers"]:
            risk_names = [
                r.get_primary_rule().description if r.get_primary_rule() else r.name
                for r in drivers["risk_drivers"]
            ]
            parts.append(f"Primary risk drivers: {', '.join(risk_names)}")
        
        if drivers["opportunity_drivers"]:
            opp_names = [
                r.get_primary_rule().description if r.get_primary_rule() else r.name
                for r in drivers["opportunity_drivers"]
            ]
            parts.append(f"Opportunity drivers: {', '.join(opp_names)}")
        
        return ". ".join(parts) if parts else "No significant drivers detected."
