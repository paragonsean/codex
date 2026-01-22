#!/usr/bin/env python3
"""
test_dual_scoring.py

Test the dual scoring system with real market data.
"""

import sys
import os
import pandas as pd
import numpy as np
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dual_scoring_system import DualScoringSystem, DualScores, SignalCluster
from market_data_processor import MarketData
from datetime import datetime, timezone


def create_mock_market_data(ticker: str) -> MarketData:
    """Create mock market data for testing."""
    # Simulate different scenarios for different tickers
    
    scenarios = {
        'MU': {  # Overbought momentum stock
            'current_price': 389.11,
            'indicators': {
                'rsi_14': 77.5,
                'ret_5d': 0.08,
                'ret_21d': 0.565,
                'ret_63d': 0.88,
                'trend_50_200': 'bullish_transition',
                'price_vs_sma_50': 0.12,
                'price_vs_sma_200': 0.05,
                'volume_z_score': 2.1,
                'position_20d_high': 0.85,
                'atr_pct': 0.06
            },
            'risk_metrics': {
                'current_drawdown': 0.0,
                'max_drawdown': -0.205,
                'volatility_regime': 'high',
                'volatility_20d': 0.67,
                'volatility_50d': 0.55
            },
            'news_effectiveness': {
                'high_volume_win_rate': 0.6,
                'failed_breakout_frequency': 0.15,
                'avg_intraday_weakness': -0.1,
                'gap_down_frequency': 0.05
            }
        },
        'WDC': {  # Strong momentum stock
            'current_price': 241.90,
            'indicators': {
                'rsi_14': 72.8,
                'ret_5d': 0.130,
                'ret_21d': 0.382,
                'ret_63d': 0.990,
                'trend_50_200': 'bullish',
                'price_vs_sma_50': 0.15,
                'price_vs_sma_200': 0.20,
                'volume_z_score': 0.46,
                'position_20d_high': 0.90,
                'atr_pct': 0.08
            },
            'risk_metrics': {
                'current_drawdown': 0.0,
                'max_drawdown': -0.201,
                'volatility_regime': 'high',
                'volatility_20d': 0.857,
                'volatility_50d': 0.70
            },
            'news_effectiveness': {
                'high_volume_win_rate': 0.7,
                'failed_breakout_frequency': 0.1,
                'avg_intraday_weakness': -0.05,
                'gap_down_frequency': 0.03
            }
        },
        'AAPL': {  # Oversold value stock
            'current_price': 247.65,
            'indicators': {
                'rsi_14': 20.5,
                'ret_5d': -0.02,
                'ret_21d': -0.09,
                'ret_63d': -0.15,
                'trend_50_200': 'bearish',
                'price_vs_sma_50': -0.08,
                'price_vs_sma_200': -0.12,
                'volume_z_score': 1.2,
                'position_20d_high': 0.1,
                'atr_pct': 0.03
            },
            'risk_metrics': {
                'current_drawdown': -0.12,
                'max_drawdown': -0.25,
                'volatility_regime': 'low',
                'volatility_20d': 0.148,
                'volatility_50d': 0.18
            },
            'news_effectiveness': {
                'high_volume_win_rate': 0.4,
                'failed_breakout_frequency': 0.25,
                'avg_intraday_weakness': -0.15,
                'gap_down_frequency': 0.08
            }
        },
        'MSFT': {  # Tech giant - moderate growth
            'current_price': 380.50,
            'indicators': {
                'rsi_14': 65.2,
                'ret_5d': 0.025,
                'ret_21d': 0.08,
                'ret_63d': 0.22,
                'trend_50_200': 'bullish',
                'price_vs_sma_50': 0.05,
                'price_vs_sma_200': 0.15,
                'volume_z_score': 0.8,
                'position_20d_high': 0.65,
                'atr_pct': 0.04
            },
            'risk_metrics': {
                'current_drawdown': -0.05,
                'max_drawdown': -0.18,
                'volatility_regime': 'normal',
                'volatility_20d': 0.25,
                'volatility_50d': 0.22
            },
            'news_effectiveness': {
                'high_volume_win_rate': 0.65,
                'failed_breakout_frequency': 0.12,
                'avg_intraday_weakness': -0.03,
                'gap_down_frequency': 0.04
            }
        },
        'GOOGL': {  # Search giant - recovering
            'current_price': 142.80,
            'indicators': {
                'rsi_14': 45.3,
                'ret_5d': -0.015,
                'ret_21d': -0.12,
                'ret_63d': -0.28,
                'trend_50_200': 'bearish',
                'price_vs_sma_50': -0.15,
                'price_vs_sma_200': -0.25,
                'volume_z_score': 1.5,
                'position_20d_high': 0.25,
                'atr_pct': 0.05
            },
            'risk_metrics': {
                'current_drawdown': -0.18,
                'max_drawdown': -0.35,
                'volatility_regime': 'elevated',
                'volatility_20d': 0.35,
                'volatility_50d': 0.28
            },
            'news_effectiveness': {
                'high_volume_win_rate': 0.45,
                'failed_breakout_frequency': 0.20,
                'avg_intraday_weakness': -0.08,
                'gap_down_frequency': 0.06
            }
        },
        'NVDA': {  # AI chip leader - volatile
            'current_price': 485.60,
            'indicators': {
                'rsi_14': 78.9,
                'ret_5d': 0.12,
                'ret_21d': 0.35,
                'ret_63d': 0.95,
                'trend_50_200': 'bullish',
                'price_vs_sma_50': 0.18,
                'price_vs_sma_200': 0.35,
                'volume_z_score': 2.5,
                'position_20d_high': 0.95,
                'atr_pct': 0.09
            },
            'risk_metrics': {
                'current_drawdown': 0.0,
                'max_drawdown': -0.22,
                'volatility_regime': 'high',
                'volatility_20d': 0.85,
                'volatility_50d': 0.65
            },
            'news_effectiveness': {
                'high_volume_win_rate': 0.75,
                'failed_breakout_frequency': 0.08,
                'avg_intraday_weakness': -0.02,
                'gap_down_frequency': 0.02
            }
        },
        'TSLA': {  # EV maker - high volatility
            'current_price': 195.30,
            'indicators': {
                'rsi_14': 55.8,
                'ret_5d': -0.05,
                'ret_21d': -0.18,
                'ret_63d': 0.15,
                'trend_50_200': 'bearish',
                'price_vs_sma_50': -0.12,
                'price_vs_sma_200': -0.08,
                'volume_z_score': 1.8,
                'position_20d_high': 0.45,
                'atr_pct': 0.08
            },
            'risk_metrics': {
                'current_drawdown': -0.15,
                'max_drawdown': -0.45,
                'volatility_regime': 'high',
                'volatility_20d': 0.65,
                'volatility_50d': 0.55
            },
            'news_effectiveness': {
                'high_volume_win_rate': 0.35,
                'failed_breakout_frequency': 0.30,
                'avg_intraday_weakness': -0.12,
                'gap_down_frequency': 0.10
            }
        },
        'BRK.B': {  # Berkshire Hathaway - stable value
            'current_price': 425.80,
            'indicators': {
                'rsi_14': 42.1,
                'ret_5d': 0.008,
                'ret_21d': 0.02,
                'ret_63d': 0.08,
                'trend_50_200': 'bullish',
                'price_vs_sma_50': 0.02,
                'price_vs_sma_200': 0.12,
                'volume_z_score': 0.3,
                'position_20d_high': 0.35,
                'atr_pct': 0.02
            },
            'risk_metrics': {
                'current_drawdown': -0.03,
                'max_drawdown': -0.15,
                'volatility_regime': 'low',
                'volatility_20d': 0.12,
                'volatility_50d': 0.15
            },
            'news_effectiveness': {
                'high_volume_win_rate': 0.70,
                'failed_breakout_frequency': 0.05,
                'avg_intraday_weakness': -0.01,
                'gap_down_frequency': 0.01
            }
        }
    }
    
    scenario = scenarios.get(ticker, scenarios['MU'])
    
    # Create mock DataFrame
    dates = pd.date_range('2025-01-01', '2026-01-21', freq='D')
    # Remove weekends
    dates = dates[dates.weekday < 5]
    
    # Generate realistic price data
    np.random.seed(hash(ticker) % 2**32)  # Use ticker for consistent random seed
    base_price = scenario['current_price']
    returns = np.random.normal(0.001, 0.02, len(dates))
    prices = [base_price * 0.9]  # Start lower
    
    for ret in returns:
        prices.append(prices[-1] * (1 + ret))
    
    prices = prices[1:]  # Remove initial price
    
    df = pd.DataFrame({
        'Open': prices,
        'High': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'Low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'Close': prices,
        'Volume': [int(1e6 * (1 + np.random.normal(0, 0.3))) for _ in prices]
    }, index=dates)
    
    return MarketData(
        ticker=ticker,
        data=df,
        current_price=scenario['current_price'],
        indicators=scenario['indicators'],
        risk_metrics=scenario['risk_metrics'],
        news_effectiveness=scenario['news_effectiveness'],
        metadata={
            'data_points': len(df),
            'start_date': df.index[0].strftime('%Y-%m-%d'),
            'end_date': df.index[-1].strftime('%Y-%m-%d'),
            'data_quality': 'mock',
            'missing_days': 0
        }
    )


