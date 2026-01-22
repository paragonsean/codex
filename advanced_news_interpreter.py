#!/usr/bin/env python3
"""
advanced_news_interpreter.py

Advanced news interpretation system that treats headlines as catalysts and risk flags.
Implements sophisticated news risk scoring, cycle detection, and "good news not working" analysis.

Features:
- News risk scoring based on quality, impact, and category weighting
- Cycle peak detection for semiconductor/memory stocks
- "Good news not working" detection using forward returns
- Catalyst and risk flag identification
- Late-cycle froth detection
"""

import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from news import Headline, fetch_headlines_for_ticker
from market_data_processor import MarketData


@dataclass
class NewsCatalyst:
    """Represents a news catalyst with risk assessment."""
    headline: Headline
    catalyst_type: str  # "positive_catalyst", "negative_catalyst", "risk_flag"
    news_risk_score: float  # 0-100
    cycle_relevance: float  # 0-100, how relevant to cycle analysis
    forward_returns: Dict[str, float]  # 1d, 2d, 3d forward returns
    price_reaction: str  # "strong_positive", "weak_positive", "neutral", "negative"


@dataclass
class CycleAnalysis:
    """Cycle phase analysis for semiconductor/memory stocks."""
    ticker: str
    cycle_phase: str  # "early", "mid", "late-mid", "late", "rollover_risk"
    cycle_confidence: float  # 0-1
    cycle_indicators: Dict[str, float]
    news_risk_score: float  # 0-100
    good_news_effectiveness: float  # 0-100, lower = worse
    key_cycle_signals: List[str]
    phase_transition_risk: float  # 0-100


@dataclass
class GoodNewsAnalysis:
    """Analysis of "good news not working" phenomenon."""
    ticker: str
    positive_headlines: List[Headline]
    forward_return_analysis: Dict[str, float]
    effectiveness_score: float  # 0-100, lower = distribution detected
    failure_rate: float  # % of positive news with negative/flat returns
    consecutive_failures: int
    distribution_signals: List[str]
    alert_triggered: bool


