from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np

from features.indicator_result import (
    IndicatorResult,
    IndicatorCategory,
    IndicatorTimeframe,
    IndicatorDirection,
    IndicatorRule,
)


class SemiconductorIndicators:
    """
    Semiconductor-specific technical indicators for cycle peak/topping detection.
    
    Focuses on memory stocks (MU, WDC, SNDK) which often peak when RSI > 75 
    for 2-4 consecutive weeks.
    """
    
    MEMORY_STOCKS = {"MU", "WDC", "SNDK", "STX"}
    RSI_OVERBOUGHT_THRESHOLD = 75
    RSI_OVERSOLD_THRESHOLD = 25
    RSI_ACCUMULATION_ZONE_LOW = 55
    RSI_ACCUMULATION_ZONE_HIGH = 70
    EXHAUSTION_THRESHOLD = 0.98
    EXHAUSTION_MIN_DAYS = 10
    DIVERGENCE_LOOKBACK_DAYS = 20
    ROC_PERIODS = [5, 10, 21]  # Short, medium, long-term ROC
    TREND_PERSISTENCE_PERIODS = [20, 50, 100]  # Days to measure % time above 50DMA
    LONG_UPTREND_MIN_DAYS = 60  # Minimum days above 50DMA to qualify as "long uptrend"
    ATR_WINDOW = 14
    ATR_BASELINE_WINDOW = 50
    ATR_EXPANSION_THRESHOLD = 1.5  # Z-score threshold for expansion
    MA_EXTENSION_ELEVATED = 15.0  # % above 50DMA = elevated
    MA_EXTENSION_EXTREME = 25.0   # % above 50DMA = extreme
    VOL_WINDOW = 20
    VOL_BASELINE_WINDOW = 120
    VOL_REGIME_HIGH_THRESHOLD = 1.3  # Ratio threshold for high vol regime
    
    @staticmethod
    def calculate_rsi_trend(df: pd.DataFrame, period: int = 14, weeks: int = 8) -> IndicatorResult:
        """
        Calculate RSI trend over the past N weeks.
        
        Args:
            df: DataFrame with OHLCV data
            period: RSI period (default 14)
            weeks: Number of weeks to analyze (default 8)
            
        Returns:
            IndicatorResult with RSI trend analysis
        """
        if df.empty or len(df) < period * weeks:
            return IndicatorResult(
                name="RSI_SUSTAINED_OVERBOUGHT_WEEKLY",
                category=IndicatorCategory.MOMENTUM,
                timeframe=IndicatorTimeframe.WEEKLY,
                direction=IndicatorDirection.NEUTRAL,
                evidence={
                    "current_rsi_14": 50.0,
                    "weekly_rsi": [],
                    "weeks_above_75": 0,
                    "weeks_below_25": 0,
                    "trend_direction": "neutral",
                },
                risk_points=0,
                opportunity_points=0,
                alert=None,
                why_it_matters="Semis (especially memory) mean-revert; sustained RSI extremes usually reflect late-cycle crowding.",
            )
        
        close = df['Close']
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
        
        weekly_rsi = []
        days_per_week = 5
        total_days = weeks * days_per_week
        
        if len(rsi) >= total_days:
            for i in range(weeks):
                week_start = -(total_days - i * days_per_week)
                week_end = week_start + days_per_week
                if week_end == 0:
                    week_end = None
                week_data = rsi.iloc[week_start:week_end]
                if len(week_data) > 0:
                    weekly_avg = float(week_data.mean())
                    weekly_rsi.append(weekly_avg)
        
        weeks_above_75 = SemiconductorIndicators._count_consecutive_weeks_above(
            weekly_rsi, SemiconductorIndicators.RSI_OVERBOUGHT_THRESHOLD
        )
        
        weeks_below_25 = SemiconductorIndicators._count_consecutive_weeks_below(
            weekly_rsi, SemiconductorIndicators.RSI_OVERSOLD_THRESHOLD
        )
        
        trend_direction = SemiconductorIndicators._determine_rsi_trend(weekly_rsi)
        
        # Evaluate rules
        rules_fired = []
        risk_points = 0
        opportunity_points = 0
        direction = IndicatorDirection.NEUTRAL
        alert = None
        
        # Rule: RSI_4W_OVERBOUGHT_CRITICAL
        if weeks_above_75 >= 4:
            rule = IndicatorRule(
                name="RSI_4W_OVERBOUGHT_CRITICAL",
                fired=True,
                points=40,
                description="RSI above 75 for 4+ weeks - extreme overbought",
            )
            rules_fired.append(rule)
            risk_points = 40
            direction = IndicatorDirection.RISK
            alert = "🔴 CRITICAL: RSI above 75 for 4+ weeks - extreme overbought"
        
        # Rule: RSI_2W_OVERBOUGHT
        elif weeks_above_75 >= 2:
            rule = IndicatorRule(
                name="RSI_2W_OVERBOUGHT",
                fired=True,
                points=20,
                description=f"RSI above 75 for {weeks_above_75} weeks",
            )
            rules_fired.append(rule)
            risk_points = 20
            direction = IndicatorDirection.RISK
            alert = f"⚠️ WARNING: RSI above 75 for {weeks_above_75} weeks - monitor for topping"
            
            # Rule: RSI_OVERBOUGHT_STILL_RISING
            if trend_direction == "rising":
                rule_rising = IndicatorRule(
                    name="RSI_OVERBOUGHT_STILL_RISING",
                    fired=True,
                    points=5,
                    description="RSI overbought and still rising",
                )
                rules_fired.append(rule_rising)
                risk_points += 5
        
        # Rule: RSI_2W_OVERSOLD (opportunity)
        if weeks_below_25 >= 2:
            rule = IndicatorRule(
                name="RSI_2W_OVERSOLD",
                fired=True,
                points=-25,
                description=f"RSI below 25 for {weeks_below_25} weeks - oversold bounce opportunity",
            )
            rules_fired.append(rule)
            opportunity_points = 25
            direction = IndicatorDirection.OPPORTUNITY
            if not alert:
                alert = f"💚 OVERSOLD: RSI below 25 for {weeks_below_25} weeks - potential bounce"
        
        return IndicatorResult(
            name="RSI_SUSTAINED_OVERBOUGHT_WEEKLY",
            category=IndicatorCategory.MOMENTUM,
            timeframe=IndicatorTimeframe.WEEKLY,
            direction=direction,
            evidence={
                "current_rsi_14": current_rsi,
                "weekly_rsi": weekly_rsi,
                "weeks_above_75": weeks_above_75,
                "weeks_below_25": weeks_below_25,
                "trend_direction": trend_direction,
            },
            rules_fired=rules_fired,
            risk_points=risk_points,
            opportunity_points=opportunity_points,
            alert=alert,
            why_it_matters="Semis (especially memory) mean-revert; sustained RSI extremes usually reflect late-cycle crowding.",
        )
    
    @staticmethod
    def _count_consecutive_weeks_above(weekly_rsi: List[float], threshold: float) -> int:
        """Count consecutive weeks from the end where RSI > threshold."""
        if not weekly_rsi:
            return 0
        
        count = 0
        for rsi in reversed(weekly_rsi):
            if rsi > threshold:
                count += 1
            else:
                break
        return count
    
    @staticmethod
    def _count_consecutive_weeks_below(weekly_rsi: List[float], threshold: float) -> int:
        """Count consecutive weeks from the end where RSI < threshold."""
        if not weekly_rsi:
            return 0
        
        count = 0
        for rsi in reversed(weekly_rsi):
            if rsi < threshold:
                count += 1
            else:
                break
        return count
    
    @staticmethod
    def _determine_rsi_trend(weekly_rsi: List[float]) -> str:
        """Determine if RSI is rising, falling, or neutral over recent weeks."""
        if len(weekly_rsi) < 3:
            return "neutral"
        
        recent_3_weeks = weekly_rsi[-3:]
        
        if recent_3_weeks[2] > recent_3_weeks[1] > recent_3_weeks[0]:
            return "rising"
        elif recent_3_weeks[2] < recent_3_weeks[1] < recent_3_weeks[0]:
            return "falling"
        elif recent_3_weeks[2] > recent_3_weeks[0]:
            return "rising"
        elif recent_3_weeks[2] < recent_3_weeks[0]:
            return "falling"
        else:
            return "neutral"
    
    @staticmethod
    def _calculate_rsi_risk_points(
        current_rsi: float, 
        weeks_above_75: int, 
        trend_direction: str
    ) -> int:
        """
        Calculate risk points based on RSI overbought conditions.
        
        Rules:
        - +10 points per week RSI > 75 (memory stocks often peak at 2-4 weeks)
        - +5 bonus points if still rising
        - +20 bonus points if >= 4 weeks above 75 (critical topping signal)
        """
        risk_points = 0
        
        risk_points += weeks_above_75 * 10
        
        if trend_direction == "rising" and current_rsi > 75:
            risk_points += 5
        
        if weeks_above_75 >= 4:
            risk_points += 20
        
        return risk_points
    
    @staticmethod
    def _generate_rsi_alert(
        current_rsi: float,
        weeks_above_75: int,
        weeks_below_25: int,
        trend_direction: str,
    ) -> Optional[str]:
        """Generate alert message based on RSI conditions."""
        if weeks_above_75 >= 4:
            return f"🔴 CRITICAL: RSI sustained above 75 for {weeks_above_75} weeks - potential cycle peak"
        elif weeks_above_75 >= 2:
            return f"⚠️ WARNING: RSI above 75 for {weeks_above_75} weeks - monitor for topping"
        elif current_rsi > 75 and trend_direction == "rising":
            return "⚠️ CAUTION: RSI overbought and still rising"
        elif weeks_below_25 >= 2:
            return f"💚 OPPORTUNITY: RSI below 25 for {weeks_below_25} weeks - potential oversold bounce"
        
        return None
    
    @staticmethod
    def is_memory_stock(ticker: str) -> bool:
        """Check if ticker is a memory stock (MU, WDC, SNDK, STX)."""
        return ticker.upper() in SemiconductorIndicators.MEMORY_STOCKS
    
    @staticmethod
    def calculate_exhaustion_signal(df: pd.DataFrame, threshold: float = 0.98, min_days: int = 10) -> IndicatorResult:
        """
        Calculate position vs 20-day high exhaustion signal.
        
        When price stays >97-99% of 20-day highs for 10+ trading days,
        upside is usually capped (distribution pattern).
        
        Args:
            df: DataFrame with OHLCV data
            threshold: Minimum ratio to 20D high (default 0.98 = 98%)
            min_days: Minimum consecutive days to flag (default 10)
            
        Returns:
            IndicatorResult with exhaustion analysis
        """
        if df.empty or len(df) < 20:
            return IndicatorResult(
                name="EXHAUSTION_NEAR_20D_HIGH",
                category=IndicatorCategory.TREND,
                timeframe=IndicatorTimeframe.DAILY,
                direction=IndicatorDirection.NEUTRAL,
                evidence={
                    "position_vs_20d_high": 0.0,
                    "days_above_threshold": 0,
                    "threshold": threshold,
                    "is_exhausted": False,
                },
                risk_points=0,
                opportunity_points=0,
                alert=None,
                why_it_matters="Breakouts need expanding participation; 'pinned highs' often mean distribution.",
            )
        
        close = df['Close']
        high_20d = df['High'].rolling(20).max()
        
        position_vs_high = close / high_20d
        
        current_position = float(position_vs_high.iloc[-1]) if not pd.isna(position_vs_high.iloc[-1]) else 0.0
        
        days_above = 0
        position_values = position_vs_high.dropna().values
        for i in range(len(position_values) - 1, -1, -1):
            if position_values[i] > threshold:
                days_above += 1
            else:
                break
        
        is_exhausted = days_above >= min_days
        
        # Evaluate rules
        rules_fired = []
        risk_points = 0
        direction = IndicatorDirection.NEUTRAL
        alert = None
        
        # Rule: PINNED_AT_HIGHS
        if is_exhausted:
            # Base risk: 15 points + 2 points per day beyond min_days (capped at +25)
            extra_days = days_above - min_days
            points = 15 + min(extra_days * 2, 25)
            
            rule = IndicatorRule(
                name="PINNED_AT_HIGHS",
                fired=True,
                points=points,
                description=f"Price pinned at {current_position:.1%} of 20D high for {days_above} days",
            )
            rules_fired.append(rule)
            risk_points = points
            direction = IndicatorDirection.RISK
            alert = f"⚠️ EXHAUSTION: Price pinned at {current_position:.1%} of 20D high for {days_above} days - upside capped"
        
        return IndicatorResult(
            name="EXHAUSTION_NEAR_20D_HIGH",
            category=IndicatorCategory.TREND,
            timeframe=IndicatorTimeframe.DAILY,
            direction=direction,
            evidence={
                "position_vs_20d_high": current_position,
                "days_above_threshold": days_above,
                "threshold": threshold,
                "is_exhausted": is_exhausted,
            },
            rules_fired=rules_fired,
            risk_points=risk_points,
            opportunity_points=0,
            alert=alert,
            why_it_matters="Breakouts need expanding participation; 'pinned highs' often mean distribution.",
        )
    
    @staticmethod
    def detect_rsi_divergence(df: pd.DataFrame, lookback_days: int = 20) -> IndicatorResult:
        """
        Detect RSI divergence - early momentum decay signal.
        
        When price makes higher highs but RSI does not, it signals:
        - Buying pressure not keeping pace with price
        - Smart money leaving quietly
        - Often occurs before memory pricing flattens
        
        Args:
            df: DataFrame with OHLCV data
            lookback_days: Days to look back for divergence (default 20)
            
        Returns:
            IndicatorResult with divergence analysis
        """
        if df.empty or len(df) < lookback_days + 14:
            return IndicatorResult(
                name="RSI_DIVERGENCE_SWING",
                category=IndicatorCategory.MOMENTUM,
                timeframe=IndicatorTimeframe.DAILY,
                direction=IndicatorDirection.NEUTRAL,
                evidence={
                    "divergence_type": "none",
                    "swing_points_used": 0,
                    "price_swing_high_1": None,
                    "price_swing_high_2": None,
                    "rsi_swing_high_1": None,
                    "rsi_swing_high_2": None,
                },
                risk_points=0,
                opportunity_points=0,
                alert=None,
                why_it_matters="Semis often show momentum decay before price breaks—smart money exits quietly.",
            )
        
        close = df['Close']
        
        # Calculate RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Get recent data
        recent_df = df.tail(lookback_days).copy()
        recent_close = recent_df['Close']
        recent_rsi = rsi.tail(lookback_days)
        
        # Find local peaks in price and RSI
        price_peaks = SemiconductorIndicators._find_peaks(recent_close.values)
        rsi_peaks = SemiconductorIndicators._find_peaks(recent_rsi.values)
        
        # Check for bearish divergence (price higher highs, RSI lower highs)
        has_bearish_div = False
        if len(price_peaks) >= 2 and len(rsi_peaks) >= 2:
            # Get last two price peaks
            last_price_peak_idx = price_peaks[-1]
            prev_price_peak_idx = price_peaks[-2]
            
            # Get last two RSI peaks
            last_rsi_peak_idx = rsi_peaks[-1]
            prev_rsi_peak_idx = rsi_peaks[-2]
            
            # Bearish divergence: price makes higher high, RSI makes lower high
            if (recent_close.iloc[last_price_peak_idx] > recent_close.iloc[prev_price_peak_idx] and
                recent_rsi.iloc[last_rsi_peak_idx] < recent_rsi.iloc[prev_rsi_peak_idx]):
                has_bearish_div = True
        
        # Check for bullish divergence (price lower lows, RSI higher lows)
        price_troughs = SemiconductorIndicators._find_troughs(recent_close.values)
        rsi_troughs = SemiconductorIndicators._find_troughs(recent_rsi.values)
        
        has_bullish_div = False
        if len(price_troughs) >= 2 and len(rsi_troughs) >= 2:
            last_price_trough_idx = price_troughs[-1]
            prev_price_trough_idx = price_troughs[-2]
            
            last_rsi_trough_idx = rsi_troughs[-1]
            prev_rsi_trough_idx = rsi_troughs[-2]
            
            # Bullish divergence: price makes lower low, RSI makes higher low
            if (recent_close.iloc[last_price_trough_idx] < recent_close.iloc[prev_price_trough_idx] and
                recent_rsi.iloc[last_rsi_trough_idx] > recent_rsi.iloc[prev_rsi_trough_idx]):
                has_bullish_div = True
        
        # Build evidence
        evidence = {
            "divergence_type": "none",
            "swing_points_used": len(price_peaks) + len(price_troughs),
            "price_swing_high_1": None,
            "price_swing_high_2": None,
            "rsi_swing_high_1": None,
            "rsi_swing_high_2": None,
        }
        
        if has_bearish_div and len(price_peaks) >= 2 and len(rsi_peaks) >= 2:
            evidence["divergence_type"] = "bearish"
            evidence["price_swing_high_1"] = float(recent_close.iloc[price_peaks[-1]])
            evidence["price_swing_high_2"] = float(recent_close.iloc[price_peaks[-2]])
            evidence["rsi_swing_high_1"] = float(recent_rsi.iloc[rsi_peaks[-1]])
            evidence["rsi_swing_high_2"] = float(recent_rsi.iloc[rsi_peaks[-2]])
        elif has_bullish_div and len(price_troughs) >= 2 and len(rsi_troughs) >= 2:
            evidence["divergence_type"] = "bullish"
        
        # Evaluate rules
        rules_fired = []
        risk_points = 0
        opportunity_points = 0
        direction = IndicatorDirection.NEUTRAL
        alert = None
        
        # Rule: BEARISH_DIVERGENCE
        if has_bearish_div:
            rule = IndicatorRule(
                name="BEARISH_DIVERGENCE",
                fired=True,
                points=30,
                description="Price higher highs but RSI lower highs - momentum decay",
            )
            rules_fired.append(rule)
            risk_points = 30
            direction = IndicatorDirection.RISK
            alert = "🔴 BEARISH DIVERGENCE: Price making higher highs but RSI declining - smart money leaving"
        
        # Rule: BULLISH_DIVERGENCE
        elif has_bullish_div:
            rule = IndicatorRule(
                name="BULLISH_DIVERGENCE",
                fired=True,
                points=-20,
                description="Price lower lows but RSI higher lows - potential reversal",
            )
            rules_fired.append(rule)
            opportunity_points = 20
            direction = IndicatorDirection.OPPORTUNITY
            alert = "💚 BULLISH DIVERGENCE: Price making lower lows but RSI rising - potential reversal"
        
        return IndicatorResult(
            name="RSI_DIVERGENCE_SWING",
            category=IndicatorCategory.MOMENTUM,
            timeframe=IndicatorTimeframe.DAILY,
            direction=direction,
            evidence=evidence,
            rules_fired=rules_fired,
            risk_points=risk_points,
            opportunity_points=opportunity_points,
            alert=alert,
            why_it_matters="Semis often show momentum decay before price breaks—smart money exits quietly.",
        )
    
    @staticmethod
    def _find_peaks(data: np.ndarray, min_distance: int = 3) -> List[int]:
        """Find local peaks in data."""
        peaks = []
        for i in range(min_distance, len(data) - min_distance):
            if all(data[i] > data[i-j] for j in range(1, min_distance + 1)):
                if all(data[i] > data[i+j] for j in range(1, min_distance + 1)):
                    peaks.append(i)
        return peaks
    
    @staticmethod
    def _find_troughs(data: np.ndarray, min_distance: int = 3) -> List[int]:
        """Find local troughs in data."""
        troughs = []
        for i in range(min_distance, len(data) - min_distance):
            if all(data[i] < data[i-j] for j in range(1, min_distance + 1)):
                if all(data[i] < data[i+j] for j in range(1, min_distance + 1)):
                    troughs.append(i)
        return troughs
    
    @staticmethod
    def detect_roc_compression(df: pd.DataFrame, periods: List[int] = [5, 10, 21]) -> IndicatorResult:
        """
        Detect ROC (Rate-of-Change) compression - cycle aging signal.
        
        When ROC slows at higher prices, it signals:
        - Late-cycle conditions (buyers hesitate at higher prices)
        - Upside becomes incremental, not violent
        - Risk/reward skews negative
        - "Thin air" - slowing speed at higher altitude
        
        Args:
            df: DataFrame with OHLCV data
            periods: ROC periods to analyze (default [5, 10, 21])
            
        Returns:
            Dict with ROC compression analysis
        """
        if df.empty or len(df) < max(periods) + 20:
            return IndicatorResult(
                name="ROC_COMPRESSION",
                category=IndicatorCategory.MOMENTUM,
                timeframe=IndicatorTimeframe.MULTI,
                direction=IndicatorDirection.NEUTRAL,
                evidence={
                    "current_roc": {},
                    "baseline_roc": {},
                    "compression_ratio": {},
                    "severity": "none",
                },
                risk_points=0,
                opportunity_points=0,
                alert=None,
                why_it_matters="Late-cycle semis grind: price rises, but speed disappears ('thin air').",
            )
        
        close = df['Close']
        
        # Calculate ROC for each period
        current_roc = {}
        for period in periods:
            if len(close) >= period + 1:
                roc = ((close.iloc[-1] - close.iloc[-period - 1]) / close.iloc[-period - 1]) * 100
                current_roc[f"roc_{period}d"] = float(roc)
        
        # Calculate average ROC from "early cycle" (first third of data)
        early_cycle_end = len(df) // 3
        early_df = df.iloc[:early_cycle_end]
        
        avg_roc_early = {}
        for period in periods:
            if len(early_df) >= period + 20:
                early_close = early_df['Close']
                roc_values = []
                for i in range(period + 1, len(early_close)):
                    roc = ((early_close.iloc[i] - early_close.iloc[i - period - 1]) / early_close.iloc[i - period - 1]) * 100
                    roc_values.append(abs(roc))  # Use absolute value for speed
                
                if roc_values:
                    avg_roc_early[f"roc_{period}d"] = float(np.mean(roc_values))
        
        # Calculate compression ratio (current ROC / early cycle ROC)
        compression_ratio = {}
        for period in periods:
            key = f"roc_{period}d"
            if key in current_roc and key in avg_roc_early and avg_roc_early[key] > 0:
                ratio = abs(current_roc[key]) / avg_roc_early[key]
                compression_ratio[key] = float(ratio)
        
        # Detect compression (ROC slowing at higher prices)
        current_price = float(close.iloc[-1])
        price_change_pct = ((current_price - close.iloc[0]) / close.iloc[0]) * 100
        
        # Compression = price is higher but ROC is slower
        is_compressed = False
        compression_severity = "none"
        
        if price_change_pct > 10:  # Only check if price is significantly higher
            # Check if multiple ROC periods show compression
            compressed_periods = sum(1 for ratio in compression_ratio.values() if ratio < 0.5)
            
            if compressed_periods >= 2:
                is_compressed = True
                avg_compression = np.mean(list(compression_ratio.values()))
                
                if avg_compression < 0.3:
                    compression_severity = "severe"
                elif avg_compression < 0.5:
                    compression_severity = "moderate"
                else:
                    compression_severity = "mild"
        
        # Evaluate rules
        rules_fired = []
        risk_points = 0
        direction = IndicatorDirection.NEUTRAL
        alert = None
        
        # Rule: ROC_COMPRESSED_2_OF_3
        if is_compressed:
            if compression_severity == "severe":
                rule = IndicatorRule(
                    name="ROC_COMPRESSED_2_OF_3",
                    fired=True,
                    points=35,
                    description="Severe ROC compression - cycle aging at altitude",
                )
                rules_fired.append(rule)
                risk_points = 35
                direction = IndicatorDirection.RISK
                alert = "🔴 SEVERE ROC COMPRESSION: Cycle aging - gains slowing at higher prices (thin air)"
            elif compression_severity == "moderate":
                rule = IndicatorRule(
                    name="ROC_COMPRESSED_2_OF_3",
                    fired=True,
                    points=25,
                    description="Moderate ROC compression - late-cycle conditions",
                )
                rules_fired.append(rule)
                risk_points = 25
                direction = IndicatorDirection.RISK
                alert = "⚠️ MODERATE ROC COMPRESSION: Late-cycle conditions - upside becoming incremental"
            else:
                rule = IndicatorRule(
                    name="ROC_COMPRESSED_2_OF_3",
                    fired=True,
                    points=15,
                    description="Mild ROC compression - buyers hesitating",
                )
                rules_fired.append(rule)
                risk_points = 15
                direction = IndicatorDirection.RISK
                alert = "⚠️ MILD ROC COMPRESSION: Buyers hesitating at higher prices"
        
        return IndicatorResult(
            name="ROC_COMPRESSION",
            category=IndicatorCategory.MOMENTUM,
            timeframe=IndicatorTimeframe.MULTI,
            direction=direction,
            evidence={
                "current_roc": current_roc,
                "baseline_roc": avg_roc_early,
                "compression_ratio": compression_ratio,
                "severity": compression_severity,
            },
            rules_fired=rules_fired,
            risk_points=risk_points,
            opportunity_points=0,
            alert=alert,
            why_it_matters="Late-cycle semis grind: price rises, but speed disappears ('thin air').",
        )
    
    @staticmethod
    def analyze_rsi_accumulation_zone(df: pd.DataFrame, zone_low: int = 55, zone_high: int = 70) -> IndicatorResult:
        """
        Analyze RSI 55-70 zone - institutional accumulation band.
        
        This is the "sweet spot" in healthy semiconductor upcycles:
        - Pullbacks reset RSI to 55-60
        - Then push higher again
        - Institutions buying dips
        - Risk/reward still favorable
        - Trend alive but not crowded
        
        Args:
            df: DataFrame with OHLCV data
            zone_low: Lower bound of accumulation zone (default 55)
            zone_high: Upper bound of accumulation zone (default 70)
            
        Returns:
            Dict with accumulation zone analysis
        """
        if df.empty or len(df) < 14:
            return IndicatorResult(
                name="RSI_ACCUMULATION_ZONE_HEALTH",
                category=IndicatorCategory.MOMENTUM,
                timeframe=IndicatorTimeframe.DAILY,
                direction=IndicatorDirection.NEUTRAL,
                evidence={
                    "current_rsi": 50.0,
                    "days_since_zone": 999,
                    "zone_visits_last_20d": 0,
                    "trend_health": "unknown",
                },
                risk_points=0,
                opportunity_points=0,
                alert=None,
                why_it_matters="Healthy semi trends repeatedly reset into this band as institutions buy dips.",
            )
        
        close = df['Close']
        
        # Calculate RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
        
        # Check if currently in accumulation zone
        in_zone = zone_low <= current_rsi <= zone_high
        
        # Count zone visits in last 20 days
        recent_rsi = rsi.tail(20)
        zone_visits = sum(1 for val in recent_rsi if zone_low <= val <= zone_high)
        
        # Days since last zone visit
        days_since_zone = 0
        for i in range(len(rsi) - 1, -1, -1):
            if pd.notna(rsi.iloc[i]) and zone_low <= rsi.iloc[i] <= zone_high:
                break
            days_since_zone += 1
        
        # Evaluate rules
        rules_fired = []
        risk_points = 0
        opportunity_points = 0
        direction = IndicatorDirection.NEUTRAL
        trend_health = "unknown"
        alert = None
        
        # Rule: OVERHEATED
        if current_rsi > 75 and days_since_zone > 10:
            trend_health = "overheated"
            rule = IndicatorRule(
                name="OVERHEATED",
                fired=True,
                points=15,
                description="RSI overheated - hasn't cooled to 55-70 zone in 10+ days",
            )
            rules_fired.append(rule)
            risk_points = 15
            direction = IndicatorDirection.RISK
            alert = "⚠️ OVERHEATED: RSI hasn't cooled to 55-70 zone in 10+ days - trend crowded"
        
        # Rule: BROKEN
        elif current_rsi < 55 and days_since_zone > 15:
            trend_health = "broken"
            rule = IndicatorRule(
                name="BROKEN",
                fired=True,
                points=20,
                description="Trend broken - RSI can't get back to 55-70 zone",
            )
            rules_fired.append(rule)
            risk_points = 20
            direction = IndicatorDirection.RISK
            alert = "🔴 TREND BROKEN: RSI can't get back to 55-70 zone - institutional support fading"
        
        # Rule: HEALTHY_PULLBACK (opportunity)
        elif current_rsi < 55 and days_since_zone <= 15:
            trend_health = "pullback"
            rule = IndicatorRule(
                name="HEALTHY_PULLBACK",
                fired=True,
                points=-10,
                description="Healthy pullback - RSI resetting below 55",
            )
            rules_fired.append(rule)
            opportunity_points = 10
            direction = IndicatorDirection.OPPORTUNITY
            alert = "💚 HEALTHY PULLBACK: RSI resetting below 55 - potential accumulation opportunity"
        
        # Rule: SWEET_SPOT (opportunity)
        elif in_zone and zone_visits >= 5:
            trend_health = "healthy"
            rule = IndicatorRule(
                name="SWEET_SPOT",
                fired=True,
                points=-10,
                description="Sweet spot - RSI in 55-70 accumulation zone",
            )
            rules_fired.append(rule)
            opportunity_points = 10
            direction = IndicatorDirection.OPPORTUNITY
            alert = "💚 SWEET SPOT: RSI in 55-70 accumulation zone - institutions buying dips"
        
        elif in_zone:
            trend_health = "healthy"
            alert = "✅ ACCUMULATION ZONE: RSI in healthy range - trend alive but not crowded"
        
        elif current_rsi > 70 and zone_visits < 3:
            trend_health = "elevated"
            risk_points = 5
            alert = "⚠️ ELEVATED: RSI above 70 with few pullbacks - watch for overheating"
        
        return IndicatorResult(
            name="RSI_ACCUMULATION_ZONE_HEALTH",
            category=IndicatorCategory.MOMENTUM,
            timeframe=IndicatorTimeframe.DAILY,
            direction=direction,
            evidence={
                "current_rsi": current_rsi,
                "days_since_zone": days_since_zone,
                "zone_visits_last_20d": zone_visits,
                "trend_health": trend_health,
            },
            rules_fired=rules_fired,
            risk_points=risk_points,
            opportunity_points=opportunity_points,
            alert=alert,
            why_it_matters="Healthy semi trends repeatedly reset into this band as institutions buy dips.",
        )
    
    @staticmethod
    def analyze_trend_persistence(df: pd.DataFrame, periods: List[int] = [20, 50, 100]) -> IndicatorResult:
        """
        Analyze trend persistence - % time above 50DMA.
        
        Better than crossovers because semiconductor stocks don't always
        cleanly cross 50/200DMA at tops. Instead:
        - Time above 50DMA drops
        - Trend weakens gradually
        - Captures internal erosion
        - Loss of institutional sponsorship
        
        Args:
            df: DataFrame with OHLCV data
            periods: Periods to measure persistence (default [20, 50, 100])
            
        Returns:
            Dict with trend persistence analysis
        """
        if df.empty or len(df) < 50:
            return IndicatorResult(
                name="TREND_PERSISTENCE_ABOVE_50DMA",
                category=IndicatorCategory.TREND,
                timeframe=IndicatorTimeframe.MULTI,
                direction=IndicatorDirection.NEUTRAL,
                evidence={
                    "pct_above_50dma": {},
                    "persistence_declining": False,
                    "trend_strength": "unknown",
                },
                risk_points=0,
                opportunity_points=0,
                alert=None,
                why_it_matters="Tops show internal erosion before the obvious breakdown.",
            )
        
        close = df['Close']
        sma_50 = close.rolling(50).mean()
        
        # Check if currently above 50DMA
        current_above = float(close.iloc[-1]) > float(sma_50.iloc[-1]) if not pd.isna(sma_50.iloc[-1]) else False
        
        # Calculate % time above 50DMA for each period
        pct_above = {}
        for period in periods:
            if len(df) >= period:
                recent_close = close.tail(period)
                recent_sma = sma_50.tail(period)
                
                above_count = sum(1 for i in range(len(recent_close)) 
                                 if not pd.isna(recent_sma.iloc[i]) and recent_close.iloc[i] > recent_sma.iloc[i])
                
                pct = (above_count / period) * 100
                pct_above[f"{period}d"] = float(pct)
        
        # Count consecutive days above/below 50DMA
        days_above = 0
        days_below = 0
        
        for i in range(len(close) - 1, -1, -1):
            if pd.notna(sma_50.iloc[i]):
                if close.iloc[i] > sma_50.iloc[i]:
                    if days_below == 0:
                        days_above += 1
                    else:
                        break
                else:
                    if days_above == 0:
                        days_below += 1
                    else:
                        break
        
        # Detect persistence decline (structural weakening)
        persistence_declining = False
        if "20d" in pct_above and "50d" in pct_above:
            # If recent 20D persistence < longer 50D persistence, trend weakening
            if pct_above["20d"] < pct_above["50d"] - 15:  # 15% threshold
                persistence_declining = True
        
        # Evaluate rules
        rules_fired = []
        risk_points = 0
        direction = IndicatorDirection.NEUTRAL
        trend_strength = "unknown"
        alert = None
        
        if "50d" in pct_above:
            pct_50d = pct_above["50d"]
            
            # Rule: BROKEN_TREND
            if pct_50d < 40:
                trend_strength = "broken"
                rule = IndicatorRule(
                    name="BROKEN_TREND",
                    fired=True,
                    points=30,
                    description="Broken trend - <40% time above 50DMA",
                )
                rules_fired.append(rule)
                risk_points = 30
                direction = IndicatorDirection.RISK
                alert = "🔴 BROKEN TREND: <40% time above 50DMA - structural weakness confirmed"
            
            # Rule: WEAK_TREND
            elif pct_50d < 60:
                trend_strength = "weak"
                rule = IndicatorRule(
                    name="WEAK_TREND",
                    fired=True,
                    points=20,
                    description="Weak trend - <60% time above 50DMA",
                )
                rules_fired.append(rule)
                risk_points = 20
                direction = IndicatorDirection.RISK
                alert = "⚠️ WEAK TREND: <60% time above 50DMA - institutional support fading"
            
            # Rule: DECLINING_PERSISTENCE
            elif pct_50d >= 60 and persistence_declining:
                trend_strength = "healthy"
                rule = IndicatorRule(
                    name="DECLINING_PERSISTENCE",
                    fired=True,
                    points=15,
                    description="Persistence declining - internal erosion beginning",
                )
                rules_fired.append(rule)
                risk_points = 15
                direction = IndicatorDirection.RISK
                alert = "⚠️ WEAKENING: Persistence declining - internal erosion beginning"
            
            elif pct_50d >= 80:
                trend_strength = "strong"
                if not persistence_declining:
                    alert = "💚 STRONG TREND: >80% time above 50DMA - institutional support solid"
            else:
                trend_strength = "healthy"
        
        # Check for sharp decline
        if persistence_declining and "20d" in pct_above and "50d" in pct_above:
            decline_pct = pct_above["50d"] - pct_above["20d"]
            if decline_pct > 25:
                alert = f"🔴 SHARP DECLINE: Persistence dropped {decline_pct:.0f}% - losing institutional sponsorship"
                risk_points = max(risk_points, 25)
        
        return IndicatorResult(
            name="TREND_PERSISTENCE_ABOVE_50DMA",
            category=IndicatorCategory.TREND,
            timeframe=IndicatorTimeframe.MULTI,
            direction=direction,
            evidence={
                "pct_above_50dma": pct_above,
                "persistence_declining": persistence_declining,
                "trend_strength": trend_strength,
            },
            rules_fired=rules_fired,
            risk_points=risk_points,
            opportunity_points=0,
            alert=alert,
            why_it_matters="Tops show internal erosion before the obvious breakdown.",
        )
    
    @staticmethod
    def detect_first_50dma_failure(df: pd.DataFrame, min_uptrend_days: int = 60) -> IndicatorResult:
        """
        Detect first 50DMA failure after long uptrend - cycle turn trigger.
        
        Institutions defend the 50DMA aggressively until they don't.
        When it fails after a long uptrend:
        - It's usually intentional
        - Often marks start of sideways months or sharp corrections
        - In memory stocks, this is the first visible crack
        - First failure matters more than later ones
        
        Args:
            df: DataFrame with OHLCV data
            min_uptrend_days: Minimum days above 50DMA to qualify as "long uptrend" (default 60)
            
        Returns:
            Dict with 50DMA failure analysis
        """
        if df.empty or len(df) < 50:
            return IndicatorResult(
                name="FIRST_50DMA_FAILURE_AFTER_LONG_UPTREND",
                category=IndicatorCategory.TREND,
                timeframe=IndicatorTimeframe.DAILY,
                direction=IndicatorDirection.NEUTRAL,
                evidence={
                    "currently_below_50dma": False,
                    "days_in_current_streak": 0,
                    "previous_uptrend_days": 0,
                    "is_first_failure": False,
                    "failure_severity": "none",
                },
                risk_points=0,
                opportunity_points=0,
                alert=None,
                why_it_matters="Institutions defend 50DMA until they don't; first failure after long defense is meaningful.",
            )
        
        close = df['Close']
        sma_50 = close.rolling(50).mean()
        
        # Track current position
        currently_below = False
        if not pd.isna(sma_50.iloc[-1]):
            currently_below = float(close.iloc[-1]) < float(sma_50.iloc[-1])
        
        # Count days in current streak (above or below)
        days_in_streak = 0
        is_below_streak = currently_below
        
        for i in range(len(close) - 1, -1, -1):
            if pd.notna(sma_50.iloc[i]):
                below = close.iloc[i] < sma_50.iloc[i]
                if below == is_below_streak:
                    days_in_streak += 1
                else:
                    break
        
        # If currently below, count how long the previous uptrend was
        previous_uptrend_days = 0
        if currently_below and days_in_streak > 0:
            # Start from where current below streak began
            start_idx = len(close) - days_in_streak - 1
            
            # Count backwards to find length of previous uptrend
            for i in range(start_idx, -1, -1):
                if pd.notna(sma_50.iloc[i]):
                    if close.iloc[i] > sma_50.iloc[i]:
                        previous_uptrend_days += 1
                    else:
                        break
        
        # Determine if this is a "first failure" after long uptrend
        is_first_failure = False
        failure_severity = "none"
        
        if currently_below and previous_uptrend_days >= min_uptrend_days:
            # Check if this is truly the FIRST failure (no other failures in the uptrend)
            # Look back through the uptrend period for any prior breaks
            uptrend_start_idx = len(close) - days_in_streak - previous_uptrend_days
            uptrend_end_idx = len(close) - days_in_streak
            
            had_prior_breaks = False
            if uptrend_start_idx >= 0:
                for i in range(uptrend_start_idx, uptrend_end_idx):
                    if pd.notna(sma_50.iloc[i]):
                        if close.iloc[i] < sma_50.iloc[i]:
                            had_prior_breaks = True
                            break
            
            if not had_prior_breaks:
                is_first_failure = True
                
                # Determine severity based on uptrend length and break duration
                if previous_uptrend_days >= 120:
                    failure_severity = "critical"
                elif previous_uptrend_days >= 90:
                    failure_severity = "severe"
                else:
                    failure_severity = "significant"
        
        # Evaluate rules
        rules_fired = []
        risk_points = 0
        direction = IndicatorDirection.NEUTRAL
        alert = None
        
        # Rule: FIRST_FAILURE_120D
        if is_first_failure and previous_uptrend_days >= 120:
            rule = IndicatorRule(
                name="FIRST_FAILURE_120D",
                fired=True,
                points=40,
                description=f"First 50DMA failure after {previous_uptrend_days} day uptrend",
            )
            rules_fired.append(rule)
            risk_points = 40
            direction = IndicatorDirection.RISK
            alert = f"🔴 CRITICAL: First 50DMA failure after {previous_uptrend_days} day uptrend - cycle turn likely"
        
        # Rule: FIRST_FAILURE_90D
        elif is_first_failure and previous_uptrend_days >= 90:
            rule = IndicatorRule(
                name="FIRST_FAILURE_90D",
                fired=True,
                points=35,
                description=f"First 50DMA failure after {previous_uptrend_days} day uptrend",
            )
            rules_fired.append(rule)
            risk_points = 35
            direction = IndicatorDirection.RISK
            alert = f"🔴 SEVERE: First 50DMA failure after {previous_uptrend_days} day uptrend - institutions stopped defending"
        
        # Rule: FIRST_FAILURE_60D
        elif is_first_failure and previous_uptrend_days >= 60:
            rule = IndicatorRule(
                name="FIRST_FAILURE_60D",
                fired=True,
                points=30,
                description=f"First 50DMA failure after {previous_uptrend_days} day uptrend",
            )
            rules_fired.append(rule)
            risk_points = 30
            direction = IndicatorDirection.RISK
            alert = f"⚠️ SIGNIFICANT: First 50DMA failure after {previous_uptrend_days} day uptrend - first visible crack"
        
        elif currently_below and previous_uptrend_days >= min_uptrend_days // 2:
            risk_points = 15
            alert = f"⚠️ WATCH: Below 50DMA after {previous_uptrend_days} day uptrend - monitor for trend change"
        
        return IndicatorResult(
            name="FIRST_50DMA_FAILURE_AFTER_LONG_UPTREND",
            category=IndicatorCategory.TREND,
            timeframe=IndicatorTimeframe.DAILY,
            direction=direction,
            evidence={
                "currently_below_50dma": currently_below,
                "days_in_current_streak": days_in_streak,
                "previous_uptrend_days": previous_uptrend_days,
                "is_first_failure": is_first_failure,
                "failure_severity": failure_severity,
            },
            rules_fired=rules_fired,
            risk_points=risk_points,
            opportunity_points=0,
            alert=alert,
            why_it_matters="Institutions defend 50DMA until they don't; first failure after long defense is meaningful.",
        )
    
    @staticmethod
    def analyze_atr_expansion(
        df: pd.DataFrame,
        window: int = 14,
        baseline: int = 50,
    ) -> IndicatorResult:
        """
        Analyze ATR expansion near highs - distribution signature.
        
        Why this works for semiconductors:
        - Early-cycle semis trend with contained ATR (orderly institutional accumulation)
        - Late-cycle/peak behavior is choppy because institutions exit in size
        - ATR expansion at/near highs is frequently distribution, not "healthy volatility"
        
        Args:
            df: DataFrame with OHLCV data
            window: ATR calculation window (default 14)
            baseline: Baseline window for ATR comparison (default 50)
            
        Returns:
            Dict with ATR expansion analysis including:
            - atr_14: Current ATR value
            - atr_pct_of_price: ATR as % of current price
            - atr_zscore: Z-score vs baseline period
            - atr_expanding: Boolean if ATR is expanding
            - risk_points: 0-25 based on expansion at highs
            - opportunity_points: 0-10 if ATR contained in uptrend
            - alert: Alert message
            - why_this_matters: Explanation text
        """
        if df.empty or len(df) < baseline:
            return IndicatorResult(
                name="ATR_EXPANSION_AT_HIGHS",
                category=IndicatorCategory.VOLATILITY,
                timeframe=IndicatorTimeframe.DAILY,
                direction=IndicatorDirection.NEUTRAL,
                evidence={
                    "atr_14": 0.0,
                    "atr_pct_price": 0.0,
                    "atr_zscore_60d": 0.0,
                    "near_highs": 0.0,
                },
                risk_points=0,
                opportunity_points=0,
                alert=None,
                why_it_matters="Late-cycle exits widen ranges; it's often distribution.",
            )
        
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        # Calculate True Range
        prev_close = close.shift(1)
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate ATR
        atr = true_range.rolling(window).mean()
        current_atr = float(atr.iloc[-1]) if not pd.isna(atr.iloc[-1]) else 0.0
        
        # ATR as % of price
        current_price = float(close.iloc[-1])
        atr_pct = (current_atr / current_price * 100) if current_price > 0 else 0.0
        
        # Calculate ATR Z-score vs baseline
        baseline_atr = atr.tail(baseline)
        atr_mean = float(baseline_atr.mean())
        atr_std = float(baseline_atr.std())
        
        atr_zscore = ((current_atr - atr_mean) / atr_std) if atr_std > 0 else 0.0
        
        # Check if ATR is expanding
        atr_expanding = atr_zscore > SemiconductorIndicators.ATR_EXPANSION_THRESHOLD
        
        # Calculate position vs 20D high
        high_20d = high.rolling(20).max()
        position_vs_high = float(close.iloc[-1] / high_20d.iloc[-1]) if not pd.isna(high_20d.iloc[-1]) else 0.0
        
        # Evaluate rules
        rules_fired = []
        risk_points = 0
        opportunity_points = 0
        direction = IndicatorDirection.NEUTRAL
        alert = None
        
        # Rule: ATR_SPIKE_NEAR_HIGHS
        if atr_expanding and position_vs_high > 0.95:
            if atr_zscore > 2.0:
                rule = IndicatorRule(
                    name="ATR_SPIKE_NEAR_HIGHS",
                    fired=True,
                    points=25,
                    description=f"ATR expanding sharply (Z={atr_zscore:.1f}) at highs",
                )
                rules_fired.append(rule)
                risk_points = 25
                direction = IndicatorDirection.RISK
                alert = f"🔴 CRITICAL: ATR expanding sharply (Z={atr_zscore:.1f}) at {position_vs_high:.1%} of 20D high - distribution risk"
            else:
                rule = IndicatorRule(
                    name="ATR_SPIKE_NEAR_HIGHS",
                    fired=True,
                    points=20,
                    description=f"ATR expanding (Z={atr_zscore:.1f}) near highs",
                )
                rules_fired.append(rule)
                risk_points = 20
                direction = IndicatorDirection.RISK
                alert = f"⚠️ WARNING: ATR expanding (Z={atr_zscore:.1f}) near highs - unstable at altitude"
        
        # Rule: ATR_EXTREME
        elif atr_pct > 6.0 and position_vs_high > 0.95:
            rule = IndicatorRule(
                name="ATR_EXTREME",
                fired=True,
                points=15,
                description=f"ATR at {atr_pct:.1f}% of price near highs",
            )
            rules_fired.append(rule)
            risk_points = 15
            direction = IndicatorDirection.RISK
            alert = f"⚠️ ELEVATED: ATR at {atr_pct:.1f}% of price near highs - choppy institutional activity"
        
        elif atr_pct > 4.0 and position_vs_high > 0.95:
            risk_points = 10
            alert = f"⚠️ WATCH: ATR elevated at {atr_pct:.1f}% near highs - monitor for distribution"
        
        elif atr_zscore < -0.5 and position_vs_high > 0.90:
            opportunity_points = 10
            alert = f"💚 CONTAINED: ATR low (Z={atr_zscore:.1f}) in uptrend - orderly accumulation"
        
        return IndicatorResult(
            name="ATR_EXPANSION_AT_HIGHS",
            category=IndicatorCategory.VOLATILITY,
            timeframe=IndicatorTimeframe.DAILY,
            direction=direction,
            evidence={
                "atr_14": current_atr,
                "atr_pct_price": atr_pct,
                "atr_zscore_60d": atr_zscore,
                "near_highs": position_vs_high,
            },
            rules_fired=rules_fired,
            risk_points=risk_points,
            opportunity_points=opportunity_points,
            alert=alert,
            why_it_matters="Late-cycle exits widen ranges; it's often distribution.",
        )
    
    @staticmethod
    def analyze_ma_extension(
        df: pd.DataFrame,
        ma_windows: tuple = (21, 50, 200),
    ) -> IndicatorResult:
        """
        Analyze distance from moving averages - rubber-band risk.
        
        Why this matters for semiconductors:
        - Semi cycles create mean reversion snaps
        - Extreme extension tends to revert even if fundamentals remain strong
        - Memory stocks: extension reverts harder than other semis
        
        Args:
            df: DataFrame with OHLCV data
            ma_windows: MA periods to check (default 21, 50, 200)
            
        Returns:
            Dict with MA extension analysis including:
            - pct_above_21dma, pct_above_50dma, pct_above_200dma
            - extension_level: normal/elevated/extreme
            - risk_points: 0-25 based on extension severity
            - opportunity_points: 0-10 if near MAs in uptrend
            - alert: Alert message
            - why_this_matters: Explanation text
        """
        if df.empty or len(df) < 21:
            return IndicatorResult(
                name="MA_EXTENSION_RISK",
                category=IndicatorCategory.TREND,
                timeframe=IndicatorTimeframe.DAILY,
                direction=IndicatorDirection.NEUTRAL,
                evidence={
                    "pct_above_21dma": 0.0,
                    "pct_above_50dma": 0.0,
                    "pct_above_200dma": 0.0,
                    "extension_level": "unknown",
                },
                risk_points=0,
                opportunity_points=0,
                alert=None,
                why_it_matters="Semis snap back to trend means; memory snaps hardest.",
            )
        
        close = df['Close']
        current_price = float(close.iloc[-1])
        
        # Calculate extensions
        extensions = {}
        for window in ma_windows:
            if len(close) >= window:
                ma = close.rolling(window).mean()
                ma_val = float(ma.iloc[-1]) if not pd.isna(ma.iloc[-1]) else 0.0
                
                if ma_val > 0:
                    pct_above = ((current_price - ma_val) / ma_val) * 100
                    extensions[f"pct_above_{window}dma"] = pct_above
                else:
                    extensions[f"pct_above_{window}dma"] = 0.0
        
        # Determine extension level based on 50DMA (primary)
        pct_above_50 = extensions.get("pct_above_50dma", None)
        
        # If we don't have 50DMA, use 21DMA as fallback
        if pct_above_50 is None:
            pct_above_50 = extensions.get("pct_above_21dma", 0.0)
        
        max_extension = max(extensions.values()) if extensions else 0.0
        
        # Evaluate rules
        rules_fired = []
        risk_points = 0
        opportunity_points = 0
        direction = IndicatorDirection.NEUTRAL
        extension_level = "normal"
        alert = None
        
        # Rule: EXTENSION_EXTREME
        if pct_above_50 >= SemiconductorIndicators.MA_EXTENSION_EXTREME:
            extension_level = "extreme"
            rule = IndicatorRule(
                name="EXTENSION_EXTREME",
                fired=True,
                points=25,
                description=f"{pct_above_50:.1f}% above 50DMA - extreme extension",
            )
            rules_fired.append(rule)
            risk_points = 25
            direction = IndicatorDirection.RISK
            alert = f"🔴 EXTREME EXTENSION: {pct_above_50:.1f}% above 50DMA - mean reversion snap risk high"
        
        # Rule: EXTENSION_ELEVATED
        elif pct_above_50 >= SemiconductorIndicators.MA_EXTENSION_ELEVATED:
            extension_level = "elevated"
            rule = IndicatorRule(
                name="EXTENSION_ELEVATED",
                fired=True,
                points=15,
                description=f"{pct_above_50:.1f}% above 50DMA - elevated extension",
            )
            rules_fired.append(rule)
            risk_points = 15
            direction = IndicatorDirection.RISK
            alert = f"⚠️ ELEVATED EXTENSION: {pct_above_50:.1f}% above 50DMA - rubber-band risk building"
        
        elif pct_above_50 >= 10.0:
            extension_level = "moderate"
            risk_points = 5
            alert = f"⚠️ MODERATE EXTENSION: {pct_above_50:.1f}% above 50DMA - monitor for reversion"
        
        elif -5.0 <= pct_above_50 <= 5.0 and pct_above_50 > 0:
            extension_level = "normal"
            opportunity_points = 10
            alert = f"💚 HEALTHY: Price near 50DMA (+{pct_above_50:.1f}%) - good risk/reward"
        
        elif pct_above_50 < -10.0:
            extension_level = "compressed"
            opportunity_points = 5
            alert = f"💚 COMPRESSED: {abs(pct_above_50):.1f}% below 50DMA - potential mean reversion up"
        
        return IndicatorResult(
            name="MA_EXTENSION_RISK",
            category=IndicatorCategory.TREND,
            timeframe=IndicatorTimeframe.DAILY,
            direction=direction,
            evidence={
                "pct_above_21dma": extensions.get("pct_above_21dma", None),
                "pct_above_50dma": extensions.get("pct_above_50dma", None),
                "pct_above_200dma": extensions.get("pct_above_200dma", None),
                "extension_level": extension_level,
            },
            rules_fired=rules_fired,
            risk_points=risk_points,
            opportunity_points=opportunity_points,
            alert=alert,
            why_it_matters="Semis snap back to trend means; memory snaps hardest.",
        )
    
    @staticmethod
    def analyze_vol_regime(
        df: pd.DataFrame,
        window: int = 20,
        baseline: int = 120,
    ) -> IndicatorResult:
        """
        Analyze volatility regime shift - detect rising volatility near highs.
        
        Why this matters for semiconductors:
        - Semis are crowded trades in upcycles
        - When volatility rises while price is near highs, it often means:
          * "Two-way trade" begins (distribution)
          * Risk premium rises (market senses a turning point)
        
        Args:
            df: DataFrame with OHLCV data
            window: Volatility calculation window (default 20)
            baseline: Baseline window for comparison (default 120)
            
        Returns:
            Dict with volatility regime analysis including:
            - vol_20_ann: 20-day annualized volatility
            - vol_baseline: Baseline volatility
            - vol_ratio: Current vol / baseline vol
            - regime: low/medium/high
            - risk_points: 0-25 based on vol expansion at highs
            - opportunity_points: 0-10 if low vol in uptrend
            - alert: Alert message
            - why_this_matters: Explanation text
        """
        if df.empty or len(df) < baseline:
            return IndicatorResult(
                name="VOLATILITY_REGIME_SHIFT",
                category=IndicatorCategory.VOLATILITY,
                timeframe=IndicatorTimeframe.DAILY,
                direction=IndicatorDirection.NEUTRAL,
                evidence={
                    "vol_20_ann": 0.0,
                    "vol_baseline_120": 0.0,
                    "vol_ratio": 0.0,
                    "regime": "unknown",
                },
                risk_points=0,
                opportunity_points=0,
                alert=None,
                why_it_matters="Rising vol at highs means two-way institutional trade; trend stability is breaking.",
            )
        
        close = df['Close']
        high = df['High']
        
        # Calculate returns
        returns = close.pct_change().dropna()
        
        # Calculate 20-day annualized volatility
        vol_20 = returns.tail(window).std() * np.sqrt(252)
        vol_20_ann = float(vol_20) if not pd.isna(vol_20) else 0.0
        
        # Calculate baseline volatility
        vol_baseline_series = returns.tail(baseline).std() * np.sqrt(252)
        vol_baseline = float(vol_baseline_series) if not pd.isna(vol_baseline_series) else 0.0
        
        # Calculate volatility ratio
        vol_ratio = (vol_20_ann / vol_baseline) if vol_baseline > 0 else 1.0
        
        # Calculate position vs 20D high
        high_20d = high.rolling(20).max()
        position_vs_high = float(close.iloc[-1] / high_20d.iloc[-1]) if not pd.isna(high_20d.iloc[-1]) else 0.0
        
        # Evaluate rules
        rules_fired = []
        risk_points = 0
        opportunity_points = 0
        direction = IndicatorDirection.NEUTRAL
        regime = "medium"
        alert = None
        
        # Rule: HIGH_VOL_AT_HIGHS
        if vol_ratio >= SemiconductorIndicators.VOL_REGIME_HIGH_THRESHOLD and position_vs_high > 0.95:
            regime = "high"
            rule = IndicatorRule(
                name="HIGH_VOL_AT_HIGHS",
                fired=True,
                points=25,
                description=f"High volatility ({vol_ratio:.1f}x) at {position_vs_high:.1%} of highs",
            )
            rules_fired.append(rule)
            risk_points = 25
            direction = IndicatorDirection.RISK
            alert = f"🔴 HIGH VOL REGIME: Volatility {vol_ratio:.1f}x baseline at {position_vs_high:.1%} of highs - two-way trade beginning"
        
        # Rule: VOL_SPIKE
        elif vol_ratio >= SemiconductorIndicators.VOL_REGIME_HIGH_THRESHOLD:
            regime = "high"
            if position_vs_high > 0.90:
                rule = IndicatorRule(
                    name="VOL_SPIKE",
                    fired=True,
                    points=20,
                    description=f"Volatility spike ({vol_ratio:.1f}x) near highs",
                )
                rules_fired.append(rule)
                risk_points = 20
                direction = IndicatorDirection.RISK
                alert = f"⚠️ VOL EXPANDING: Volatility {vol_ratio:.1f}x baseline near highs - risk premium rising"
            else:
                risk_points = 10
                alert = f"⚠️ ELEVATED VOL: Volatility {vol_ratio:.1f}x baseline - monitor for instability"
        
        elif vol_ratio >= 1.1 and position_vs_high > 0.95:
            regime = "medium-high"
            risk_points = 15
            alert = f"⚠️ VOL RISING: Volatility {vol_ratio:.1f}x baseline at highs - early distribution signal"
        
        elif vol_ratio <= 0.8 and position_vs_high > 0.90:
            regime = "low"
            opportunity_points = 10
            alert = f"💚 LOW VOL UPTREND: Volatility {vol_ratio:.1f}x baseline - orderly accumulation"
        
        return IndicatorResult(
            name="VOLATILITY_REGIME_SHIFT",
            category=IndicatorCategory.VOLATILITY,
            timeframe=IndicatorTimeframe.DAILY,
            direction=direction,
            evidence={
                "vol_20_ann": vol_20_ann,
                "vol_baseline_120": vol_baseline,
                "vol_ratio": vol_ratio,
                "regime": regime,
            },
            rules_fired=rules_fired,
            risk_points=risk_points,
            opportunity_points=opportunity_points,
            alert=alert,
            why_it_matters="Rising vol at highs means two-way institutional trade; trend stability is breaking.",
        )
    
    @staticmethod
    def analyze_semiconductor_cycle_risk(
        ticker: str,
        df: pd.DataFrame,
        current_price: float,
    ) -> Dict[str, any]:
        """
        Comprehensive semiconductor cycle risk analysis.
        
        Args:
            ticker: Stock ticker
            df: OHLCV DataFrame
            current_price: Current stock price
            
        Returns:
            Dict with cycle risk analysis
        """
        # Collect all indicator results (now IndicatorResult objects)
        rsi_analysis = SemiconductorIndicators.calculate_rsi_trend(df)
        exhaustion_analysis = SemiconductorIndicators.calculate_exhaustion_signal(df)
        divergence_analysis = SemiconductorIndicators.detect_rsi_divergence(df)
        roc_compression_analysis = SemiconductorIndicators.detect_roc_compression(df)
        accumulation_zone_analysis = SemiconductorIndicators.analyze_rsi_accumulation_zone(df)
        trend_persistence_analysis = SemiconductorIndicators.analyze_trend_persistence(df)
        dma_failure_analysis = SemiconductorIndicators.detect_first_50dma_failure(df)
        atr_expansion_analysis = SemiconductorIndicators.analyze_atr_expansion(df)
        ma_extension_analysis = SemiconductorIndicators.analyze_ma_extension(df)
        vol_regime_analysis = SemiconductorIndicators.analyze_vol_regime(df)
        
        is_memory = SemiconductorIndicators.is_memory_stock(ticker)
        
        # Collect all IndicatorResult objects
        all_indicators = [
            rsi_analysis,
            exhaustion_analysis,
            divergence_analysis,
            roc_compression_analysis,
            accumulation_zone_analysis,
            trend_persistence_analysis,
            dma_failure_analysis,
            atr_expansion_analysis,
            ma_extension_analysis,
            vol_regime_analysis,
        ]
        
        # Aggregate risk and opportunity points
        total_risk_points = 0
        total_opportunity_points = 0
        
        weight = 1.0 if is_memory else 0.7
        
        for indicator in all_indicators:
            total_risk_points += indicator.risk_points * weight
            total_opportunity_points += indicator.opportunity_points * weight
        
        # Calculate net cycle pressure (risk - opportunity)
        cycle_risk_score = total_risk_points - total_opportunity_points
        
        risk_level = "low"
        if cycle_risk_score >= 50:
            risk_level = "critical"
        elif cycle_risk_score >= 30:
            risk_level = "high"
        elif cycle_risk_score >= 15:
            risk_level = "medium"
        
        # Use DriverSelector to identify top drivers
        from features.indicator_result import DriverSelector
        drivers = DriverSelector.select_drivers(
            all_indicators,
            max_risk_drivers=3,
            max_opportunity_drivers=1,
            min_opportunity_threshold=10,
        )
        driver_summary = DriverSelector.format_driver_summary(drivers)
        
        return {
            "ticker": ticker,
            "is_memory_stock": is_memory,
            "rsi_analysis": rsi_analysis,
            "exhaustion_analysis": exhaustion_analysis,
            "divergence_analysis": divergence_analysis,
            "roc_compression_analysis": roc_compression_analysis,
            "accumulation_zone_analysis": accumulation_zone_analysis,
            "trend_persistence_analysis": trend_persistence_analysis,
            "dma_failure_analysis": dma_failure_analysis,
            "atr_expansion_analysis": atr_expansion_analysis,
            "ma_extension_analysis": ma_extension_analysis,
            "vol_regime_analysis": vol_regime_analysis,
            "total_risk_points": total_risk_points,
            "total_opportunity_points": total_opportunity_points,
            "cycle_risk_score": cycle_risk_score,
            "risk_level": risk_level,
            "risk_drivers": drivers["risk_drivers"],
            "opportunity_drivers": drivers["opportunity_drivers"],
            "driver_summary": driver_summary,
            "recommendations": SemiconductorIndicators._generate_cycle_recommendations(
                cycle_risk_score, rsi_analysis, exhaustion_analysis, divergence_analysis, 
                roc_compression_analysis, accumulation_zone_analysis, trend_persistence_analysis, 
                dma_failure_analysis, atr_expansion_analysis, ma_extension_analysis, vol_regime_analysis, is_memory
            ),
        }
    
    @staticmethod
    def _generate_cycle_recommendations(
        cycle_risk_score: int,
        rsi_analysis: 'IndicatorResult',
        exhaustion_analysis: 'IndicatorResult',
        divergence_analysis: 'IndicatorResult',
        roc_compression_analysis: 'IndicatorResult',
        accumulation_zone_analysis: 'IndicatorResult',
        trend_persistence_analysis: 'IndicatorResult',
        dma_failure_analysis: 'IndicatorResult',
        atr_expansion_analysis: 'IndicatorResult',
        ma_extension_analysis: 'IndicatorResult',
        vol_regime_analysis: 'IndicatorResult',
        is_memory: bool,
    ) -> List[str]:
        """Generate actionable recommendations based on cycle risk."""
        recommendations = []
        
        if cycle_risk_score >= 50:
            recommendations.append("Consider trimming position or taking profits")
            recommendations.append("Set tight stop-loss levels")
            if is_memory:
                recommendations.append("Memory stocks often correct sharply after sustained RSI > 75")
        elif cycle_risk_score >= 30:
            recommendations.append("Monitor closely for topping signals")
            recommendations.append("Consider scaling out partially")
        elif cycle_risk_score >= 15:
            recommendations.append("Watch for RSI divergence with price")
        
        # 50DMA failure recommendations (highest priority - check first)
        if dma_failure_analysis.evidence.get("is_first_failure", False):
            if dma_failure_analysis.evidence.get("failure_severity") == "critical":
                recommendations.insert(0, "CRITICAL: First 50DMA failure after 120+ day uptrend - cycle turn confirmed")
                recommendations.insert(1, "Exit positions; institutions have stopped defending - expect sideways/correction")
                if is_memory:
                    recommendations.insert(2, "Memory stocks: This is the first visible crack - sharp correction likely")
            else:
                recommendations.insert(0, "First 50DMA failure detected - institutions stopped defending trend")
                recommendations.insert(1, "Reduce exposure significantly; expect sideways months or correction")
        elif dma_failure_analysis.evidence.get("currently_below_50dma", False) and dma_failure_analysis.evidence.get("previous_uptrend_days", 0) >= 30:
            recommendations.append("Below 50DMA after uptrend - monitor for trend change")
            recommendations.append("Wait for reclaim of 50DMA before adding exposure")
        
        # Trend persistence recommendations
        if trend_persistence_analysis.evidence.get("trend_strength") == "broken":
            recommendations.append("Trend broken - <40% time above 50DMA confirms structural weakness")
            recommendations.append("Institutional support lost; exit remaining positions")
        elif trend_persistence_analysis.evidence.get("trend_strength") == "weak":
            recommendations.append("Trend weakening - persistence declining below 60%")
            recommendations.append("Reduce exposure; institutional sponsorship fading")
        elif trend_persistence_analysis.evidence.get("persistence_declining", False):
            recommendations.append("Persistence declining - internal erosion detected")
            recommendations.append("Monitor closely; trend durability deteriorating")
        
        # Accumulation zone recommendations
        if accumulation_zone_analysis.evidence.get("trend_health") == "healthy":
            recommendations.append("RSI in sweet spot (55-70) - institutions buying dips")
            recommendations.append("Risk/reward favorable for adding on pullbacks")
        elif accumulation_zone_analysis.evidence.get("trend_health") == "overheated":
            recommendations.append("RSI overheated - trend crowded, wait for pullback to 55-70")
        elif accumulation_zone_analysis.evidence.get("trend_health") == "broken":
            recommendations.append("Trend broken - RSI can't recover to accumulation zone")
            recommendations.append("Institutional support fading; reduce exposure")
        elif accumulation_zone_analysis.evidence.get("trend_health") == "pullback":
            recommendations.append("Healthy pullback - RSI resetting for next leg")
            recommendations.append("Watch for re-entry if RSI returns to 55-70 zone")
        
        if roc_compression_analysis.evidence.get("severity") in ["severe", "moderate", "mild"]:
            if roc_compression_analysis.evidence.get("severity") == "severe":
                recommendations.append("Severe ROC compression - cycle aging, gains slowing dramatically")
                recommendations.append("Risk/reward skews negative at current altitude")
            else:
                recommendations.append("ROC compression detected - late-cycle conditions emerging")
                recommendations.append("Upside becoming incremental rather than violent")
        
        if divergence_analysis.evidence.get("divergence_type") == "bearish":
            recommendations.append("Bearish divergence detected - momentum decay in progress")
            recommendations.append("Smart money may be exiting; reduce exposure")
            if is_memory:
                recommendations.append("Memory pricing may be flattening despite strong earnings")
        
        if exhaustion_analysis.evidence.get("is_exhausted", False):
            recommendations.append("Exhaustion pattern detected - breakout likely failed")
            recommendations.append("Upside appears capped; watch for distribution")
        
        if divergence_analysis.evidence.get("divergence_type") == "bullish":
            recommendations.append("Bullish divergence detected - potential reversal opportunity")
            recommendations.append("Consider accumulation if other signals align")
        
        if rsi_analysis.evidence.get("weeks_below_25", 0) >= 2:
            recommendations.append("Potential oversold bounce opportunity")
            recommendations.append("Consider accumulation on weakness")
        
        if (trend_persistence_analysis.evidence.get("trend_strength") == "strong" and 
            not trend_persistence_analysis.evidence.get("persistence_declining", False) and 
            not dma_failure_analysis.evidence.get("is_first_failure", False)):
            recommendations.append("Strong trend persistence - >80% time above 50DMA")
            recommendations.append("Institutional support solid; favorable for holding")
        
        # Phase 1 indicator recommendations
        if atr_expansion_analysis.risk_points > 0 and atr_expansion_analysis.evidence.get("near_highs", 0) > 0.95:
            recommendations.append("ATR expanding at highs - distribution signature detected")
            recommendations.append("Institutional exits creating wider ranges; reduce exposure")
        
        if ma_extension_analysis.evidence.get("extension_level") == "extreme":
            pct_above_50 = ma_extension_analysis.evidence.get("pct_above_50dma")
            if pct_above_50:
                recommendations.append(f"Extreme extension ({pct_above_50:.1f}% above 50DMA) - mean reversion snap risk")
                if is_memory:
                    recommendations.append("Memory stocks: extension reverts harder - trim positions")
        
        if vol_regime_analysis.evidence.get("regime") == "high":
            recommendations.append("High volatility regime at highs - two-way trade beginning")
            recommendations.append("Risk premium rising; market sensing turning point")
        
        return recommendations
