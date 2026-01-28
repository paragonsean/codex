#!/usr/bin/env python3
"""
trading_strategy_analyzer.py

Personalized trading strategy analyzer that matches real trading workflows.
Supports different trading styles, position management, and actionable recommendations.

Usage:
    python trading_strategy_analyzer.py --portfolio portfolio.json --strategy swing
    python trading_strategy_analyzer.py --watchlist AAPL TSLA NVDA --strategy position --timeframe 1y
    python trading_strategy_analyzer.py --config trading_config.json
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
import yfinance as yf

# Import the enhanced news analyzer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from news import (
    fetch_prices, summarize_prices, fetch_headlines_for_ticker,
    compute_combined_signal, TickerReport, Headline, PriceSummary
)


@dataclass
class Position:
    """Represents a current trading position."""
    ticker: str
    shares: float
    cost_basis: float  # per share
    current_price: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    unrealized_pnl_pct: Optional[float] = None
    position_value: Optional[float] = None
    
    def calculate_metrics(self, current_price: float):
        """Calculate position metrics based on current price."""
        self.current_price = current_price
        self.position_value = self.shares * current_price
        self.unrealized_pnl = (current_price - self.cost_basis) * self.shares
        self.unrealized_pnl_pct = ((current_price - self.cost_basis) / self.cost_basis) * 100


@dataclass
class TradingStrategy:
    """Trading strategy configuration."""
    name: str
    description: str
    timeframes: Dict[str, int]  # e.g., {"trend": 252, "cycle": 126}
    risk_tolerance: float  # 0.0-1.0
    max_position_size: float  # max % of portfolio
    stop_loss_pct: float
    take_profit_pct: float
    rebalance_threshold: float  # % deviation before rebalancing
    indicators: List[str]  # key indicators for this strategy
    
    def get_timeframe_days(self, timeframe: str) -> int:
        """Get days for a specific timeframe."""
        return self.timeframes.get(timeframe, 252)


# Predefined trading strategies
TRADING_STRATEGIES = {
    "swing": TradingStrategy(
        name="Swing Trading",
        description="Medium-term trades lasting weeks to months, focusing on momentum and trend reversals",
        timeframes={"trend": 252, "cycle": 63, "entry": 21},
        risk_tolerance=0.7,
        max_position_size=0.15,
        stop_loss_pct=0.08,
        take_profit_pct=0.20,
        rebalance_threshold=0.05,
        indicators=["RSI", "MACD", "Moving Averages", "Volume"]
    ),
    "position": TradingStrategy(
        name="Position Trading",
        description="Long-term positions based on fundamental analysis and major trends",
        timeframes={"trend": 504, "cycle": 252, "entry": 63},
        risk_tolerance=0.5,
        max_position_size=0.25,
        stop_loss_pct=0.15,
        take_profit_pct=0.50,
        rebalance_threshold=0.10,
        indicators=["50/200 DMA", "Trend", "Fundamentals", "News Sentiment"]
    ),
    "income": TradingStrategy(
        name="Income/Covered Calls",
        description="Income generation through dividends and options writing",
        timeframes={"trend": 252, "cycle": 126, "entry": 42},
        risk_tolerance=0.3,
        max_position_size=0.20,
        stop_loss_pct=0.12,
        take_profit_pct=0.15,
        rebalance_threshold=0.08,
        indicators=["Dividend Yield", "Options Flow", "Volatility", "Support/Resistance"]
    ),
    "momentum": TradingStrategy(
        name="Momentum Trading",
        description="Short-term momentum plays focusing on strong trends and news catalysts",
        timeframes={"trend": 63, "cycle": 21, "entry": 10},
        risk_tolerance=0.9,
        max_position_size=0.10,
        stop_loss_pct=0.05,
        take_profit_pct=0.15,
        rebalance_threshold=0.03,
        indicators=["RSI", "Volume", "Price Action", "News Impact"]
    )
}


@dataclass
class TradingRecommendation:
    """Actionable trading recommendation."""
    ticker: str
    action: str  # "BUY", "SELL", "HOLD", "TRIM", "ADD", "CLOSE"
    confidence: float  # 0.0-1.0
    reasoning: List[str]
    price_target: Optional[float] = None
    stop_loss: Optional[float] = None
    position_size_pct: Optional[float] = None
    timeframe: Optional[str] = None
    risk_reward: Optional[float] = None


@dataclass
class TradingAnalysis:
    """Complete trading analysis for a position or watchlist item."""
    ticker: str
    strategy: TradingStrategy
    position: Optional[Position]
    technical_analysis: Optional[PriceSummary]
    news_analysis: Optional[TickerReport]
    recommendation: TradingRecommendation
    key_metrics: Dict[str, float]
    risk_assessment: Dict[str, Union[str, float]]


class TradingStrategyAnalyzer:
    """Main analyzer for personalized trading strategies."""
    
    def __init__(self, strategy: Union[str, TradingStrategy]):
        if isinstance(strategy, str):
            if strategy not in TRADING_STRATEGIES:
                raise ValueError(f"Unknown strategy: {strategy}")
            self.strategy = TRADING_STRATEGIES[strategy]
        else:
            self.strategy = strategy
    
    def analyze_position(self, position: Position, max_headlines: int = 20) -> TradingAnalysis:
        """Analyze a current position based on the trading strategy."""
        print(f"Analyzing position: {position.ticker} ({position.shares} shares @ ${position.cost_basis:.2f})")
        
        # Fetch technical data
        trend_days = self.strategy.get_timeframe_days("trend")
        df = fetch_prices(position.ticker, trend_days)
        price_summary = summarize_prices(position.ticker, df)
        
        # Update position metrics
        if price_summary:
            position.calculate_metrics(price_summary.last_close)
        
        # Fetch news analysis
        headlines = fetch_headlines_for_ticker(
            ticker=position.ticker,
            max_items=max_headlines,
            keywords=["earnings", "guidance", "merger", "acquisition", "product", "AI", "chip"]
        )
        
        news_sent_total = sum(h.sentiment for h in headlines)
        news_kw_total = sum(h.keyword_score for h in headlines)
        combined_signal, notes = compute_combined_signal(price_summary, headlines)
        
        news_report = TickerReport(
            ticker=position.ticker,
            price=price_summary,
            headlines=headlines,
            news_sentiment_total=news_sent_total,
            news_keyword_total=news_kw_total,
            combined_signal=combined_signal,
            notes=notes
        )
        
        # Generate recommendation
        recommendation = self._generate_position_recommendation(position, price_summary, news_report)
        
        # Calculate key metrics
        key_metrics = self._calculate_key_metrics(position, price_summary, news_report)
        
        # Risk assessment
        risk_assessment = self._assess_risk(position, price_summary, news_report)
        
        return TradingAnalysis(
            ticker=position.ticker,
            strategy=self.strategy,
            position=position,
            technical_analysis=price_summary,
            news_analysis=news_report,
            recommendation=recommendation,
            key_metrics=key_metrics,
            risk_assessment=risk_assessment
        )
    
    def analyze_watchlist_item(self, ticker: str, max_headlines: int = 20) -> TradingAnalysis:
        """Analyze a watchlist item (no current position)."""
        print(f"Analyzing watchlist item: {ticker}")
        
        # Fetch technical data
        trend_days = self.strategy.get_timeframe_days("trend")
        df = fetch_prices(ticker, trend_days)
        price_summary = summarize_prices(ticker, df)
        
        # Fetch news analysis
        headlines = fetch_headlines_for_ticker(
            ticker=ticker,
            max_items=max_headlines,
            keywords=["earnings", "guidance", "merger", "acquisition", "product", "AI", "chip"]
        )
        
        news_sent_total = sum(h.sentiment for h in headlines)
        news_kw_total = sum(h.keyword_score for h in headlines)
        combined_signal, notes = compute_combined_signal(price_summary, headlines)
        
        news_report = TickerReport(
            ticker=ticker,
            price=price_summary,
            headlines=headlines,
            news_sentiment_total=news_sent_total,
            news_keyword_total=news_kw_total,
            combined_signal=combined_signal,
            notes=notes
        )
        
        # Generate recommendation
        recommendation = self._generate_watchlist_recommendation(ticker, price_summary, news_report)
        
        # Calculate key metrics
        key_metrics = self._calculate_key_metrics(None, price_summary, news_report)
        
        # Risk assessment
        risk_assessment = self._assess_risk(None, price_summary, news_report)
        
        return TradingAnalysis(
            ticker=ticker,
            strategy=self.strategy,
            position=None,
            technical_analysis=price_summary,
            news_analysis=news_report,
            recommendation=recommendation,
            key_metrics=key_metrics,
            risk_assessment=risk_assessment
        )
    
    def _generate_position_recommendation(self, position: Position, price_summary: Optional[PriceSummary], 
                                       news_report: TickerReport) -> TradingRecommendation:
        """Generate recommendation for an existing position."""
        reasoning = []
        action = "HOLD"
        confidence = 0.5
        
        if not price_summary:
            return TradingRecommendation(
                ticker=position.ticker,
                action="HOLD",
                confidence=0.0,
                reasoning=["No price data available"]
            )
        
        current_price = price_summary.last_close
        pnl_pct = position.unrealized_pnl_pct or 0
        
        # Strategy-specific logic
        if self.strategy.name == "Swing Trading":
            # Swing trading: trim winners, cut losers quickly
            if pnl_pct >= self.strategy.take_profit_pct * 100:
                action = "TRIM"
                confidence = 0.8
                reasoning.append(f"Take profit: +{pnl_pct:.1f}% exceeds target of {self.strategy.take_profit_pct*100:.0f}%")
                position_size_pct = 0.5  # Trim 50%
            elif pnl_pct <= -self.strategy.stop_loss_pct * 100:
                action = "SELL"
                confidence = 0.9
                reasoning.append(f"Stop loss triggered: {pnl_pct:.1f}% exceeds limit of -{self.strategy.stop_loss_pct*100:.0f}%")
            elif news_report.combined_signal > 10:
                action = "ADD"
                confidence = 0.6
                reasoning.append("Strong positive news signal supports adding to position")
                position_size_pct = 0.3  # Add 30%
            elif news_report.combined_signal < -5:
                action = "TRIM"
                confidence = 0.7
                reasoning.append("Negative news signal suggests reducing exposure")
                position_size_pct = 0.3
        
        elif self.strategy.name == "Position Trading":
            # Position trading: hold through volatility, focus on long-term trends
            if pnl_pct >= self.strategy.take_profit_pct * 100:
                action = "TRIM"
                confidence = 0.6
                reasoning.append(f"Take partial profits: +{pnl_pct:.1f}%")
                position_size_pct = 0.25  # Trim 25%
            elif pnl_pct <= -self.strategy.stop_loss_pct * 100:
                action = "TRIM"
                confidence = 0.7
                reasoning.append(f"Significant drawdown: {pnl_pct:.1f}%, consider reducing position")
                position_size_pct = 0.5
            elif "bullish" in price_summary.trend_50_200 and news_report.combined_signal > 5:
                action = "ADD"
                confidence = 0.6
                reasoning.append("Strong uptrend and positive news support adding")
                position_size_pct = 0.2
        
        elif self.strategy.name == "Income/Covered Calls":
            # Income strategy: focus on income generation, less concerned with price swings
            if pnl_pct >= 10:  # 10% profit for covered call opportunities
                action = "TRIM"
                confidence = 0.7
                reasoning.append(f"Good covered call opportunity at +{pnl_pct:.1f}%")
                position_size_pct = 0.3
            elif pnl_pct <= -15:  # Significant decline
                action = "ADD"
                confidence = 0.6
                reasoning.append(f"Average down at lower price: {pnl_pct:.1f}% decline")
                position_size_pct = 0.4
        
        elif self.strategy.name == "Momentum Trading":
            # Momentum: quick entries and exits
            if news_report.combined_signal > 15:
                action = "ADD"
                confidence = 0.8
                reasoning.append("Strong momentum signal")
                position_size_pct = 0.2
            elif news_report.combined_signal < -10:
                action = "SELL"
                confidence = 0.8
                reasoning.append("Momentum reversal detected")
            elif pnl_pct <= -self.strategy.stop_loss_pct * 100:
                action = "SELL"
                confidence = 0.9
                reasoning.append(f"Stop loss hit: {pnl_pct:.1f}%")
        
        # Technical analysis adjustments
        if price_summary.rsi_14 >= 80:
            reasoning.append("RSI extremely overbought (>80)")
            if action == "HOLD":
                action = "TRIM"
                confidence = max(confidence, 0.7)
                position_size_pct = position_size_pct if 'position_size_pct' in locals() else 0.3
        elif price_summary.rsi_14 <= 20:
            reasoning.append("RSI extremely oversold (<20)")
            if action == "HOLD":
                action = "ADD"
                confidence = max(confidence, 0.6)
                position_size_pct = position_size_pct if 'position_size_pct' in locals() else 0.2
        
        # Set price targets and stops
        price_target = None
        stop_loss = None
        
        if action in ["BUY", "ADD"]:
            price_target = current_price * (1 + self.strategy.take_profit_pct)
            stop_loss = current_price * (1 - self.strategy.stop_loss_pct)
        elif action in ["SELL", "TRIM"]:
            stop_loss = position.cost_basis * (1 - self.strategy.stop_loss_pct)
        
        # Calculate risk/reward
        risk_reward = None
        if price_target and stop_loss:
            reward = price_target - current_price
            risk = current_price - stop_loss
            risk_reward = reward / risk if risk > 0 else None
        
        return TradingRecommendation(
            ticker=position.ticker,
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            price_target=price_target,
            stop_loss=stop_loss,
            position_size_pct=position_size_pct if 'position_size_pct' in locals() else None,
            timeframe=self.strategy.get_timeframe_days("cycle"),
            risk_reward=risk_reward
        )
    
    def _generate_watchlist_recommendation(self, ticker: str, price_summary: Optional[PriceSummary],
                                         news_report: TickerReport) -> TradingRecommendation:
        """Generate recommendation for a watchlist item (no position)."""
        reasoning = []
        action = "HOLD"
        confidence = 0.3
        
        if not price_summary:
            return TradingRecommendation(
                ticker=ticker,
                action="HOLD",
                confidence=0.0,
                reasoning=["No price data available"]
            )
        
        current_price = price_summary.last_close
        
        # Strategy-specific entry logic
        if self.strategy.name == "Swing Trading":
            if news_report.combined_signal > 8 and price_summary.ret_21d > 0.05:
                action = "BUY"
                confidence = 0.7
                reasoning.append("Strong momentum and positive news signal")
                position_size_pct = 0.1  # 10% position
            elif price_summary.rsi_14 <= 30 and news_report.combined_signal > 0:
                action = "BUY"
                confidence = 0.6
                reasoning.append("Oversold conditions with positive news")
                position_size_pct = 0.08
        
        elif self.strategy.name == "Position Trading":
            if "bullish" in price_summary.trend_50_200 and news_report.combined_signal > 5:
                action = "BUY"
                confidence = 0.7
                reasoning.append("Long-term uptrend with positive fundamentals")
                position_size_pct = 0.15
            elif price_summary.max_drawdown <= -0.3 and news_report.combined_signal > 3:
                action = "BUY"
                confidence = 0.6
                reasoning.append("Deep drawdown with positive news (potential turnaround)")
                position_size_pct = 0.1
        
        elif self.strategy.name == "Income/Covered Calls":
            # For income strategy, look for stable, dividend-paying stocks
            if price_summary.vol_21d_ann <= 0.4 and news_report.combined_signal >= 0:
                action = "BUY"
                confidence = 0.6
                reasoning.append("Low volatility suitable for income strategy")
                position_size_pct = 0.12
        
        elif self.strategy.name == "Momentum Trading":
            if news_report.combined_signal > 12 and price_summary.ret_5d > 0.08:
                action = "BUY"
                confidence = 0.8
                reasoning.append("Strong momentum breakout")
                position_size_pct = 0.08
            elif price_summary.volume_z_20 >= 3 and news_report.combined_signal > 8:
                action = "BUY"
                confidence = 0.7
                reasoning.append("Volume spike with positive news")
                position_size_pct = 0.06
        
        # Set targets and stops for buy recommendations
        price_target = None
        stop_loss = None
        risk_reward = None
        
        if action == "BUY":
            price_target = current_price * (1 + self.strategy.take_profit_pct)
            stop_loss = current_price * (1 - self.strategy.stop_loss_pct)
            reward = price_target - current_price
            risk = current_price - stop_loss
            risk_reward = reward / risk if risk > 0 else None
        
        return TradingRecommendation(
            ticker=ticker,
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            price_target=price_target,
            stop_loss=stop_loss,
            position_size_pct=position_size_pct if 'position_size_pct' in locals() else None,
            timeframe=self.strategy.get_timeframe_days("cycle"),
            risk_reward=risk_reward
        )
    
    def _calculate_key_metrics(self, position: Optional[Position], price_summary: Optional[PriceSummary],
                             news_report: TickerReport) -> Dict[str, float]:
        """Calculate key metrics for the analysis."""
        metrics = {}
        
        if price_summary:
            metrics.update({
                "current_price": price_summary.last_close,
                "rsi_14": price_summary.rsi_14,
                "volatility_21d": price_summary.vol_21d_ann,
                "max_drawdown": price_summary.max_drawdown,
                "ret_5d": price_summary.ret_5d,
                "ret_21d": price_summary.ret_21d,
                "ret_63d": price_summary.ret_63d,
                "volume_z_score": price_summary.volume_z_20
            })
        
        if position:
            metrics.update({
                "cost_basis": position.cost_basis,
                "unrealized_pnl_pct": position.unrealized_pnl_pct or 0,
                "position_value": position.position_value or 0
            })
        
        metrics.update({
            "news_signal": news_report.combined_signal,
            "news_sentiment": news_report.news_sentiment_total,
            "news_keyword_hits": news_report.news_keyword_total
        })
        
        return metrics
    
    def _assess_risk(self, position: Optional[Position], price_summary: Optional[PriceSummary],
                   news_report: TickerReport) -> Dict[str, Union[str, float]]:
        """Assess risk level and factors."""
        risk_factors = []
        risk_score = 0.0
        
        if price_summary:
            # Technical risk factors
            if price_summary.rsi_14 >= 75:
                risk_factors.append("Overbought conditions")
                risk_score += 0.2
            elif price_summary.rsi_14 <= 25:
                risk_factors.append("Oversold conditions (potential bounce)")
                risk_score += 0.1
            
            if price_summary.vol_21d_ann >= 0.6:
                risk_factors.append("High volatility")
                risk_score += 0.3
            elif price_summary.vol_21d_ann >= 0.4:
                risk_factors.append("Moderate volatility")
                risk_score += 0.15
            
            if price_summary.max_drawdown <= -0.3:
                risk_factors.append("Large drawdown from peak")
                risk_score += 0.25
            elif price_summary.max_drawdown <= -0.2:
                risk_factors.append("Moderate drawdown")
                risk_score += 0.15
            
            if "bearish" in price_summary.trend_50_200:
                risk_factors.append("Downtrend (50<200 DMA)")
                risk_score += 0.2
        
        # News sentiment risk
        if news_report.combined_signal <= -5:
            risk_factors.append("Negative news sentiment")
            risk_score += 0.2
        elif news_report.combined_signal <= -2:
            risk_factors.append("Slightly negative news")
            risk_score += 0.1
        
        # Position-specific risk
        if position:
            if position.unrealized_pnl_pct and position.unrealized_pnl_pct <= -10:
                risk_factors.append(f"Significant loss: {position.unrealized_pnl_pct:.1f}%")
                risk_score += 0.3
            elif position.unrealized_pnl_pct and position.unrealized_pnl_pct <= -5:
                risk_factors.append(f"Moderate loss: {position.unrealized_pnl_pct:.1f}%")
                risk_score += 0.15
        
        # Determine overall risk level
        if risk_score >= 0.7:
            risk_level = "HIGH"
        elif risk_score >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors
        }


def load_portfolio_from_file(filepath: str) -> List[Position]:
    """Load portfolio from JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        positions = []
        for pos_data in data.get('positions', []):
            position = Position(
                ticker=pos_data['ticker'],
                shares=pos_data['shares'],
                cost_basis=pos_data['cost_basis']
            )
            positions.append(position)
        
        return positions
    except Exception as e:
        print(f"Error loading portfolio: {e}")
        return []