class AdvancedNewsInterpreter:
    """Advanced news interpretation with catalyst and cycle analysis."""
    
    def __init__(self):
        # Category weights for news risk scoring
        self.category_weights = {
            "earnings": 1.0,      # Highest weight
            "guidance": 0.9,     # Very high weight
            "financial": 0.8,    # High weight
            "legal": 0.7,        # Medium-high weight
            "mergers": 0.6,      # Medium weight
            "operations": 0.5,   # Medium-low weight
            "products": 0.4,     # Lower weight
            "market": 0.3        # Lowest weight
        }
        
        # Cycle warning keywords
        self.cycle_warning_keywords = {
            "oversupply", "inventory", "pricing pressure", "capex pause",
            "excess supply", "glut", "stockpile", "backlog", "order delay",
            "production cut", "demand slowdown", "capacity", "utilization"
        }
        
        # Late-cycle froth indicators
        self.froth_keywords = {
            "breakthrough", "revolutionary", "paradigm shift", "unprecedented",
            "game changer", "transformative", "disruptive", "next generation"
        }
        
        # Semiconductor cycle indicators
        self.semi_cycle_keywords = {
            "memory", "dram", "nand", "hbm", "ssd", "foundry", "semiconductor",
            "chip", "ai chip", "datacenter", "cloud", "capex", "fab", "wafer"
        }
    
    def analyze_news_catalysts(self, headlines: List[Headline], 
                              market_data: MarketData) -> List[NewsCatalyst]:
        """Analyze news headlines as catalysts and risk flags."""
        catalysts = []
        
        for headline in headlines:
            # Determine catalyst type
            catalyst_type = self._classify_catalyst_type(headline)
            
            # Calculate news risk score
            news_risk_score = self._calculate_news_risk_score(headline)
            
            # Calculate cycle relevance
            cycle_relevance = self._calculate_cycle_relevance(headline)
            
            # Calculate forward returns (if price data available)
            forward_returns = self._calculate_forward_returns(headline, market_data)
            
            # Determine price reaction
            price_reaction = self._classify_price_reaction(forward_returns)
            
            catalysts.append(NewsCatalyst(
                headline=headline,
                catalyst_type=catalyst_type,
                news_risk_score=news_risk_score,
                cycle_relevance=cycle_relevance,
                forward_returns=forward_returns,
                price_reaction=price_reaction
            ))
        
        return catalysts
    
    def analyze_cycle_conditions(self, ticker: str, headlines: List[Headline],
                               market_data: MarketData) -> CycleAnalysis:
        """Analyze cycle peak conditions for semiconductor/memory stocks."""
        indicators = market_data.indicators
        risk_metrics = market_data.risk_metrics
        
        # Initialize cycle indicators
        cycle_indicators = {}
        key_signals = []
        
        # 1. Technical overheating
        rsi = indicators.get('rsi_14', 50)
        if rsi > 75:
            cycle_indicators['rsi_overheating'] = min((rsi - 75) * 4, 100)  # Scale to 0-100
            key_signals.append(f"RSI extremely overbought ({rsi:.1f})")
        elif rsi > 70:
            cycle_indicators['rsi_overbought'] = min((rsi - 70) * 3.3, 100)
            key_signals.append(f"RSI overbought ({rsi:.1f})")
        
        # 2. Price extension
        ret_63d = indicators.get('ret_63d', 0)
        if ret_63d > 0.5:  # 50%+ gains
            cycle_indicators['price_extended'] = min(ret_63d * 100, 100)
            key_signals.append(f"Extended gains ({ret_63d:+.1%})")
        elif ret_63d > 0.3:  # 30%+ gains
            cycle_indicators['price_extended'] = min(ret_63d * 133, 100)
            key_signals.append(f"Strong gains ({ret_63d:+.1%})")
        
        # 3. News shift to negative cycle keywords
        cycle_news_risk = self._calculate_cycle_news_risk(headlines)
        cycle_indicators['negative_news_shift'] = cycle_news_risk
        if cycle_news_risk > 60:
            key_signals.append("Negative cycle keywords in news")
        
        # 4. Volatility regime shift
        vol_20d = indicators.get('volatility_20d', 0)
        vol_50d = indicators.get('volatility_50d', 0)
        if vol_20d > vol_50d * 1.3:
            cycle_indicators['volatility_expansion'] = min(((vol_20d / vol_50d) - 1) * 333, 100)
            key_signals.append("Volatility expansion without price progress")
        
        # 5. Capex expansion headlines (late-cycle behavior)
        capex_signals = self._count_capex_headlines(headlines)
        if capex_signals > 2:
            cycle_indicators['capex_expansion'] = min(capex_signals * 20, 100)
            key_signals.append(f"Capex expansion headlines ({capex_signals})")
        
        # 6. Price momentum vs volatility divergence
        momentum = abs(indicators.get('ret_21d', 0))
        if momentum < 0.05 and vol_20d > 0.3:  # Low momentum, high volatility
            cycle_indicators['momentum_volatility_divergence'] = min(vol_20d * 200 - momentum * 100, 100)
            key_signals.append("High volatility with low momentum")
        
        # Calculate overall cycle phase
        cycle_score = sum(cycle_indicators.values()) / len(cycle_indicators) if cycle_indicators else 0
        
        cycle_phase, confidence = self._determine_cycle_phase(cycle_score, key_signals)
        
        # Calculate news risk score
        news_risk_score = self._calculate_overall_news_risk(headlines)
        
        # Calculate "good news not working" effectiveness
        good_news_analysis = self.analyze_good_news_effectiveness(headlines, market_data)
        
        return CycleAnalysis(
            ticker=ticker,
            cycle_phase=cycle_phase,
            cycle_confidence=confidence,
            cycle_indicators=cycle_indicators,
            news_risk_score=news_risk_score,
            good_news_effectiveness=good_news_analysis.effectiveness_score,
            key_cycle_signals=key_signals,
            phase_transition_risk=self._calculate_transition_risk(cycle_score, cycle_phase)
        )
    
    def analyze_good_news_effectiveness(self, headlines: List[Headline],
                                       market_data: MarketData) -> GoodNewsAnalysis:
        """Analyze 'good news not working' phenomenon."""
        # Filter positive headlines
        positive_headlines = [h for h in headlines if h.sentiment > 0]
        
        if not positive_headlines:
            return GoodNewsAnalysis(
                ticker=market_data.ticker,
                positive_headlines=[],
                forward_return_analysis={},
                effectiveness_score=50.0,  # Neutral
                failure_rate=0.0,
                consecutive_failures=0,
                distribution_signals=[],
                alert_triggered=False
            )
        
        # Calculate forward returns for each positive headline
        forward_returns = {}
        failure_count = 0
        consecutive_failures = 0
        distribution_signals = []
        
        for headline in positive_headlines:
            returns = self._calculate_forward_returns(headline, market_data)
            forward_returns[headline.title[:50]] = returns
            
            # Check if good news failed (negative or flat returns)
            avg_return = np.mean(list(returns.values())) if returns else 0
            if avg_return <= 0:
                failure_count += 1
                consecutive_failures += 1
                distribution_signals.append(f"Positive headline failed: {headline.title[:30]}...")
            else:
                consecutive_failures = 0
        
        # Calculate effectiveness score (lower = worse)
        failure_rate = failure_count / len(positive_headlines) if positive_headlines else 0
        effectiveness_score = 100 - (failure_rate * 100)  # Invert so lower = worse
        
        # Alert trigger if multiple failures in recent period
        alert_triggered = consecutive_failures >= 2 or failure_rate >= 0.6
        
        return GoodNewsAnalysis(
            ticker=market_data.ticker,
            positive_headlines=positive_headlines,
            forward_return_analysis=forward_returns,
            effectiveness_score=effectiveness_score,
            failure_rate=failure_rate,
            consecutive_failures=consecutive_failures,
            distribution_signals=distribution_signals,
            alert_triggered=alert_triggered
        )
    
    def _classify_catalyst_type(self, headline: Headline) -> str:
        """Classify headline as catalyst type."""
        # Positive catalysts
        if headline.sentiment > 1:
            return "positive_catalyst"
        
        # Negative catalysts
        if headline.sentiment < -1:
            return "negative_catalyst"
        
        # Risk flags based on content
        text_lower = headline.title.lower()
        
        # Check for cycle warning keywords
        if any(keyword in text_lower for keyword in self.cycle_warning_keywords):
            return "risk_flag"
        
        # Check for legal/regulatory issues
        if any(word in text_lower for word in ["lawsuit", "probe", "investigation", "regulation"]):
            return "risk_flag"
        
        return "neutral"
    
    def _calculate_news_risk_score(self, headline: Headline) -> float:
        """Calculate news risk score (0-100)."""
        base_score = 0
        
        # Sentiment component
        if headline.sentiment < -2:
            base_score += 40
        elif headline.sentiment < -1:
            base_score += 25
        elif headline.sentiment < 0:
            base_score += 10
        
        # Category weighting
        category_weight = 1.0
        for category in headline.categories:
            category_weight = max(category_weight, self.category_weights.get(category, 0.5))
        
        base_score *= category_weight
        
        # Impact multiplier
        impact_multiplier = 1.0 + (headline.impact * 0.3)
        base_score *= impact_multiplier
        
        # Quality inverse (lower quality = higher risk)
        quality_inverse = 2.0 - headline.quality
        base_score *= quality_inverse
        
        # Cycle warning keywords
        text_lower = headline.title.lower()
        if any(keyword in text_lower for keyword in self.cycle_warning_keywords):
            base_score += 20
        
        # Late-cycle froth detection
        if any(keyword in text_lower for keyword in self.froth_keywords):
            if headline.quality < 0.6:  # Low quality + hype = froth
                base_score += 15
        
        return min(max(base_score, 0), 100)
    
    def _calculate_cycle_relevance(self, headline: Headline) -> float:
        """Calculate how relevant headline is to cycle analysis."""
        text_lower = headline.title.lower()
        
        relevance = 0
        
        # Direct semiconductor keywords
        if any(keyword in text_lower for keyword in self.semi_cycle_keywords):
            relevance += 40
        
        # Cycle warning keywords
        if any(keyword in text_lower for keyword in self.cycle_warning_keywords):
            relevance += 30
        
        # Capex keywords
        if any(word in text_lower for word in ["capex", "capital expenditure", "investment", "spending"]):
            relevance += 20
        
        # Supply/demand keywords
        if any(word in text_lower for word in ["supply", "demand", "inventory", "backlog"]):
            relevance += 10
        
        return min(relevance, 100)
    
    def _calculate_forward_returns(self, headline: Headline, market_data: MarketData) -> Dict[str, float]:
        """Calculate 1d, 2d, 3d forward returns from headline date."""
        # This is a simplified implementation
        # In practice, you'd match headline dates to price data
        
        returns = {"1d": 0.0, "2d": 0.0, "3d": 0.0}
        
        # Use recent returns as proxy (simplified)
        indicators = market_data.indicators
        returns["1d"] = indicators.get('ret_5d', 0) / 5  # Approximate daily
        returns["2d"] = indicators.get('ret_5d', 0) / 2.5
        returns["3d"] = indicators.get('ret_5d', 0) / 1.67
        
        # Adjust based on sentiment
        if headline.sentiment > 0:
            # Positive news should have positive returns
            sentiment_factor = 1 + (headline.sentiment * 0.1)
            for key in returns:
                returns[key] *= sentiment_factor
        elif headline.sentiment < 0:
            # Negative news should have negative returns
            sentiment_factor = 1 + (headline.sentiment * 0.1)
            for key in returns:
                returns[key] *= sentiment_factor
        
        return returns
    
    def _classify_price_reaction(self, forward_returns: Dict[str, float]) -> str:
        """Classify price reaction based on forward returns."""
        avg_return = np.mean(list(forward_returns.values())) if forward_returns else 0
        
        if avg_return > 0.02:  # >2%
            return "strong_positive"
        elif avg_return > 0.005:  # >0.5%
            return "weak_positive"
        elif avg_return < -0.01:  # <-1%
            return "negative"
        else:
            return "neutral"
    
    def _calculate_cycle_news_risk(self, headlines: List[Headline]) -> float:
        """Calculate news risk score specifically for cycle analysis."""
        cycle_risk_headlines = 0
        total_headlines = len(headlines)
        
        for headline in headlines:
            text_lower = headline.title.lower()
            
            # Check for cycle warning keywords
            if any(keyword in text_lower for keyword in self.cycle_warning_keywords):
                cycle_risk_headlines += 1
            # Check for negative earnings/guidance
            elif headline.sentiment < -1 and any(cat in headline.categories for cat in ["earnings", "guidance"]):
                cycle_risk_headlines += 1
        
        return (cycle_risk_headlines / total_headlines * 100) if total_headlines > 0 else 0
    
    def _count_capex_headlines(self, headlines: List[Headline]) -> int:
        """Count headlines mentioning capex expansion."""
        capex_count = 0
        
        for headline in headlines:
            text_lower = headline.title.lower()
            if any(word in text_lower for word in ["capex", "capital expenditure", "investment", "spending"]):
                if any(word in text_lower for word in ["expand", "increase", "growth", "rise"]):
                    capex_count += 1
        
        return capex_count
    
    def _determine_cycle_phase(self, cycle_score: float, key_signals: List[str]) -> Tuple[str, float]:
        """Determine cycle phase based on indicators."""
        if cycle_score < 20:
            return "early", 0.8
        elif cycle_score < 40:
            return "mid", 0.7
        elif cycle_score < 60:
            return "late-mid", 0.6
        elif cycle_score < 80:
            return "late", 0.7
        else:
            return "rollover_risk", 0.9
    
    def _calculate_transition_risk(self, cycle_score: float, current_phase: str) -> float:
        """Calculate risk of phase transition."""
        if current_phase == "late-mid":
            return min((cycle_score - 50) * 3, 100)  # Risk increases as we approach late
        elif current_phase == "late":
            return min((cycle_score - 60) * 2.5, 100)
        elif current_phase == "rollover_risk":
            return min(cycle_score * 1.2, 100)
        else:
            return max(0, (cycle_score - 40) * 1.5)  # Lower risk in early/mid phases
    
    def _calculate_overall_news_risk(self, headlines: List[Headline]) -> float:
        """Calculate overall news risk score."""
        if not headlines:
            return 0
        
        total_risk = sum(self._calculate_news_risk_score(h) for h in headlines)
        return min(total_risk / len(headlines), 100)


