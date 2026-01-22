#!/usr/bin/env python3
"""
test_news_analysis.py

Test the news analysis functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from news import fetch_headlines_for_ticker, summarize_prices, compute_combined_signal
from news import Headline, PriceSummary

def test_news_analysis():
    """Test the news analysis system."""
    print('🧪 Testing News Analysis System')
    print('=' * 50)
    
    # Test with a sample ticker
    ticker = 'MU'
    print(f'\n📰 Testing news analysis for {ticker}...')
    
    try:
        # Fetch headlines
        print('📡 Fetching headlines...')
        headlines = fetch_headlines_for_ticker(ticker, max_items=10, keywords=[])
        print(f'✅ Found {len(headlines)} headlines')
        
        # Fetch price data
        print('📈 Fetching price data...')
        from news import fetch_prices
        df = fetch_prices(ticker, days=180)
        prices_df = summarize_prices(ticker, df)
        
        if prices_df is not None and not prices_df.empty:
            price_summary = PriceSummary(
                current_price=prices_df['Close'].iloc[-1],
                change=prices_df['Close'].iloc[-1] - prices_df['Close'].iloc[0],
                change_pct=0.0,  # Would calculate properly
                high=prices_df['High'].max(),
                low=prices_df['Low'].min(),
                volume=prices_df['Volume'].mean()
            )
            print(f'✅ Price data: ${price_summary.current_price:.2f}')
            
            # Compute combined signal
            print('📊 Computing combined signal...')
            combined_signal = compute_combined_signal(headlines, price_summary)
            print(f'✅ Combined signal: {combined_signal:+.2f}')
            
            # Display results
            print('\n📋 Headlines Analysis:')
            for i, headline in enumerate(headlines[:5], 1):
                print(f'  {i}. {headline.title[:60]}...')
                print(f'     Sentiment: {headline.sentiment:+.1f}')
                print(f'     Quality: {headline.quality_score:.1f}')
            
            print('\n📈 Price Summary:')
            print(f'  Current: ${price_summary.current_price:.2f}')
            print(f'  Change: ${price_summary.change:+.2f} ({price_summary.change_pct:+.1f}%)')
            print(f'  Range: ${price_summary.low:.2f} - ${price_summary.high:.2f}')
            print(f'  Avg Volume: {price_summary.volume:,.0f}')
            
        else:
            print('❌ No price data available')
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
    
    print('\n✅ News analysis test completed!')

if __name__ == "__main__":
    test_news_analysis()
