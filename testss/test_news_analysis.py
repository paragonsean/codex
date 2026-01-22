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
        price_summary = summarize_prices(ticker, df)
        
        if price_summary is not None:
            print(f'✅ Price data: ${price_summary.last_close:.2f}')
            
            # Compute combined signal
            print('📊 Computing combined signal...')
            combined_signal, notes = compute_combined_signal(price_summary, headlines)
            print(f'✅ Combined signal: {combined_signal:+.2f}')
            
            # Display results
            print('\n📋 Headlines Analysis:')
            for i, headline in enumerate(headlines[:5], 1):
                print(f'  {i}. {headline.title[:60]}...')
                print(f'     Sentiment: {headline.sentiment:+.1f}')
                print(f'     Quality: {headline.quality:.1f}')
            
            print('\n📈 Price Summary:')
            print(f'  Current: ${price_summary.last_close:.2f}')
            print(f'  5D Return: {price_summary.ret_5d:+.1%}')
            print(f'  21D Return: {price_summary.ret_21d:+.1%}')
            print(f'  63D Return: {price_summary.ret_63d:+.1%}')
            
        else:
            print('❌ No price data available')
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
    
    print('\n✅ News analysis test completed!')

if __name__ == "__main__":
    test_news_analysis()
