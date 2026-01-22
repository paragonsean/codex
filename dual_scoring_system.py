#!/usr/bin/env python3
"""
dual_scoring_system.py

Advanced dual scoring system with separate Opportunity and Sell-Risk scores.
Uses signal clustering rather than single indicators for more robust analysis.

Features:
- Opportunity Score (0-100): Buy/hold bias based on positive clusters
- Sell-Risk Score (0-100): Trim/exit bias based on negative clusters  
- Signal clustering: Multiple related indicators create stronger signals
- Dynamic weighting: Different market conditions emphasize different factors
- Comprehensive signal detection across technical, volume, and pattern analysis

Usage:
    from dual_scoring_system import DualScoringSystem
    
    scorer = DualScoringSystem()
    scores = scorer.calculate_scores(market_data, news_data)
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone


@dataclass
class SignalCluster:
    """Represents a cluster of related signals."""
    name: str
    signals: List[str]
    weight: float
    triggered: bool
    strength: float  # 0.0-1.0
    description: str


@dataclass
class DualScores:
    """Dual scoring results with detailed breakdown."""
    ticker: str
    opportunity_score: float  # 0-100, buy/hold bias
    sell_risk_score: float   # 0-100, trim/exit bias
    opportunity_clusters: List[SignalCluster]
    sell_risk_clusters: List[SignalCluster]
    overall_bias: str  # "STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"
    confidence: float  # 0-1, how strong the signal is
    timestamp: str
    key_factors: List[str]  # Top 3 factors driving the scores


class DualScoringSystem:
    """Advanced dual scoring system with signal clustering."""
    
    def __init__(self):
        self.cluster_weights = self._initialize_cluster_weights()
        self.signal_thresholds = self._initialize_signal_thresholds()
    
    def _get_indicator_value(self, indicators: Dict[str, any], key: str, default: float = 0) -> float:
        """Helper to get scalar value from indicators dict."""
        value = indicators.get(key, default)
        if hasattr(value, 'iloc'):
            return float(value.iloc[-1]) if len(value) > 0 else default
        return float(value) if value is not None else default
    
    def calculate_scores(self, market_data, news_data=None) -> DualScores:
        """Calculate comprehensive dual scores."""
        ticker = market_data.ticker
        
        # Calculate opportunity clusters
        opportunity_clusters = self._analyze_opportunity_clusters(market_data, news_data)
        
        # Calculate sell-risk clusters  
        sell_risk_clusters = self._analyze_sell_risk_clusters(market_data, news_data)
        
        # Calculate weighted scores
        opportunity_score = self._calculate_cluster_score(opportunity_clusters)
        sell_risk_score = self._calculate_cluster_score(sell_risk_clusters)
        
        # Determine overall bias and confidence
        overall_bias, confidence = self._determine_bias(
            opportunity_score, sell_risk_score, opportunity_clusters, sell_risk_clusters
        )
        
        # Extract key factors
        key_factors = self._extract_key_factors(opportunity_clusters, sell_risk_clusters)
        
        return DualScores(
            ticker=ticker,
            opportunity_score=opportunity_score,
            sell_risk_score=sell_risk_score,
            opportunity_clusters=opportunity_clusters,
            sell_risk_clusters=sell_risk_clusters,
            overall_bias=overall_bias,
            confidence=confidence,
            timestamp=datetime.now(timezone.utc).isoformat(),
            key_factors=key_factors
        )
    
    def _analyze_opportunity_clusters(self, market_data, news_data=None) -> List[SignalCluster]:
        """Analyze opportunity-focused signal clusters."""
        clusters = []
        indicators = market_data.indicators
        risk_metrics = market_data.risk_metrics
        
        # Cluster 1: Technical Momentum
        momentum_signals = []
        momentum_strength = 0.0
        
        # Positive price momentum
        ret_21d = self._get_indicator_value(indicators, 'ret_21d', 0)
        if ret_21d > 0.05:  # 5%+ in 21 days
            momentum_signals.append("Strong 21D momentum")
            momentum_strength += 0.3
        elif ret_21d > 0.02:  # 2%+ in 21 days
            momentum_signals.append("Moderate 21D momentum")
            momentum_strength += 0.2
        
        # RSI oversold
        rsi = indicators.get('rsi_14', 50)
        if rsi < 30:
            momentum_signals.append("RSI oversold (<30)")
            momentum_strength += 0.4
        elif rsi < 35:
            momentum_signals.append("RSI near oversold (<35)")
            momentum_strength += 0.2
        
        # Moving average trend
        trend = indicators.get('trend_50_200', 'unknown')
        if 'bullish' in trend:
            momentum_signals.append("Bullish trend (50>200)")
            momentum_strength += 0.3
        
        # Volume confirmation
        vol_z = self._get_indicator_value(indicators, 'volume_z_score', 0)
        ret_5d = self._get_indicator_value(indicators, 'ret_5d', 0)
        if vol_z > 1.5 and ret_5d > 0:
            momentum_signals.append("Volume confirms upside")
            momentum_strength += 0.2
        
        clusters.append(SignalCluster(
            name="Technical Momentum",
            signals=momentum_signals,
            weight=self.cluster_weights['momentum'],
            triggered=len(momentum_signals) >= 2,
            strength=min(momentum_strength, 1.0),
            description=f"Price momentum and trend signals ({len(momentum_signals)} signals)"
        ))
        
        # Cluster 2: Value/Reversal Opportunity
        value_signals = []
        value_strength = 0.0
        
        # Deep drawdown (potential turnaround)
        current_dd = risk_metrics.get('current_drawdown', 0)
        if current_dd < -0.25:  # 25%+ drawdown
            value_signals.append("Deep drawdown (>25%)")
            value_strength += 0.4
        elif current_dd < -0.15:  # 15%+ drawdown
            value_signals.append("Moderate drawdown (>15%)")
            value_strength += 0.2
        
        # Low volatility regime (good for entry)
        vol_regime = risk_metrics.get('volatility_regime', 'normal')
        if vol_regime == 'low':
            value_signals.append("Low volatility regime")
            value_strength += 0.2
        
        # Price near support
        position_20d = indicators.get('position_20d_high', 0.5)
        if position_20d < 0.2:  # Near 20D low
            value_signals.append("Near 20D support")
            value_strength += 0.2
        
        # Positive news sentiment
        if news_data and news_data.news_sentiment_total > 2:
            value_signals.append("Positive news sentiment")
            value_strength += 0.3
        
        clusters.append(SignalCluster(
            name="Value/Reversal",
            signals=value_signals,
            weight=self.cluster_weights['value'],
            triggered=len(value_signals) >= 2,
            strength=min(value_strength, 1.0),
            description=f"Value and reversal signals ({len(value_signals)} signals)"
        ))
        
        # Cluster 3: Breakout Potential
        breakout_signals = []
        breakout_strength = 0.0
        
        # Consolidation breakout
        high_20d = indicators.get('high_20d', 0)
        current_price = market_data.current_price
        if current_price >= high_20d * 0.98:  # Near 20D high
            breakout_signals.append("Near 20D high")
            breakout_strength += 0.3
        
        # Volume surge
        if vol_z > 2.0:
            breakout_signals.append("Volume surge")
            breakout_strength += 0.3
        
        # Expanding volatility (pre-breakout)
        vol_20d = self._get_indicator_value(indicators, 'volatility_20d', 0)
        vol_50d = self._get_indicator_value(indicators, 'volatility_50d', 0)
            
        if vol_20d > vol_50d * 1.2:
            breakout_signals.append("Volatility expansion")
            breakout_strength += 0.2
        
        # Price momentum acceleration
        ret_5d = self._get_indicator_value(indicators, 'ret_5d', 0)
        ret_21d = self._get_indicator_value(indicators, 'ret_21d', 0)
        if ret_5d > ret_21d * 2 and ret_5d > 0:
            breakout_signals.append("Momentum acceleration")
            breakout_strength += 0.2
        
        clusters.append(SignalCluster(
            name="Breakout Potential",
            signals=breakout_signals,
            weight=self.cluster_weights['breakout'],
            triggered=len(breakout_signals) >= 2,
            strength=min(breakout_strength, 1.0),
            description=f"Breakout and momentum signals ({len(breakout_signals)} signals)"
        ))
        
        return clusters
    
    def _analyze_sell_risk_clusters(self, market_data, news_data=None) -> List[SignalCluster]:
        """Analyze sell-risk focused signal clusters."""
        clusters = []
        indicators = market_data.indicators
        risk_metrics = market_data.risk_metrics
        news_eff = market_data.news_effectiveness
        
        # Cluster 1: Technical Overheating
        overheating_signals = []
        overheating_strength = 0.0
        
        # RSI overbought
        rsi = indicators.get('rsi_14', 50)
        if rsi > 80:
            overheating_signals.append("RSI extremely overbought (>80)")
            overheating_strength += 0.4
        elif rsi > 70:
            overheating_signals.append("RSI overbought (>70)")
            overheating_strength += 0.3
        
        # RSI divergence (price higher highs, RSI lower highs)
        # Simplified divergence check
        ret_21d = self._get_indicator_value(indicators, 'ret_21d', 0)
        if rsi > 70 and ret_21d > 0.1:  # Strong gains but RSI high
            overheating_signals.append("Potential RSI divergence")
            overheating_strength += 0.3
        
        # Extended gains
        ret_63d = self._get_indicator_value(indicators, 'ret_63d', 0)
        if ret_63d > 0.5:  # 50%+ in 63 days
            overheating_signals.append("Extended gains (>50% in 3mo)")
            overheating_strength += 0.3
        elif ret_63d > 0.3:  # 30%+ in 63 days
            overheating_signals.append("Strong gains (>30% in 3mo)")
            overheating_strength += 0.2
        
        # High volatility with gains
        vol_20d = self._get_indicator_value(indicators, 'volatility_20d', 0)
        if vol_20d > 0.4 and ret_21d > 0.05:
            overheating_signals.append("High volatility with gains")
            overheating_strength += 0.2
        
        # New condition: High RSI with low volume
        vol_z = self._get_indicator_value(indicators, 'volume_z_score', 0)
        if rsi > 70 and vol_z < -1:
            overheating_signals.append("High RSI with low volume")
            overheating_strength += 0.2
        
        clusters.append(SignalCluster(
            name="Technical Overheating",
            signals=overheating_signals,
            weight=self.cluster_weights['overheating'],
            triggered=len(overheating_signals) >= 2,
            strength=min(overheating_strength, 1.0),
            description=f"Overbought and extended signals ({len(overheating_signals)} signals)"
        ))
        
        # Cluster 2: Trend Deterioration
        trend_signals = []
        trend_strength = 0.0
        
        # Below 50DMA
        price_vs_50 = indicators.get('price_vs_sma_50', 0)
        if price_vs_50 < -0.05:  # 5% below 50DMA
            trend_signals.append("Trading below 50DMA")
            trend_strength += 0.3
        
        # 50DMA flattening/turning down
        # Simplified: if price below 50DMA and recent performance weak
        if price_vs_50 < 0 and indicators.get('ret_21d', 0) < -0.02:
            trend_signals.append("50DMA resistance")
            trend_strength += 0.3
        
        # Bearish trend
        trend = indicators.get('trend_50_200', 'unknown')
        if 'bearish' in trend:
            trend_signals.append("Bearish trend (50<200)")
            trend_strength += 0.4
        
        # Moving average cross threat
        price_vs_200 = indicators.get('price_vs_sma_200', 0)
        if price_vs_50 < 0 and price_vs_200 > 0:  # Below 50, above 200
            trend_signals.append("MA cross threat")
            trend_strength += 0.2
        
        clusters.append(SignalCluster(
            name="Trend Deterioration",
            signals=trend_signals,
            weight=self.cluster_weights['trend_deterioration'],
            triggered=len(trend_signals) >= 2,
            strength=min(trend_strength, 1.0),
            description=f"Trend weakening signals ({len(trend_signals)} signals)"
        ))
        
        # Cluster 3: Distribution Behavior
        distribution_signals = []
        distribution_strength = 0.0
        
        # High volume on down days (from news effectiveness)
        high_vol_win_rate = news_eff.get('high_volume_win_rate', 0.5)
        if high_vol_win_rate < 0.3:  # Low win rate on high volume
            distribution_signals.append("High volume distribution")
            distribution_strength += 0.4
        elif high_vol_win_rate < 0.4:
            distribution_signals.append("Volume-based selling")
            distribution_strength += 0.2
        
        # Failed breakouts
        failed_breakouts = news_eff.get('failed_breakout_frequency', 0)
        if failed_breakouts > 0.3:  # 30%+ failed breakouts
            distribution_signals.append("High failed breakout rate")
            distribution_strength += 0.3
        elif failed_breakouts > 0.2:
            distribution_signals.append("Failed breakout pattern")
            distribution_strength += 0.2
        
        # Intraday weakness
        intraday_weakness = news_eff.get('avg_intraday_weakness', 0)
        if intraday_weakness < -0.3:  # Strong intraday weakness
            distribution_signals.append("Strong intraday weakness")
            distribution_strength += 0.3
        elif intraday_weakness < -0.2:
            distribution_signals.append("Intraday selling pressure")
            distribution_strength += 0.2
        
        # Gap down frequency
        gap_down_freq = news_eff.get('gap_down_frequency', 0)
        if gap_down_freq > 0.1:  # 10%+ gap downs
            distribution_signals.append("Frequent gap downs")
            distribution_strength += 0.2
        
        clusters.append(SignalCluster(
            name="Distribution Behavior",
            signals=distribution_signals,
            weight=self.cluster_weights['distribution'],
            triggered=len(distribution_signals) >= 2,
            strength=min(distribution_strength, 1.0),
            description=f"Distribution and selling signals ({len(distribution_signals)} signals)"
        ))
        
        # Cluster 4: Volatility Regime Shift
        volatility_signals = []
        volatility_strength = 0.0
        
        # ATR rising while returns flatten
        atr_pct = indicators.get('atr_pct', 0)
        ret_21d = indicators.get('ret_21d', 0)
        if atr_pct > 0.05 and abs(ret_21d) < 0.02:  # High ATR but flat returns
            volatility_signals.append("High ATR, flat returns")
            volatility_strength += 0.4
        
        # Volatility regime shift to high
        vol_regime = risk_metrics.get('volatility_regime', 'normal')
        if vol_regime == 'high':
            volatility_signals.append("High volatility regime")
            volatility_strength += 0.3
        elif vol_regime == 'elevated':
            volatility_signals.append("Elevated volatility")
            volatility_strength += 0.2
        
        # Volatility expansion
        vol_20d = self._get_indicator_value(indicators, 'volatility_20d', 0)
        vol_50d = self._get_indicator_value(indicators, 'volatility_50d', 0)
        if vol_20d > vol_50d * 1.3:
            volatility_signals.append("Rapid volatility expansion")
            volatility_strength += 0.3
        
        # Downside deviation increasing
        downside_dev = risk_metrics.get('downside_deviation', 0)
        if downside_dev > 0.02:  # 2%+ downside deviation
            volatility_signals.append("High downside deviation")
            volatility_strength += 0.2
        
        clusters.append(SignalCluster(
            name="Volatility Regime Shift",
            signals=volatility_signals,
            weight=self.cluster_weights['volatility_shift'],
            triggered=len(volatility_signals) >= 2,
            strength=min(volatility_strength, 1.0),
            description=f"Volatility and risk signals ({len(volatility_signals)} signals)"
        ))
        
        return clusters
    
    def _calculate_cluster_score(self, clusters: List[SignalCluster]) -> float:
        """Calculate weighted score from clusters."""
        total_score = 0.0
        total_weight = 0.0
        
        for cluster in clusters:
            if cluster.triggered:
                cluster_score = cluster.strength * cluster.weight * 100
                total_score += cluster_score
                total_weight += cluster.weight
        
        # Normalize to 0-100 scale
        if total_weight > 0:
            normalized_score = (total_score / total_weight) * (1 / max(self.cluster_weights.values()))
        else:
            normalized_score = 0.0
        
        return min(max(normalized_score, 0), 100)
    
    def _determine_bias(self, opportunity_score: float, sell_risk_score: float,
                       opp_clusters: List[SignalCluster], risk_clusters: List[SignalCluster]) -> Tuple[str, float]:
        """Determine overall bias and confidence."""
        # Calculate net score
        net_score = opportunity_score - sell_risk_score
        
        # Determine bias
        if net_score > 30:
            bias = "STRONG_BUY"
        elif net_score > 15:
            bias = "BUY"
        elif net_score > -15:
            bias = "HOLD"
        elif net_score > -30:
            bias = "SELL"
        else:
            bias = "STRONG_SELL"
        
        # Calculate confidence based on cluster strength and count
        triggered_opp = sum(1 for c in opp_clusters if c.triggered)
        triggered_risk = sum(1 for c in risk_clusters if c.triggered)
        total_triggered = triggered_opp + triggered_risk
        
        if total_triggered == 0:
            confidence = 0.0
        else:
            # Average strength of triggered clusters
            avg_strength = 0.0
            for cluster in opp_clusters + risk_clusters:
                if cluster.triggered:
                    avg_strength += cluster.strength
            avg_strength /= total_triggered
            
            # Confidence based on strength and number of signals
            confidence = avg_strength * (total_triggered / 8.0)  # 8 total possible clusters
            confidence = min(confidence, 1.0)
        
        return bias, confidence
    
    def _extract_key_factors(self, opp_clusters: List[SignalCluster], 
                           risk_clusters: List[SignalCluster]) -> List[str]:
        """Extract top 3 factors driving the scores."""
        all_factors = []
        
        # Add opportunity factors
        for cluster in opp_clusters:
            if cluster.triggered and cluster.strength > 0.3:
                for signal in cluster.signals[:2]:  # Top 2 signals per cluster
                    all_factors.append((f"🟢 {signal}", cluster.strength))
        
        # Add risk factors
        for cluster in risk_clusters:
            if cluster.triggered and cluster.strength > 0.3:
                for signal in cluster.signals[:2]:  # Top 2 signals per cluster
                    all_factors.append((f"🔴 {signal}", cluster.strength))
        
        # Sort by strength and take top 3
        all_factors.sort(key=lambda x: x[1], reverse=True)
        return [factor[0] for factor in all_factors[:3]]
    
    def _initialize_cluster_weights(self) -> Dict[str, float]:
        """Initialize cluster weights."""
        return {
            # Opportunity clusters
            'momentum': 0.35,
            'value': 0.25,
            'breakout': 0.20,
            
            # Sell-risk clusters
            'overheating': 0.35,
            'trend_deterioration': 0.30,
            'distribution': 0.25,
            'volatility_shift': 0.20
        }
    
    def _initialize_signal_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize signal thresholds."""
        return {
            'rsi': {
                'oversold': 30,
                'overbought': 70,
                'extreme_overbought': 80
            },
            'returns': {
                'strong_5d': 0.05,
                'strong_21d': 0.05,
                'strong_63d': 0.30,
                'extended_63d': 0.50
            },
            'volume': {
                'high_z': 1.5,
                'very_high_z': 2.0
            },
            'drawdown': {
                'moderate': -0.15,
                'deep': -0.25
            },
            'volatility': {
                'low': 0.15,
                'elevated': 0.25,
                'high': 0.35
            }
        }


