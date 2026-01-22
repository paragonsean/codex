#!/usr/bin/env python3
"""
test_gated_reports.py

Test the gated system through the interactive menu.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interactive_menu import TradingSystemMenu

def test_gated_reports():
    """Test the gated system through interactive menu."""
    print('🧪 Testing Gated Report Generation')
    print('=' * 50)
    
    # Create menu instance
    menu = TradingSystemMenu()
    
    # Test with different lookback periods
    test_cases = [
        ('MU', 30),   # Should trigger 50DMA gate
        ('MU', 180),  # Normal case
    ]
    
    for ticker, lookback in test_cases:
        print(f'\n📊 Testing {ticker} with {lookback} days lookback...')
        
        try:
            # Get analysis data
            results = menu.system.analyze_ticker(ticker, lookback)
            
            if "error" not in results:
                # Check gates
                data_gates = results.get('data_gates', {})
                news_gates = results.get('news_gates', {})
                recommendation = results.get('recommendation', {})
                
                print(f'✅ Analysis completed')
                print(f'📊 Data Quality Score: {data_gates.get("data_quality_score", 0):.1f}%')
                print(f'🚫 Data Restrictions: {len(data_gates.get("restrictions", []))}')
                print(f'📰 News Restrictions: {len(news_gates.get("restrictions", []))}')
                print(f'🎯 Recommendation: {recommendation.get("tier", "N/A")} (Confidence: {recommendation.get("confidence", 0):.1f}%)')
                
                # Show applied restrictions
                if data_gates.get("restrictions"):
                    print('⚠️  Data Restrictions:')
                    for restriction in data_gates["restrictions"]:
                        print(f'   - {restriction}')
                
                if news_gates.get("restrictions"):
                    print('📰 News Restrictions:')
                    for restriction in news_gates["restrictions"]:
                        print(f'   - {restriction}')
                
                # Show gate info if available
                if 'applied_gates' in recommendation:
                    gates = recommendation['applied_gates']
                    print(f'🔒 Applied Gates: Data Score={gates.get("data_quality_score", 0):.1f}%')
                
                # Generate report to test full integration
                print('📄 Generating report...')
                html_content = menu._create_html_report(results, ticker, lookback)
                print(f'✅ Report generated ({len(html_content)} characters)')
                
            else:
                print(f'❌ Error: {results["error"]}')
                
        except Exception as e:
            print(f'❌ Error: {e}')
            import traceback
            traceback.print_exc()
    
    print('\n✅ Gated report test completed!')

if __name__ == "__main__":
    test_gated_reports()