def save_trading_analysis(analyses: List[TradingAnalysis], output_file: str):
    """Save trading analysis to JSON file."""
    output_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "strategy": analyses[0].strategy.name if analyses else "unknown",
        "analyses": []
    }
    
    for analysis in analyses:
        analysis_dict = {
            "ticker": analysis.ticker,
            "recommendation": asdict(analysis.recommendation),
            "key_metrics": analysis.key_metrics,
            "risk_assessment": analysis.risk_assessment
        }
        
        if analysis.position:
            analysis_dict["position"] = asdict(analysis.position)
        
        if analysis.technical_analysis:
            analysis_dict["technical_analysis"] = asdict(analysis.technical_analysis)
        
        output_data["analyses"].append(analysis_dict)
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)


def print_trading_analysis(analyses: List[TradingAnalysis]):
    """Print formatted trading analysis."""
    print(f"\n{'='*80}")
    print(f"📊 TRADING STRATEGY ANALYSIS - {analyses[0].strategy.name.upper() if analyses else 'UNKNOWN'}")
    print(f"{'='*80}")
    
    for analysis in analyses:
        print(f"\n{'='*60}")
        print(f"🎯 {analysis.ticker}")
        print(f"{'='*60}")
        
        # Position info if available
        if analysis.position:
            pos = analysis.position
            pnl_color = "📈" if (pos.unrealized_pnl_pct or 0) > 0 else "📉"
            print(f"Position: {pos.shares} shares @ ${pos.cost_basis:.2f}")
            print(f"Current: ${pos.current_price:.2f} {pnl_color} {pos.unrealized_pnl_pct:+.1f}% (${pos.unrealized_pnl:+.2f})")
        
        # Recommendation
        rec = analysis.recommendation
        action_colors = {
            "BUY": "🟢", "SELL": "🔴", "HOLD": "🟡", 
            "TRIM": "🟠", "ADD": "🔵", "CLOSE": "⚫"
        }
        action_icon = action_colors.get(rec.action, "❓")
        
        print(f"\n{action_icon} RECOMMENDATION: {rec.action}")
        print(f"Confidence: {rec.confidence:.0%}")
        
        if rec.price_target:
            print(f"Price Target: ${rec.price_target:.2f}")
        if rec.stop_loss:
            print(f"Stop Loss: ${rec.stop_loss:.2f}")
        if rec.position_size_pct:
            print(f"Position Size: {rec.position_size_pct:.0%}")
        if rec.risk_reward:
            print(f"Risk/Reward: {rec.risk_reward:.2f}")
        
        print(f"\n📝 Reasoning:")
        for i, reason in enumerate(rec.reasoning, 1):
            print(f"  {i}. {reason}")
        
        # Key metrics
        print(f"\n📊 Key Metrics:")
        metrics = analysis.key_metrics
        if "current_price" in metrics:
            print(f"  Price: ${metrics['current_price']:.2f}")
        if "rsi_14" in metrics:
            print(f"  RSI(14): {metrics['rsi_14']:.1f}")
        if "volatility_21d" in metrics:
            print(f"  Volatility: {metrics['volatility_21d']:.1%}")
        if "ret_21d" in metrics:
            print(f"  21D Return: {metrics['ret_21d']:+.1%}")
        if "news_signal" in metrics:
            print(f"  News Signal: {metrics['news_signal']:+.1f}")
        
        # Risk assessment
        risk = analysis.risk_assessment
        risk_colors = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}
        risk_icon = risk_colors.get(risk["risk_level"], "❓")
        
        print(f"\n{risk_icon} RISK ASSESSMENT: {risk['risk_level']} (Score: {risk['risk_score']:.2f})")
        if risk["risk_factors"]:
            print("  Factors:")
            for factor in risk["risk_factors"]:
                print(f"    • {factor}")


