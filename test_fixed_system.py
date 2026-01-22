#!/usr/bin/env python3
"""
test_fixed_system.py

Test the fixed advanced trading system directly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_trading_system import AdvancedTradingSystem

def test_fixed_system():
    """Test the fixed advanced trading system."""
    print('🧪 Testing Fixed Advanced Trading System')
    print('=' * 60)
    
    # Test with a sample ticker
    ticker = 'MU'
    print(f'\n📰 Testing {ticker} with fixed system...')
    
    try:
        # Create system instance
        system = AdvancedTradingSystem()
        
        # Test single stock analysis
        print('\n🔄 Running analyze_ticker...')
        results = system.analyze_ticker(ticker, 180)
        
        if "error" not in results:
            print('✅ Analysis completed successfully!')
            
            # Check key data structures
            print(f'\n📊 Data Quality Score: {results.get("data_gates", {}).get("data_quality_score", "N/A")}')
            print(f'📰 News Catalysts: {len(results.get("news_catalysts", []))} items')
            print(f'📈 Good News Analysis: {type(results.get("good_news_analysis", {}))}')
            
            # Check if we have proper data types
            news_catalysts = results.get('news_catalysts', [])
            if news_catalysts and len(news_catalysts) > 0:
                first_catalyst = news_catalysts[0]
                print(f'🔍 First catalyst type: {type(first_catalyst)}')
                if hasattr(first_catalyst, 'headline'):
                    print(f'📰 Headline type: {type(first_catalyst.headline)}')
                    if hasattr(first_catalyst.headline, 'sentiment'):
                        print(f'✅ Headline has sentiment: {first_catalyst.headline.sentiment}')
                    else:
                        print('❌ Headline missing sentiment attribute')
            
            # Test recommendation generation
            recommendation = results.get('recommendation', {})
            if recommendation:
                print(f'🎯 Recommendation: {recommendation.get("tier", "N/A")} (Confidence: {recommendation.get("confidence", 0):.1f}%)')
            
        else:
            print(f'❌ Error: {results["error"]}')
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
    
    print('\n✅ Fixed system test completed!')

if __name__ == "__main__":
    test_fixed_system()