def test_dual_scoring():
    """Test the dual scoring system with different scenarios."""
    print("🧪 Testing Dual Scoring System")
    print("=" * 60)
    
    scorer = DualScoringSystem()
    tickers = ['MU', 'WDC', 'AAPL']
    
    for ticker in tickers:
        print(f"\n{'='*80}")
        print(f"🎯 Analyzing {ticker}")
        print(f"{'='*80}")
        
        # Create mock market data
        market_data = create_mock_market_data(ticker)
        
        # Calculate scores
        scores = scorer.calculate_scores(market_data)
        
        # Print results
        from dual_scoring_system import print_dual_scores
        print_dual_scores(scores)
        
        # Show cluster details
        print(f"\n📊 Cluster Analysis:")
        print(f"Opportunity Clusters Triggered: {sum(1 for c in scores.opportunity_clusters if c.triggered)}/3")
        print(f"Sell-Risk Clusters Triggered: {sum(1 for c in scores.sell_risk_clusters if c.triggered)}/4")
        
        print(f"\n🎯 Trading Recommendation:")
        if scores.overall_bias in ["STRONG_BUY", "BUY"]:
            print(f"✅ {scores.overall_bias} - Opportunity score {scores.opportunity_score:.1f} significantly exceeds risk score {scores.sell_risk_score:.1f}")
        elif scores.overall_bias == "HOLD":
            print(f"⚖️  HOLD - Balanced opportunity ({scores.opportunity_score:.1f}) and risk ({scores.sell_risk_score:.1f}) scores")
        else:
            print(f"❌ {scores.overall_bias} - Sell-risk score {scores.sell_risk_score:.1f} significantly exceeds opportunity score {scores.opportunity_score:.1f}")


