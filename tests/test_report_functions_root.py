#!/usr/bin/env python3
"""
test_report_functions.py

Test the report generation functions directly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from interactive_menu import TradingSystemMenu

def test_report_functions():
    """Test the report generation functions directly."""
    print('🧪 Testing Report Generation Functions')
    print('=' * 50)
    
    # Test with a sample ticker
    ticker = 'MU'
    print(f'\n📰 Testing report functions for {ticker}...')
    
    try:
        # Create menu instance
        menu = TradingSystemMenu()
        
        # Test single stock report generation
        print('\n📄 Testing Single Stock Report Generation...')
        
        # Get analysis data
        results = menu.system.analyze_ticker(ticker, 180)
        
        if "error" not in results:
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
            
            print('\n✅ All report generation tests passed!')
            
        else:
            print(f'❌ Error in analysis: {results["error"]}')
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_report_functions()
