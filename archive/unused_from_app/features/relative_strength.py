"""
Relative Strength vs SOX Analysis - Leadership Loss Detector

Semiconductors top by rotation inside the sector: leaders start lagging SOX
before price breaks. This catches the "quiet peak" - stock still looks strong,
but capital is moving elsewhere.

This is one of the best "quiet peak" tells for semiconductor stocks.
"""

from __future__ import annotations

from typing import Dict, Optional
import pandas as pd
import numpy as np

from features.indicator_result import (
    IndicatorResult,
    IndicatorCategory,
    IndicatorTimeframe,
    IndicatorDirection,
    IndicatorRule,
)


class RelativeStrengthAnalyzer:
    """
    Analyzes relative strength vs SOX index to detect leadership loss.
    
    Why this matters for semiconductor cycles:
    - Semis top by rotation inside the sector
    - Leaders (MU/NVDA/AMD) start lagging the index before price breaks
    - Money rotates into "safer semi" (EDA, analog) while index looks fine
    - This is one of the best "quiet peak" tells
    """
    
    @staticmethod
    def analyze_relative_strength_vs_sox(
        stock_df: pd.DataFrame,
        sox_df: pd.DataFrame,
        lookback_20d: int = 20,
        lookback_60d: int = 60,
    ) -> IndicatorResult:
        """
        Analyze relative strength vs SOX index.
        
        Algorithm:
        1. Normalize both series to 1.0 at start of lookback
        2. rs_ratio = norm_stock / norm_sox
        3. Take slope of rs_ratio over 20d and 60d
        
        Interpretation:
        - rs_slope_20d < 0 = losing leadership now
        - rs_slope_60d < 0 = structural lagging
        - If price near highs while RS weak → distribution risk
        
        Args:
            stock_df: Stock OHLCV DataFrame
            sox_df: SOX index OHLCV DataFrame
            lookback_20d: Short-term lookback period
            lookback_60d: Long-term lookback period
            
        Returns:
            IndicatorResult with relative strength analysis
        """
        # Default empty result
        if stock_df.empty or sox_df.empty or len(stock_df) < lookback_60d or len(sox_df) < lookback_60d:
            return IndicatorResult(
                name="RELATIVE_STRENGTH_VS_SOX",
                category=IndicatorCategory.RELATIVE,
                timeframe=IndicatorTimeframe.DAILY,
                direction=IndicatorDirection.NEUTRAL,
                evidence={
                    "rs_ratio_current": 0.0,
                    "rs_slope_20d": 0.0,
                    "rs_slope_60d": 0.0,
                    "rs_breakdown": False,
                    "price_at_highs": False,
                    "stock_return_20d": 0.0,
                },
                risk_points=0,
                opportunity_points=0,
                alert=None,
                why_it_matters=(
                    "Semis top by rotation inside the sector: leaders start lagging SOX before price breaks. "
                    "It catches the 'quiet peak' - stock still looks strong, but capital is moving elsewhere."
                ),
            )
        
        stock_close = stock_df['Close']
        sox_close = sox_df['Close']
        
        # Align the series (use common dates)
        aligned = pd.DataFrame({
            'stock': stock_close,
            'sox': sox_close,
        }).dropna()
        
        if len(aligned) < lookback_60d:
            return IndicatorResult(
                name="RELATIVE_STRENGTH_VS_SOX",
                category=IndicatorCategory.RELATIVE,
                timeframe=IndicatorTimeframe.DAILY,
                direction=IndicatorDirection.NEUTRAL,
                evidence={
                    "rs_ratio_current": 0.0,
                    "rs_slope_20d": 0.0,
                    "rs_slope_60d": 0.0,
                    "rs_breakdown": False,
                    "price_at_highs": False,
                    "stock_return_20d": 0.0,
                },
                risk_points=0,
                opportunity_points=0,
                alert=None,
                why_it_matters=(
                    "Semis top by rotation inside the sector: leaders start lagging SOX before price breaks. "
                    "It catches the 'quiet peak' - stock still looks strong, but capital is moving elsewhere."
                ),
            )
        
        # Normalize both series to 1.0 at start of 60d lookback
        stock_norm = aligned['stock'] / aligned['stock'].iloc[-lookback_60d]
        sox_norm = aligned['sox'] / aligned['sox'].iloc[-lookback_60d]
        
        # Calculate RS ratio (normalized stock / normalized SOX)
        rs_ratio = stock_norm / sox_norm
        
        # Current RS ratio
        rs_ratio_current = float(rs_ratio.iloc[-1])
        
        # Calculate slopes using linear regression
        def calculate_slope(series: pd.Series, period: int) -> float:
            """Calculate slope of series over period using linear regression."""
            if len(series) < period:
                return 0.0
            
            recent = series.tail(period).values
            x = np.arange(len(recent))
            
            # Linear regression: y = mx + b
            coeffs = np.polyfit(x, recent, 1)
            slope = coeffs[0]
            
            # Normalize slope to percentage per day
            return float(slope * 100)
        
        rs_slope_20d = calculate_slope(rs_ratio, lookback_20d)
        rs_slope_60d = calculate_slope(rs_ratio, lookback_60d)
        
        # Check if RS breakdown (slope turned negative)
        rs_breakdown = rs_slope_20d < 0 and rs_slope_60d < 0
        
        # Check if price at highs
        stock_high_20d = aligned['stock'].tail(20).max()
        current_stock = aligned['stock'].iloc[-1]
        price_at_highs = (current_stock / stock_high_20d) > 0.95
        
        # Calculate stock return over 20d
        stock_return_20d = ((aligned['stock'].iloc[-1] / aligned['stock'].iloc[-lookback_20d] - 1) * 100) if len(aligned) >= lookback_20d else 0.0
        
        # Build evidence
        evidence = {
            "rs_ratio_current": rs_ratio_current,
            "rs_slope_20d": rs_slope_20d,
            "rs_slope_60d": rs_slope_60d,
            "rs_breakdown": rs_breakdown,
            "price_at_highs": price_at_highs,
            "stock_return_20d": stock_return_20d,
        }
        
        # Evaluate rules
        rules_fired = []
        risk_points = 0
        opportunity_points = 0
        direction = IndicatorDirection.NEUTRAL
        alert = None
        
        # Rule: RS_LEADERSHIP_LOSS
        if rs_slope_20d < 0 and stock_return_20d > 0:
            rule = IndicatorRule(
                name="RS_LEADERSHIP_LOSS",
                fired=True,
                points=25,
                description="Losing leadership vs SOX while price still rising",
            )
            rules_fired.append(rule)
            risk_points += 25
            direction = IndicatorDirection.RISK
            alert = f"🔴 LEADERSHIP LOSS: RS slope declining ({rs_slope_20d:.2f}%/day) while stock up {stock_return_20d:.1f}% - rotation away"
        
        # Rule: RS_DISTRIBUTION_WARNING
        if price_at_highs and rs_slope_60d < 0:
            rule = IndicatorRule(
                name="RS_DISTRIBUTION_WARNING",
                fired=True,
                points=30,
                description="Price at highs but losing relative strength vs SOX",
            )
            rules_fired.append(rule)
            risk_points += 30
            direction = IndicatorDirection.RISK
            if not alert:
                alert = f"🔴 DISTRIBUTION WARNING: Price at highs but RS slope negative ({rs_slope_60d:.2f}%/day) - quiet peak"
        
        # Rule: RS_BREAKDOWN
        if rs_breakdown:
            rule = IndicatorRule(
                name="RS_BREAKDOWN",
                fired=True,
                points=20,
                description="RS breakdown - both 20D and 60D slopes negative",
            )
            rules_fired.append(rule)
            risk_points += 20
            direction = IndicatorDirection.RISK
            if not alert:
                alert = f"⚠️ RS BREAKDOWN: Both short and long-term RS declining - structural lagging vs SOX"
        
        # Rule: RS_RECOVERY (opportunity)
        if rs_slope_20d > 0 and rs_slope_60d < 0:
            # Short-term recovery after decline
            rule = IndicatorRule(
                name="RS_RECOVERY",
                fired=True,
                points=-15,
                description="RS recovering vs SOX - potential leadership return",
            )
            rules_fired.append(rule)
            opportunity_points += 15
            direction = IndicatorDirection.OPPORTUNITY
            if not alert:
                alert = f"💚 RS RECOVERY: Short-term RS improving ({rs_slope_20d:.2f}%/day) - regaining leadership"
        
        # Rule: RS_STRONG (opportunity)
        if rs_slope_20d > 0 and rs_slope_60d > 0 and rs_ratio_current > 1.0:
            rule = IndicatorRule(
                name="RS_STRONG",
                fired=True,
                points=-10,
                description="Strong relative strength vs SOX - leading sector",
            )
            rules_fired.append(rule)
            opportunity_points += 10
            direction = IndicatorDirection.OPPORTUNITY
            if not alert:
                alert = f"💚 STRONG RS: Outperforming SOX on both timeframes - sector leader"
        
        return IndicatorResult(
            name="RELATIVE_STRENGTH_VS_SOX",
            category=IndicatorCategory.RELATIVE,
            timeframe=IndicatorTimeframe.DAILY,
            direction=direction,
            evidence=evidence,
            rules_fired=rules_fired,
            risk_points=risk_points,
            opportunity_points=opportunity_points,
            alert=alert,
            why_it_matters=(
                "Semis top by rotation inside the sector: leaders start lagging SOX before price breaks. "
                "It catches the 'quiet peak' - stock still looks strong, but capital is moving elsewhere. "
                "Money rotates into 'safer semi' (EDA, analog) while the index still looks fine. "
                "This is one of the best 'quiet peak' tells."
            ),
        )