def print_dual_scores(scores: DualScores):
    """Print comprehensive dual scoring results."""
    print(f"\n{'='*80}")
    print(f"🎯 DUAL SCORING ANALYSIS - {scores.ticker}")
    print(f"{'='*80}")
    
    print(f"\n📊 OVERALL ASSESSMENT:")
    print(f"  Opportunity Score: {scores.opportunity_score:.1f}/100")
    print(f"  Sell-Risk Score:  {scores.sell_risk_score:.1f}/100")
    print(f"  Overall Bias:      {scores.overall_bias}")
    print(f"  Confidence:        {scores.confidence:.1%}")
    
    print(f"\n🟢 OPPORTUNITY CLUSTERS:")
    for cluster in scores.opportunity_clusters:
        status = "✅ ACTIVE" if cluster.triggered else "❌ INACTIVE"
        print(f"  {cluster.name}: {cluster.strength:.1%} strength {status}")
        if cluster.triggered:
            for signal in cluster.signals:
                print(f"    • {signal}")
        else:
            print(f"    • No signals triggered")
    
    print(f"\n🔴 SELL-RISK CLUSTERS:")
    for cluster in scores.sell_risk_clusters:
        status = "⚠️  ACTIVE" if cluster.triggered else "❌ INACTIVE"
        print(f"  {cluster.name}: {cluster.strength:.1%} strength {status}")
        if cluster.triggered:
            for signal in cluster.signals:
                print(f"    • {signal}")
        else:
            print(f"    • No signals triggered")
    
    print(f"\n🎯 KEY DRIVING FACTORS:")
    for i, factor in enumerate(scores.key_factors, 1):
        print(f"  {i}. {factor}")
    
    print(f"\n📋 TRADING IMPLICATIONS:")
    if scores.overall_bias in ["STRONG_BUY", "BUY"]:
        print("  • Consider accumulation opportunities")
        print("  • Focus on entry timing and position sizing")
        if scores.sell_risk_score < 30:
            print("  • Low sell-risk allows for larger positions")
    elif scores.overall_bias == "HOLD":
        print("  • Maintain current positions")
        if scores.opportunity_score > scores.sell_risk_score:
            print("  • Slight bullish bias - watch for entry opportunities")
        else:
            print("  • Slight bearish bias - watch for exit signals")
    else:
        print("  • Consider reducing or exiting positions")
        print("  • Protect capital with stop-losses")
        if scores.opportunity_score < 30:
            print("  • Low opportunity score - avoid new positions")


