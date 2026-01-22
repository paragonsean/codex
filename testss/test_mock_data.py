#!/usr/bin/env python3
"""
test_mock_data.py

Test the improved mock data generation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_dual_scoring import create_mock_market_data

def test_mock_data():
    """Test the improved mock data generation."""
    print('🧪 Testing Improved Mock Data')
    print('=' * 40)
    
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA', 'BRK.B']
    
    for ticker in tickers:
        data = create_mock_market_data(ticker)
        print(f'\n{ticker}:')
        print(f'  Current Price: ${data.current_price:.2f}')
        print(f'  RSI: {data.indicators.get("rsi_14", "N/A")}')
        print(f'  21D Return: {data.indicators.get("ret_21d", "N/A"):+.1%}')
        print(f'  Trend: {data.indicators.get("trend_50_200", "N/A")}')
        print(f'  Volatility: {data.risk_metrics.get("volatility_regime", "N/A")}')

if __name__ == "__main__":
    test_mock_data()
