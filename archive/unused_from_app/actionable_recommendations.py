#!/usr/bin/env python3
"""
actionable_recommendations.py

Generate actionable trading recommendations with specific tiers, reasons, and key levels.
Implements sophisticated recommendation logic based on cycle analysis, news effectiveness,
and technical indicators.

Features:
- Recommendation tiers: HOLD/ADD, HOLD/TAKE PROFITS, TRIM 25-50%, EXIT/RISK OFF, HEDGE
- Top 3 reasons for each recommendation
- Key levels for invalidation/confirmation
- Next review dates
- Portfolio-aware suggestions with rotation targets
"""

import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from advanced_news_interpreter import CycleAnalysis, GoodNewsAnalysis, NewsCatalyst
from dual_scoring_system import DualScores
from market_data_processor import MarketData


@dataclass
class Recommendation:
    """Actionable trading recommendation with detailed reasoning."""
    ticker: str
    tier: str  # "HOLD/ADD", "HOLD/TAKE PROFITS", "TRIM 25-50%", "EXIT/RISK OFF", "HEDGE"
    confidence: float  # 0-1
    urgency: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    top_3_reasons: List[str]
    key_levels: Dict[str, str]  # invalidate/confirm levels
    next_review_date: str
    position_sizing: Optional[str]  # e.g., "Reduce by 25%", "Add 10%"
    hedge_suggestions: Optional[List[str]]


@dataclass
class PortfolioSuggestion:
    """Portfolio-aware rotation and concentration suggestions."""
    concentration_warnings: List[str]
    rotation_targets: List[Dict[str, str]]  # ticker -> reason
    sector_adjustments: List[str]
    timing_guidance: str


