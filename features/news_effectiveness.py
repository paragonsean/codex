"""
Good News Effectiveness Analysis - Critical Expectations Peak Detector

Semiconductor peaks are often expectations peaks. The market stops responding 
to positive catalysts because:
- The narrative is fully priced
- Incremental buyers are gone
- Institutions are selling into strength

This is the cleanest "top without bad news" indicator.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from datetime import datetime, timedelta

import pandas as pd
import numpy as np


class GoodNewsEffectivenessAnalyzer:
    """
    Analyzes whether positive news catalysts are still driving price action.
    
    Why this matters for semiconductor cycles:
    - Semiconductor peaks are often expectations peaks
    - The market stops responding to positive catalysts when narrative is fully priced
    - Incremental buyers are gone; institutions selling into strength
    - This is the cleanest "top without bad news" indicator
    """
    
    POSITIVE_SENTIMENT_THRESHOLD = 0.3
    NEGATIVE_SENTIMENT_THRESHOLD = -0.3
    SUCCESS_RETURN_THRESHOLD = 0.01  # 1% positive return = success
    
    @staticmethod
    def analyze_good_news_effectiveness(
        reaction_records: List[any],
        horizon_days: tuple = (1, 2, 3),
        lookback_window: int = 30,
    ) -> Dict[str, any]:
        """
        Analyze good news effectiveness - track when positive catalysts stop working.
        
        Args:
            reaction_records: List of ReactionRecord objects with news and price data
            horizon_days: Forward return horizons to check (default 1, 2, 3 days)
            lookback_window: Days to look back for recent effectiveness (default 30)
            
        Returns:
            Dict with good news effectiveness analysis including:
            - positive_headlines: Count of positive news
            - negative_headlines: Count of negative news
            - good_news_success_rate: % of positive news that drove positive returns
            - consecutive_failures: Consecutive positive news that failed
            - risk_points: 0-35 based on effectiveness breakdown
            - opportunity_points: 0-15 if good news still working well
            - alert: Alert message if effectiveness declining
            - why_this_matters: Explanation text for reports
        """
        if not reaction_records:
            return {
                "positive_headlines": 0,
                "negative_headlines": 0,
                "neutral_headlines": 0,
                "good_news_success_rate": 0.0,
                "bad_news_success_rate": 0.0,
                "consecutive_failures": 0,
                "recent_effectiveness": 0.0,
                "baseline_effectiveness": 0.0,
                "effectiveness_declining": False,
                "risk_points": 0,
                "opportunity_points": 0,
                "alert": None,
                "why_this_matters": "Expectation peaks show up as 'bullish headlines, weak returns.' Narrative saturation; top risk rises materially.",
            }
        
        # Classify headlines by sentiment
        positive_news = []
        negative_news = []
        neutral_news = []
        
        for record in reaction_records:
            sentiment = getattr(record, 'sentiment', 0.0)
            
            if sentiment > GoodNewsEffectivenessAnalyzer.POSITIVE_SENTIMENT_THRESHOLD:
                positive_news.append(record)
            elif sentiment < GoodNewsEffectivenessAnalyzer.NEGATIVE_SENTIMENT_THRESHOLD:
                negative_news.append(record)
            else:
                neutral_news.append(record)
        
        # Analyze good news effectiveness
        good_news_successes = 0
        good_news_total = len(positive_news)
        
        for record in positive_news:
            # Check if any forward return horizon was positive
            success = False
            for horizon in horizon_days:
                forward_return = getattr(record, f'forward_return_{horizon}d', None)
                if forward_return and forward_return > GoodNewsEffectivenessAnalyzer.SUCCESS_RETURN_THRESHOLD:
                    success = True
                    break
            
            if success:
                good_news_successes += 1
        
        good_news_success_rate = (good_news_successes / good_news_total * 100) if good_news_total > 0 else 0.0
        
        # Analyze bad news effectiveness (inverse - bad news should drive negative returns)
        bad_news_successes = 0
        bad_news_total = len(negative_news)
        
        for record in negative_news:
            success = False
            for horizon in horizon_days:
                forward_return = getattr(record, f'forward_return_{horizon}d', None)
                if forward_return and forward_return < -GoodNewsEffectivenessAnalyzer.SUCCESS_RETURN_THRESHOLD:
                    success = True
                    break
            
            if success:
                bad_news_successes += 1
        
        bad_news_success_rate = (bad_news_successes / bad_news_total * 100) if bad_news_total > 0 else 0.0
        
        # Count consecutive failures (recent positive news that didn't work)
        consecutive_failures = 0
        for record in reversed(positive_news):
            failed = True
            for horizon in horizon_days:
                forward_return = getattr(record, f'forward_return_{horizon}d', None)
                if forward_return and forward_return > GoodNewsEffectivenessAnalyzer.SUCCESS_RETURN_THRESHOLD:
                    failed = False
                    break
            
            if failed:
                consecutive_failures += 1
            else:
                break
        
        # Calculate recent vs baseline effectiveness
        cutoff_date = None
        if reaction_records and hasattr(reaction_records[0], 'published_date'):
            latest_date = max(r.published_date for r in reaction_records if hasattr(r, 'published_date'))
            if isinstance(latest_date, datetime):
                cutoff_date = latest_date - timedelta(days=lookback_window)
        
        recent_positive = []
        baseline_positive = []
        
        for record in positive_news:
            if cutoff_date and hasattr(record, 'published_date'):
                if record.published_date >= cutoff_date:
                    recent_positive.append(record)
                else:
                    baseline_positive.append(record)
            else:
                # If no dates, split by position
                if len(recent_positive) < lookback_window:
                    recent_positive.append(record)
                else:
                    baseline_positive.append(record)
        
        # Calculate recent effectiveness
        recent_successes = 0
        for record in recent_positive:
            for horizon in horizon_days:
                forward_return = getattr(record, f'forward_return_{horizon}d', None)
                if forward_return and forward_return > GoodNewsEffectivenessAnalyzer.SUCCESS_RETURN_THRESHOLD:
                    recent_successes += 1
                    break
        
        recent_effectiveness = (recent_successes / len(recent_positive) * 100) if recent_positive else 0.0
        
        # Calculate baseline effectiveness
        baseline_successes = 0
        for record in baseline_positive:
            for horizon in horizon_days:
                forward_return = getattr(record, f'forward_return_{horizon}d', None)
                if forward_return and forward_return > GoodNewsEffectivenessAnalyzer.SUCCESS_RETURN_THRESHOLD:
                    baseline_successes += 1
                    break
        
        baseline_effectiveness = (baseline_successes / len(baseline_positive) * 100) if baseline_positive else 0.0
        
        # Detect effectiveness decline
        effectiveness_declining = False
        if baseline_effectiveness > 0 and recent_effectiveness < baseline_effectiveness - 20:
            effectiveness_declining = True
        
        # Calculate risk and opportunity points
        risk_points = 0
        opportunity_points = 0
        alert = None
        
        if good_news_total >= 5:  # Need minimum sample size
            if good_news_success_rate < 30:
                # Critical: good news barely working
                risk_points = 35
                alert = f"🔴 CRITICAL: Good news effectiveness collapsed to {good_news_success_rate:.0f}% - narrative fully priced"
            elif good_news_success_rate < 50:
                # Severe: good news working less than half the time
                risk_points = 25
                alert = f"🔴 SEVERE: Good news effectiveness declining ({good_news_success_rate:.0f}%) - incremental buyers gone"
            elif consecutive_failures >= 3:
                # Warning: recent string of failures
                risk_points = 20
                alert = f"⚠️ WARNING: {consecutive_failures} consecutive positive news failures - institutions selling into strength"
            elif effectiveness_declining:
                # Caution: effectiveness declining vs baseline
                risk_points = 15
                alert = f"⚠️ DECLINING: Good news effectiveness dropped from {baseline_effectiveness:.0f}% to {recent_effectiveness:.0f}%"
            elif good_news_success_rate >= 75:
                # Opportunity: good news still very effective
                opportunity_points = 15
                alert = f"💚 STRONG: Good news effectiveness at {good_news_success_rate:.0f}% - narrative still driving price"
            elif good_news_success_rate >= 60:
                # Healthy: good news working well
                opportunity_points = 10
                alert = f"✅ HEALTHY: Good news effectiveness at {good_news_success_rate:.0f}% - positive catalysts working"
        
        return {
            "positive_headlines": good_news_total,
            "negative_headlines": bad_news_total,
            "neutral_headlines": len(neutral_news),
            "good_news_success_rate": good_news_success_rate,
            "bad_news_success_rate": bad_news_success_rate,
            "consecutive_failures": consecutive_failures,
            "recent_effectiveness": recent_effectiveness,
            "baseline_effectiveness": baseline_effectiveness,
            "effectiveness_declining": effectiveness_declining,
            "risk_points": risk_points,
            "opportunity_points": opportunity_points,
            "alert": alert,
            "why_this_matters": (
                "Expectation peaks show up as 'bullish headlines, weak returns.' "
                "When positive catalysts stop working, the narrative is fully priced, "
                "incremental buyers are gone, and institutions are selling into strength. "
                "This is the cleanest 'top without bad news' indicator."
            ),
        }