def demonstrate_signal_clustering():
    """Demonstrate how signal clustering works."""
    print(f"\n{'='*80}")
    print("🔍 SIGNAL CLUSTERING DEMONSTRATION")
    print(f"{'='*80}")
    
    print("\n📋 Why Signal Clustering Matters:")
    print("• Single indicators can be noisy and unreliable")
    print("• Clusters of related signals provide stronger confirmation")
    print("• Different market conditions require different signal emphasis")
    print("• Reduces false signals and improves decision quality")
    
    print("\n🎯 Example: MU Overheating Analysis")
    print("Individual Signals:")
    print("  • RSI = 77.5 (overbought) → Moderate sell signal")
    print("  • 21D return = +56.6% (strong gains) → Moderate sell signal") 
    print("  • Volatility = 67% (high) → Weak sell signal")
    print("  • Volume Z-score = 2.1 (high) → Ambiguous signal")
    
    print("\nCluster Analysis:")
    print("  📊 Technical Overheating Cluster:")
    print("    • RSI overbought (>70) ✅")
    print("    • Extended gains (>30% in 3mo) ✅") 
    print("    • High volatility with gains ✅")
    print("    → Cluster STRENGTH: 0.7 (Strong)")
    print("    → Cluster WEIGHT: 0.35 (High importance)")
    
    print("\n  📊 Distribution Behavior Cluster:")
    print("    • High volume win rate = 60% ❌ (Good)")
    print("    • Failed breakout frequency = 15% ❌ (Low)")
    print("    → Cluster STRENGTH: 0.0 (Not triggered)")
    
    print("\n🎯 Final Assessment:")
    print("• Multiple overheating signals create strong sell-risk cluster")
    print("• Lack of distribution signals reduces overall risk")
    print("• Result: Moderate sell-risk score with specific overheating concerns")


if __name__ == "__main__":
    test_dual_scoring()
    demonstrate_signal_clustering()