class ActionableRecommendationsEngine:
    """Generate actionable trading recommendations with comprehensive analysis."""
    
    def __init__(self):
        # Recommendation thresholds
        self.tier_thresholds = {
            "HOLD/ADD": {"min_score": 70, "max_risk": 30},
            "HOLD/TAKE PROFITS": {"min_score": 50, "max_risk": 50},
            "TRIM 25-50%": {"min_score": 30, "max_risk": 70},
            "EXIT/RISK OFF": {"min_score": 0, "max_risk": 90},
            "HEDGE": {"min_score": 20, "max_risk": 80}
        }
        
        # Semiconductor rotation targets (post-peak opportunities)
        self.rotation_targets = {
            "upstream": ["ASML", "AMAT", "LRCX", "KLAC"],  # Equipment
            "design": ["SNPS", "CDNS", "ADI", "MRVL"],    # Design software
            "testing": ["TER", "COHU"],                    # Testing
            "diversified": ["INTC", "TXN"],               # Diversified
            "packaging": ["ASX", "AMKR"]                  # Packaging
        }
        
        # Memory sector hierarchy for rotation
        self.memory_hierarchy = {
            "highest_risk": ["WDC"],  # NAND-heavy
            "medium_risk": ["MU"],    # Balanced
            "lowest_risk": ["SNDK"]   # More stable
        }
    
    def _get_indicator_value(self, indicators: Dict[str, any], key: str, default: float = 0) -> float:
        """Helper to get scalar value from indicators dict."""
        value = indicators.get(key, default)
        if hasattr(value, 'iloc'):
            return float(value.iloc[-1]) if len(value) > 0 else default
        return float(value) if value is not None else default
    
    def generate_recommendation(self, ticker: str, dual_scores: DualScores,
                               cycle_analysis: CycleAnalysis,
                               good_news_analysis: GoodNewsAnalysis,
                               market_data: MarketData) -> Recommendation:
        """Generate comprehensive actionable recommendation."""
        
        # Determine recommendation tier
        tier, confidence = self._determine_recommendation_tier(
            dual_scores, cycle_analysis, good_news_analysis
        )
        
        # Determine urgency
        urgency = self._determine_urgency(
            dual_scores, cycle_analysis, good_news_analysis
        )
        
        # Generate top 3 reasons
        top_3_reasons = self._generate_top_3_reasons(
            dual_scores, cycle_analysis, good_news_analysis, market_data
        )
        
        # Determine key levels
        key_levels = self._determine_key_levels(market_data, cycle_analysis)
        
        # Calculate next review date
        next_review_date = self._calculate_next_review_date(urgency, cycle_analysis)
        
        # Determine position sizing
        position_sizing = self._determine_position_sizing(tier, market_data)
        
        # Generate hedge suggestions if needed
        hedge_suggestions = self._generate_hedge_suggestions(tier, market_data) if tier == "HEDGE" else None
        
        return Recommendation(
            ticker=ticker,
            tier=tier,
            confidence=confidence,
            urgency=urgency,
            top_3_reasons=top_3_reasons,
            key_levels=key_levels,
            next_review_date=next_review_date,
            position_sizing=position_sizing,
            hedge_suggestions=hedge_suggestions
        )
    
    def generate_portfolio_suggestions(self, recommendations: List[Recommendation],
                                     portfolio_weights: Optional[Dict[str, float]] = None) -> PortfolioSuggestion:
        """Generate portfolio-aware suggestions."""
        concentration_warnings = []
        rotation_targets = []
        sector_adjustments = []
        
        if portfolio_weights:
            # Check concentration
            total_weight = sum(portfolio_weights.values())
            for ticker, weight in portfolio_weights.items():
                if weight / total_weight > 0.25:  # >25% in one position
                    concentration_warnings.append(
                        f"High concentration in {ticker}: {weight/total_weight:.1%}"
                    )
            
            # Memory sector concentration
            memory_weight = sum(portfolio_weights.get(t, 0) for t in ["MU", "WDC", "SNDK"])
            if memory_weight / total_weight > 0.4:  # >40% in memory
                concentration_warnings.append(
                    f"High memory sector concentration: {memory_weight/total_weight:.1%}"
                )
        
        # Generate rotation targets based on sell-risk
        high_risk_tickers = [r.ticker for r in recommendations if r.tier in ["EXIT/RISK OFF", "TRIM 25-50%"]]
        
        for ticker in high_risk_tickers:
            if ticker in self.memory_hierarchy["highest_risk"]:
                # Suggest rotation to upstream or design
                rotation_targets.extend([
                    {"ticker": "ASML", "reason": f"Rotate from {ticker} NAND exposure to equipment"},
                    {"ticker": "SNPS", "reason": f"Rotate from {ticker} to design software"}
                ])
            elif ticker in self.memory_hierarchy["medium_risk"]:
                rotation_targets.extend([
                    {"ticker": "ADI", "reason": f"Rotate from {ticker} to diversified semiconductors"},
                    {"ticker": "INTC", "reason": f"Rotate from {ticker} to established player"}
                ])
        
        # Sector adjustments
        late_cycle_count = sum(1 for r in recommendations 
                               if r.tier in ["EXIT/RISK OFF", "TRIM 25-50%"] and 
                               any(t in r.ticker for t in ["MU", "WDC", "SNDK"]))
        
        if late_cycle_count >= 2:
            sector_adjustments.append("Multiple memory stocks showing peak signals - reduce sector exposure")
            sector_adjustments.append("Consider rotating to upstream equipment or design software")
        
        # Timing guidance
        if high_risk_tickers:
            timing_guidance = "Immediate rotation recommended as multiple peak triggers detected"
        else:
            timing_guidance = "Monitor for additional peak signals before rotating"
        
        return PortfolioSuggestion(
            concentration_warnings=concentration_warnings,
            rotation_targets=rotation_targets[:5],  # Top 5 targets
            sector_adjustments=sector_adjustments,
            timing_guidance=timing_guidance
        )
    
    def _determine_recommendation_tier(self, dual_scores: DualScores,
                                       cycle_analysis: CycleAnalysis,
                                       good_news_analysis: GoodNewsAnalysis) -> Tuple[str, float]:
        """Determine recommendation tier based on all analysis."""
        opportunity_score = dual_scores.opportunity_score
        sell_risk_score = dual_scores.sell_risk_score
        
        # Adjust scores based on cycle analysis
        if cycle_analysis.cycle_phase in ["late", "rollover_risk"]:
            sell_risk_score += 20  # Increase risk in late cycle
        elif cycle_analysis.cycle_phase == "early":
            opportunity_score += 10  # Boost opportunity in early cycle
        
        # Adjust based on good news effectiveness
        if good_news_analysis.alert_triggered:
            sell_risk_score += 25  # Major risk signal
        elif good_news_analysis.effectiveness_score < 30:
            sell_risk_score += 15  # Poor news response
        
        # Determine tier
        if sell_risk_score >= 80:
            return "EXIT/RISK OFF", 0.9
        elif sell_risk_score >= 60:
            return "TRIM 25-50%", 0.8
        elif sell_risk_score >= 40:
            return "HOLD/TAKE PROFITS", 0.6
        elif opportunity_score >= 70 and sell_risk_score < 40:
            return "HOLD/ADD", 0.7
        elif opportunity_score >= 50 and sell_risk_score < 50:
            return "HOLD/ADD", 0.5
        elif sell_risk_score >= 50 and opportunity_score < 30:
            return "HEDGE", 0.6
        else:
            return "HOLD/TAKE PROFITS", 0.4
    
    def _determine_urgency(self, dual_scores: DualScores,
                          cycle_analysis: CycleAnalysis,
                          good_news_analysis: GoodNewsAnalysis) -> str:
        """Determine recommendation urgency."""
        urgency_score = 0
        
        # High urgency triggers
        if good_news_analysis.alert_triggered:
            urgency_score += 40
        if cycle_analysis.phase_transition_risk > 70:
            urgency_score += 30
        if dual_scores.sell_risk_score > 80:
            urgency_score += 30
        
        # Medium urgency triggers
        if cycle_analysis.cycle_phase == "rollover_risk":
            urgency_score += 20
        if good_news_analysis.consecutive_failures >= 2:
            urgency_score += 20
        if dual_scores.sell_risk_score > 60:
            urgency_score += 15
        
        if urgency_score >= 60:
            return "CRITICAL"
        elif urgency_score >= 30:
            return "HIGH"
        elif urgency_score >= 15:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_top_3_reasons(self, dual_scores: DualScores,
                               cycle_analysis: CycleAnalysis,
                               good_news_analysis: GoodNewsAnalysis,
                               market_data: MarketData) -> List[str]:
        """Generate top 3 reasons for recommendation."""
        reasons = []
        
        # Cycle-related reasons
        if cycle_analysis.cycle_phase in ["late", "rollover_risk"]:
            reasons.append(f"Cycle phase: {cycle_analysis.cycle_phase.replace('_', ' ').title()}")
        if cycle_analysis.phase_transition_risk > 60:
            reasons.append(f"High transition risk ({cycle_analysis.phase_transition_risk:.0f}/100)")
        
        # Good news effectiveness reasons
        if good_news_analysis.alert_triggered:
            reasons.append("Good news not working - distribution detected")
        if good_news_analysis.failure_rate > 0.6:
            reasons.append(f"High positive news failure rate ({good_news_analysis.failure_rate:.0%})")
        
        # Technical reasons
        rsi = market_data.indicators.get('rsi_14', 50)
        if rsi > 80:
            reasons.append(f"RSI extremely overbought ({rsi:.1f})")
        elif rsi > 70:
            reasons.append(f"RSI overbought ({rsi:.1f})")
        elif rsi < 30:
            reasons.append(f"RSI oversold ({rsi:.1f})")
        
        # Price momentum reasons
        ret_63d = self._get_indicator_value(market_data.indicators, 'ret_63d', 0)
        if ret_63d > 0.5:
            reasons.append(f"Extended gains ({ret_63d:+.1%})")
        elif ret_63d < -0.3:
            reasons.append(f"Significant losses ({ret_63d:+.1%})")
        
        # Volatility reasons
        vol_20d = self._get_indicator_value(market_data.indicators, 'volatility_20d', 0)
        if vol_20d > 0.5:
            reasons.append(f"High volatility ({vol_20d:.1%})")
        
        # News risk reasons
        if cycle_analysis.news_risk_score > 60:
            reasons.append(f"High news risk score ({cycle_analysis.news_risk_score:.0f})")
        
        # Score-based reasons
        if dual_scores.sell_risk_score > 70:
            reasons.append(f"High sell-risk score ({dual_scores.sell_risk_score:.0f})")
        elif dual_scores.opportunity_score > 70:
            reasons.append(f"High opportunity score ({dual_scores.opportunity_score:.0f})")
        
        return reasons[:3]  # Top 3
    
    def _determine_key_levels(self, market_data: MarketData,
                             cycle_analysis: CycleAnalysis) -> Dict[str, str]:
        """Determine key levels for invalidation and confirmation."""
        levels = {}
        
        current_price = market_data.current_price
        indicators = market_data.indicators
        
        # Support and resistance levels
        if 'high_20d' in indicators and 'low_20d' in indicators:
            levels["support"] = f"${indicators['low_20d']:.2f}"
            levels["resistance"] = f"${indicators['high_20d']:.2f}"
        
        # Moving average levels
        if 'sma_50' in indicators and 'sma_200' in indicators:
            levels["50dma"] = f"${indicators['sma_50']:.2f}"
            levels["200dma"] = f"${indicators['sma_200']:.2f}"
        
        # Invalidation levels
        if cycle_analysis.cycle_phase in ["late", "rollover_risk"]:
            levels["invalidate_sell_risk"] = f"Reclaims 50DMA at ${indicators.get('sma_50', current_price):.2f}"
            levels["confirm_rollover"] = f"Breaks below prior swing low"
        
        # Target levels
        if indicators.get('rsi_14', 50) < 30:
            levels["oversold_target"] = f"RSI recovery above 35"
        
        return levels
    
    def _calculate_next_review_date(self, urgency: str, cycle_analysis: CycleAnalysis) -> str:
        """Calculate next review date based on urgency and cycle phase."""
        today = datetime.now(timezone.utc)
        
        if urgency == "CRITICAL":
            days = 1
        elif urgency == "HIGH":
            days = 3
        elif urgency == "MEDIUM":
            days = 5
        else:
            days = 7
        
        # Adjust for cycle phase
        if cycle_analysis.cycle_phase in ["late", "rollover_risk"]:
            days = min(days, 3)  # More frequent reviews in late cycle
        
        next_review = today + timedelta(days=days)
        return next_review.strftime("%Y-%m-%d")
    
    def _determine_position_sizing(self, tier: str, market_data: MarketData) -> Optional[str]:
        """Determine position sizing recommendations."""
        if tier == "TRIM 25-50%":
            rsi = market_data.indicators.get('rsi_14', 50)
            if rsi > 80:
                return "Reduce by 50% (extremely overbought)"
            elif rsi > 75:
                return "Reduce by 35% (very overbought)"
            else:
                return "Reduce by 25% (take profits)"
        
        elif tier == "HOLD/ADD":
            vol_20d = market_data.indicators.get('volatility_20d', 0)
            if vol_20d < 0.2:
                return "Add 15% (low volatility entry)"
            else:
                return "Add 10% (cautious addition)"
        
        return None
    
    def _generate_hedge_suggestions(self, tier: str, market_data: MarketData) -> List[str]:
        """Generate hedging suggestions."""
        suggestions = []
        
        current_price = market_data.current_price
        
        # Covered calls
        if tier == "HEDGE":
            suggestions.append(f"Covered calls: Sell calls at ${current_price * 1.1:.2f} (10% OTM)")
            suggestions.append(f"Collar: Buy puts at ${current_price * 0.9:.2f}, sell calls at ${current_price * 1.1:.2f}")
        
        # Put spreads
        rsi = market_data.indicators.get('rsi_14', 50)
        if rsi > 70:
            suggestions.append(f"Bear put spread: Protect against 10-15% decline")
        
        # Volatility-based hedges
        vol_20d = market_data.indicators.get('volatility_20d', 0)
        if vol_20d > 0.4:
            suggestions.append("Volatility hedge: Consider straddles or strangles")
        
        return suggestions