def main():
    """Demonstrate the dual scoring system."""
    import argparse
    from market_data_processor import MarketDataProcessor
    
    parser = argparse.ArgumentParser(description="Dual scoring system analysis")
    parser.add_argument("tickers", nargs="+", help="Tickers to analyze")
    parser.add_argument("--days", type=int, default=180, help="Analysis period")
    
    args = parser.parse_args()
    
    scorer = DualScoringSystem()
    processor = MarketDataProcessor()
    
    for ticker in args.tickers:
        try:
            # Get market data (using test approach for now)
            from test_market_data import test_with_working_ticker
            # This would normally use: market_data = processor.fetch_and_process(ticker, args.days)
            
            print(f"Processing {ticker}...")
            # For demo, create mock data
            print(f"⚠️  Using demo data for {ticker}")
            
            # Mock scores for demonstration
            mock_scores = DualScores(
                ticker=ticker,
                opportunity_score=65.0,
                sell_risk_score=35.0,
                opportunity_clusters=[],
                sell_risk_clusters=[],
                overall_bias="BUY",
                confidence=0.7,
                timestamp=datetime.now(timezone.utc).isoformat(),
                key_factors=["🟢 Strong 21D momentum", "🟢 RSI oversold (<30)", "🔴 RSI overbought (>70)"]
            )
            
            print_dual_scores(mock_scores)
            
        except Exception as e:
            print(f"❌ Error processing {ticker}: {e}")


if __name__ == "__main__":
    main()
