#!/usr/bin/env python3
"""
test_fixed_reports.py

Test the fixed report generation system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from interactive_menu import TradingSystemMenu

def test_fixed_reports():
    """Test the fixed report generation system."""
    print('🧪 Testing Fixed Report Generation')
    print('=' * 50)
    
    # Create menu instance
    menu = TradingSystemMenu()
    
    # Test with a sample ticker
    ticker = 'MU'
    print(f'\n📰 Testing report generation for {ticker}...')
    
    try:
        # Get analysis data using the fixed system
        print('\n🔄 Running analyze_ticker...')
        results = menu.system.analyze_ticker(ticker, 180)
        
        if "error" not in results:
            print('✅ Analysis completed successfully!')
            
            # Test HTML report generation
            print('📄 Testing HTML report...')
            html_content = menu._create_html_report(results, ticker, 180)
            print(f'✅ HTML report generated ({len(html_content)} characters)')
            
            # Test Markdown report generation
            print('📋 Testing Markdown report...')
            md_content = menu._create_markdown_report(results, ticker, 180)
            print(f'✅ Markdown report generated ({len(md_content)} characters)')
            
            # Test news impact section
            print('📈 Testing News Impact Section...')
            good_news = results.get('good_news_analysis', {})
            news_impact_html = menu._create_news_impact_section(good_news)
            print(f'✅ News impact section generated ({len(news_impact_html)} characters)')
            
            # Test news impact markdown
            print('📋 Testing News Impact Markdown...')
            news_impact_md = menu._create_news_impact_markdown(good_news)
            print(f'✅ News impact markdown generated ({len(news_impact_md)} characters)')
            
            # Test sentiment breakdown
            print('📊 Testing Sentiment Breakdown Section...')
            sentiment_html = menu._create_sentiment_breakdown_section(results)
            print(f'✅ Sentiment breakdown generated ({len(sentiment_html)} characters)')
            
            # Test news headlines section
            print('📰 Testing News Headlines Section...')
            headlines_html = menu._create_news_headlines_section(results)
            print(f'✅ News headlines section generated ({len(headlines_html)} characters)')
            
            print('\n✅ All report generation tests passed!')
            
            # Show sample of the data
            print('\n📊 Sample Data:')
            print(f'  Data Quality Score: {results.get("data_gates", {}).get("data_quality_score", "N/A")}')
            print(f'  News Catalysts: {len(results.get("news_catalysts", []))} items')
            print(f'  Recommendation: {results.get("recommendation", {}).get("tier", "N/A")}')
            
        else:
            print(f'❌ Error in analysis: {results["error"]}')
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
    
    print('\n✅ Fixed report test completed!')

if __name__ == "__main__":
    test_fixed_reports()