def print_recommendation(recommendation: Recommendation):
    """Print detailed recommendation."""
    print(f"\n{'='*80}")
    print(f"🎯 ACTIONABLE RECOMMENDATION - {recommendation.ticker}")
    print(f"{'='*80}")
    
    urgency_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}
    
    print(f"\n📊 RECOMMENDATION:")
    print(f"  Tier: {recommendation.tier}")
    print(f"  Confidence: {recommendation.confidence:.1%}")
    print(f"  Urgency: {urgency_emoji.get(recommendation.urgency, '❓')} {recommendation.urgency}")
    
    if recommendation.position_sizing:
        print(f"  Position Sizing: {recommendation.position_sizing}")
    
    print(f"\n💡 TOP 3 REASONS:")
    for i, reason in enumerate(recommendation.top_3_reasons, 1):
        print(f"  {i}. {reason}")
    
    print(f"\n📍 KEY LEVELS:")
    for level_type, level_value in recommendation.key_levels.items():
        print(f"  {level_type.replace('_', ' ').title()}: {level_value}")
    
    print(f"\n📅 NEXT REVIEW: {recommendation.next_review_date}")
    
    if recommendation.hedge_suggestions:
        print(f"\n🛡️ HEDGE SUGGESTIONS:")
        for suggestion in recommendation.hedge_suggestions:
            print(f"  • {suggestion}")