def main():
    parser = argparse.ArgumentParser(description="Personalized trading strategy analyzer")
    parser.add_argument("--strategy", choices=list(TRADING_STRATEGIES.keys()), 
                       default="swing", help="Trading strategy")
    parser.add_argument("--portfolio", type=str, help="Portfolio JSON file")
    parser.add_argument("--watchlist", nargs="+", help="Watchlist tickers")
    parser.add_argument("--max-headlines", type=int, default=20, help="Max headlines per ticker")
    parser.add_argument("--output", type=str, help="Output JSON file")
    parser.add_argument("--timeframe", type=str, help="Override strategy timeframe (e.g., 1y, 6m)")
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = TradingStrategyAnalyzer(args.strategy)
    print(f"🚀 Using {analyzer.strategy.name} strategy")
    print(f"📋 Description: {analyzer.strategy.description}")
    
    analyses = []
    
    # Analyze portfolio positions
    if args.portfolio:
        positions = load_portfolio_from_file(args.portfolio)
        if positions:
            print(f"\n📁 Analyzing {len(positions)} portfolio positions...")
            for position in positions:
                try:
                    analysis = analyzer.analyze_position(position, args.max_headlines)
                    analyses.append(analysis)
                except Exception as e:
                    print(f"❌ Error analyzing {position.ticker}: {e}")
    
    # Analyze watchlist
    if args.watchlist:
        print(f"\n👀 Analyzing {len(args.watchlist)} watchlist items...")
        for ticker in args.watchlist:
            try:
                analysis = analyzer.analyze_watchlist_item(ticker, args.max_headlines)
                analyses.append(analysis)
            except Exception as e:
                print(f"❌ Error analyzing {ticker}: {e}")
    
    if not analyses:
        print("❌ No positions or watchlist items to analyze")
        return
    
    # Sort by recommendation confidence
    analyses.sort(key=lambda x: x.recommendation.confidence, reverse=True)
    
    # Print results
    print_trading_analysis(analyses)
    
    # Save results
    if args.output:
        save_trading_analysis(analyses, args.output)
        print(f"\n💾 Analysis saved to: {args.output}")
    
    # Summary
    print(f"\n{'='*80}")
    print("📈 SUMMARY")
    print(f"{'='*80}")
    
    action_counts = {}
    for analysis in analyses:
        action = analysis.recommendation.action
        action_counts[action] = action_counts.get(action, 0) + 1
    
    for action, count in action_counts.items():
        action_colors = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡", "TRIM": "🟠", "ADD": "🔵"}
        icon = action_colors.get(action, "❓")
        print(f"{icon} {action}: {count}")
    
    high_confidence = [a for a in analyses if a.recommendation.confidence >= 0.7]
    print(f"\n🎯 High Confidence Recommendations (≥70%): {len(high_confidence)}")


if __name__ == "__main__":
    main()
