#!/usr/bin/env python3
"""
test_complete_report_system.py

Test the complete interactive menu report generation system.
"""

import _bootstrap

from interactive_menu import TradingSystemMenu

def test_complete_report_system():
    """Test the complete report generation system."""
    print('🧪 Testing Complete Report Generation System')
    print('=' * 60)
    
    # Test with a sample ticker
    ticker = 'MU'
    print(f'\n📰 Testing complete report generation for {ticker}...')
    
    try:
        menu = TradingSystemMenu()
        days = 180

        results = menu.system.analyze_ticker(ticker, days)
        if "error" in results:
            print(f"❌ Error: {results['error']}")
            return

        html = menu._create_html_report(results, ticker, days)
        md = menu._create_markdown_report(results, ticker, days)

        if not html or not md:
            print("❌ Report generation produced empty output")
            return

        print('✅ Report generation test completed successfully!')
        print(f"📄 HTML length: {len(html)}")
        print(f"📋 Markdown length: {len(md)}")
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_report_system()