def print_advanced_news_analysis(catalysts: List[NewsCatalyst], 
                                cycle_analysis: CycleAnalysis,
                                good_news_analysis: GoodNewsAnalysis):
    """Print comprehensive advanced news analysis."""
    ticker = cycle_analysis.ticker
    
    print(f"\n{'='*80}")
    print(f"🔍 ADVANCED NEWS ANALYSIS - {ticker}")
    print(f"{'='*80}")
    
    # Cycle Analysis
    print(f"\n🔄 CYCLE ANALYSIS:")
    print(f"  Phase: {cycle_analysis.cycle_phase.upper()}")
    print(f"  Confidence: {cycle_analysis.cycle_confidence:.1%}")
    print(f"  News Risk Score: {cycle_analysis.news_risk_score:.1f}/100")
    print(f"  Good News Effectiveness: {cycle_analysis.good_news_effectiveness:.1f}/100")
    print(f"  Transition Risk: {cycle_analysis.phase_transition_risk:.1f}/100")
    
    if cycle_analysis.key_cycle_signals:
        print(f"  Key Signals:")
        for signal in cycle_analysis.key_cycle_signals:
            print(f"    • {signal}")
    
    # Good News Analysis
    print(f"\n📰 GOOD NEWS EFFECTIVENESS:")
    print(f"  Positive Headlines: {len(good_news_analysis.positive_headlines)}")
    print(f"  Failure Rate: {good_news_analysis.failure_rate:.1%}")
    print(f"  Consecutive Failures: {good_news_analysis.consecutive_failures}")
    print(f"  Alert Triggered: {'⚠️ YES' if good_news_analysis.alert_triggered else '✅ No'}")
    
    if good_news_analysis.distribution_signals:
        print(f"  Distribution Signals:")
        for signal in good_news_analysis.distribution_signals[:3]:
            print(f"    • {signal}")
    
    # News Catalysts
    print(f"\n🎯 NEWS CATALYSTS:")
    positive_catalysts = [c for c in catalysts if c.catalyst_type == "positive_catalyst"]
    negative_catalysts = [c for c in catalysts if c.catalyst_type == "negative_catalyst"]
    risk_flags = [c for c in catalysts if c.catalyst_type == "risk_flag"]
    
    if positive_catalysts:
        print(f"  Positive Catalysts ({len(positive_catalysts)}):")
        for catalyst in positive_catalysts[:3]:
            print(f"    • {catalyst.headline.title[:50]}... (Risk: {catalyst.news_risk_score:.1f})")
    
    if negative_catalysts:
        print(f"  Negative Catalysts ({len(negative_catalysts)}):")
        for catalyst in negative_catalysts[:3]:
            print(f"    • {catalyst.headline.title[:50]}... (Risk: {catalyst.news_risk_score:.1f})")
    
    if risk_flags:
        print(f"  Risk Flags ({len(risk_flags)}):")
        for catalyst in risk_flags[:3]:
            print(f"    • {catalyst.headline.title[:50]}... (Risk: {catalyst.news_risk_score:.1f})")