def print_portfolio_suggestions(suggestions: PortfolioSuggestion):
    """Print portfolio-aware suggestions."""
    print(f"\n{'='*80}")
    print(f"📚 PORTFOLIO SUGGESTIONS")
    print(f"{'='*80}")
    
    if suggestions.concentration_warnings:
        print(f"\n⚠️  CONCENTRATION WARNINGS:")
        for warning in suggestions.concentration_warnings:
            print(f"  • {warning}")
    
    if suggestions.rotation_targets:
        print(f"\n🔄 ROTATION TARGETS:")
        for target in suggestions.rotation_targets:
            print(f"  • {target['ticker']}: {target['reason']}")
    
    if suggestions.sector_adjustments:
        print(f"\n📊 SECTOR ADJUSTMENTS:")
        for adjustment in suggestions.sector_adjustments:
            print(f"  • {adjustment}")
    
    print(f"\n⏰ TIMING GUIDANCE:")
    print(f"  {suggestions.timing_guidance}")


def main():
    """Demonstrate actionable recommendations."""
    import argparse
    from advanced_news_interpreter import AdvancedNewsInterpreter
    from dual_scoring_system import DualScoringSystem
    from test_dual_scoring import create_mock_market_data
    
    parser = argparse.ArgumentParser(description="Actionable recommendations")
    parser.add_argument("tickers", nargs="+", help="Tickers to analyze")
    parser.add_argument("--portfolio", help="Portfolio weights JSON file")
    
    args = parser.parse_args()
    
    # Load portfolio weights if provided
    portfolio_weights = {}
    if args.portfolio:
        try:
            import json
            with open(args.portfolio, 'r') as f:
                portfolio_data = json.load(f)
            portfolio_weights = {pos['ticker']: pos['shares'] for pos in portfolio_data.get('positions', [])}
        except Exception as e:
            print(f"Warning: Could not load portfolio file: {e}")
    
    engine = ActionableRecommendationsEngine()
    
    for ticker in args.tickers:
        try:
            # Create mock data for demonstration
            market_data = create_mock_market_data(ticker)
            
            # Create mock analysis results
            from dual_scoring_system import DualScores
            from advanced_news_interpreter import CycleAnalysis, GoodNewsAnalysis
            
            dual_scores = DualScores(
                ticker=ticker,
                opportunity_score=45.0,
                sell_risk_score=75.0,
                opportunity_clusters=[],
                sell_risk_clusters=[],
                overall_bias="SELL",
                confidence=0.7,
                timestamp=datetime.now().isoformat(),
                key_factors=[]
            )
            
            cycle_analysis = CycleAnalysis(
                ticker=ticker,
                cycle_phase="late",
                cycle_confidence=0.8,
                cycle_indicators={},
                news_risk_score=65.0,
                good_news_effectiveness=25.0,
                key_cycle_signals=["RSI overbought", "Extended gains", "Negative cycle keywords"],
                phase_transition_risk=75.0
            )
            
            good_news_analysis = GoodNewsAnalysis(
                ticker=ticker,
                positive_headlines=[],
                forward_return_analysis={},
                effectiveness_score=20.0,
                failure_rate=0.8,
                consecutive_failures=3,
                distribution_signals=["Positive headline failed"],
                alert_triggered=True
            )
            
            # Generate recommendation
            recommendation = engine.generate_recommendation(
                ticker, dual_scores, cycle_analysis, good_news_analysis, market_data
            )
            
            print_recommendation(recommendation)
            
        except Exception as e:
            print(f"❌ Error processing {ticker}: {e}")
    
    # Generate portfolio suggestions if portfolio provided
    if portfolio_weights:
        # Mock recommendations for portfolio analysis
        mock_recommendations = []
        for ticker in args.tickers:
            mock_recommendations.append(Recommendation(
                ticker=ticker,
                tier="TRIM 25-50%",
                confidence=0.7,
                urgency="HIGH",
                top_3_reasons=["Cycle phase: Late", "High sell-risk score", "Good news not working"],
                key_levels={"support": "$350.00", "resistance": "$400.00"},
                next_review_date="2026-01-27",
                position_sizing="Reduce by 25%",
                hedge_suggestions=[]
            ))
        
        portfolio_suggestions = engine.generate_portfolio_suggestions(
            mock_recommendations, portfolio_weights
        )
        
        print_portfolio_suggestions(portfolio_suggestions)


if __name__ == "__main__":
    main()
