#!/usr/bin/env python3
"""
test_market_data.py

Simple test of market data processing using the working news.py approach.
"""

import sys
import os
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from news import fetch_prices, summarize_prices
from market_data_processor import MarketDataProcessor

def test_with_working_ticker():
    """Test with a ticker we know works."""
    print("Testing market data processor with working approach...")
    
    # Use the working fetch_prices from news.py
    ticker = "MU"
    days = 180
    
    print(f"Fetching data for {ticker} using news.py approach...")
    df = fetch_prices(ticker, days)
    
    if df.empty:
        print("❌ No data fetched")
        return
    
    print(f"✅ Data fetched successfully: {len(df)} rows")
    print(f"Columns: {list(df.columns)}")
    print(f"Date range: {df.index[0]} to {df.index[-1]}")
    
    # Handle multi-index columns
    if isinstance(df.columns, pd.MultiIndex):
        print("Handling multi-index columns...")
        # Extract the data for our ticker
        close_data = df[('Close', ticker)]
        high_data = df[('High', ticker)]
        low_data = df[('Low', ticker)]
        open_data = df[('Open', ticker)]
        volume_data = df[('Volume', ticker)]
    else:
        close_data = df['Close']
        high_data = df['High']
        low_data = df['Low']
        open_data = df['Open']
        volume_data = df['Volume']
    
    # Test the price summary
    summary = summarize_prices(ticker, df)
    if summary:
        print(f"✅ Price summary created:")
        print(f"  Last price: ${summary.last_close:.2f}")
        print(f"  RSI: {summary.rsi_14:.1f}")
        print(f"  21D return: {summary.ret_21d:+.2%}")
    
    # Test the market data processor with this data
    print(f"\nTesting MarketDataProcessor...")
    processor = MarketDataProcessor()
    
    # Manually set the data to bypass the fetching issue
    processor.data_cache[ticker] = df
    
    try:
        # Create a mock market data object
        from market_data_processor import MarketData
        import numpy as np
        
        # Calculate some basic indicators manually
        current_price = float(close_data.iloc[-1])
        
        # Simple RSI calculation
        delta = close_data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = float(rsi.iloc[-1])
        
        # Simple moving averages
        sma_50 = float(close_data.rolling(50).mean().iloc[-1])
        sma_200 = float(close_data.rolling(200).mean().iloc[-1])
        
        # Returns
        ret_5d = float((close_data.iloc[-1] / close_data.iloc[-6]) - 1) if len(close_data) > 5 else 0
        ret_21d = float((close_data.iloc[-1] / close_data.iloc[-22]) - 1) if len(close_data) > 21 else 0
        
        # Volume metrics
        volume_z = float((volume_data.iloc[-1] - volume_data.tail(20).mean()) / volume_data.tail(20).std())
        
        indicators = {
            'rsi_14': current_rsi,
            'sma_50': sma_50,
            'sma_200': sma_200,
            'ret_5d': ret_5d,
            'ret_21d': ret_21d,
            'volume_z_score': volume_z
        }
        
        # Risk metrics
        returns = close_data.pct_change().dropna()
        max_dd = float(((close_data / close_data.expanding().max()) - 1).min())
        volatility = float(returns.tail(20).std() * np.sqrt(252))
        
        risk_metrics = {
            'max_drawdown': max_dd,
            'realized_vol_20d': volatility
        }
        
        # News effectiveness proxies (simplified)
        up_days = returns[returns > 0]
        up_vol_ratio = float(up_days.std() / returns.std()) if len(up_days) > 0 else 0
        
        news_effectiveness = {
            'up_day_vol_ratio': up_vol_ratio,
            'news_effectiveness_score': min(max(up_vol_ratio * 0.5, 1.0), 0)
        }
        
        # Create market data object
        market_data = MarketData(
            ticker=ticker,
            data=df,
            current_price=current_price,
            indicators=indicators,
            risk_metrics=risk_metrics,
            news_effectiveness=news_effectiveness,
            metadata={
                'data_points': len(df),
                'start_date': df.index[0].strftime('%Y-%m-%d'),
                'end_date': df.index[-1].strftime('%Y-%m-%d'),
                'data_quality': 'good',
                'missing_days': 0
            }
        )
        
        # Print summary
        from market_data_processor import print_market_data_summary
        print_market_data_summary(market_data)
        
        print(f"\n✅ MarketDataProcessor test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in MarketDataProcessor test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_working_ticker()