def main():
    """Demonstrate advanced news interpretation."""
    import argparse
    from market_data_processor import MarketDataProcessor
    from news import fetch_headlines_for_ticker
    
    parser = argparse.ArgumentParser(description="Advanced news interpretation")
    parser.add_argument("tickers", nargs="+", help="Tickers to analyze")
    parser.add_argument("--days", type=int, default=180, help="Analysis period")
    parser.add_argument("--max-headlines", type=int, default=20, help="Max headlines")
    
    args = parser.parse_args()
    
    interpreter = AdvancedNewsInterpreter()
    
    for ticker in args.tickers:
        try:
            print(f"\n🔄 Processing {ticker}...")
            
            # Fetch headlines
            headlines = fetch_headlines_for_ticker(
                ticker=ticker,
                max_items=args.max_headlines,
                keywords=["AI", "HBM", "DRAM", "NAND", "capex", "guidance", "inventory"]
            )
            
            # Create mock market data for demonstration
            # In practice, you'd use: market_data = processor.fetch_and_process(ticker, args.days)
            from test_dual_scoring import create_mock_market_data
            market_data = create_mock_market_data(ticker)
            
            # Analyze news catalysts
            catalysts = interpreter.analyze_news_catalysts(headlines, market_data)
            
            # Analyze cycle conditions
            cycle_analysis = interpreter.analyze_cycle_conditions(ticker, headlines, market_data)
            
            # Analyze good news effectiveness
            good_news_analysis = interpreter.analyze_good_news_effectiveness(headlines, market_data)
            
            # Print results
            print_advanced_news_analysis(catalysts, cycle_analysis, good_news_analysis)
            
        except Exception as e:
            print(f"❌ Error processing {ticker}: {e}")


if __name__ == "__main__":
    main()
