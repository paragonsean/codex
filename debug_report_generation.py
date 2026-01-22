#!/usr/bin/env python3
"""
debug_report_generation.py

Debug the report generation issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_trading_system import AdvancedTradingSystem

def debug_report_generation():
    """Debug the report generation issue."""
    print("🔍 Debugging Report Generation")
    print("=" * 50)
    
    system = AdvancedTradingSystem()
    
    # Get the data
    print("\n🔄 Getting analysis data...")
    results = system.analyze_ticker('MU', 180)
    
    print("\n📊 Data Structure:")
    print(f"  Ticker: {results['ticker']}")
    print(f"  Market Data Keys: {list(results['market_data'].keys())}")
    print(f"  Dual Scores Keys: {list(results['dual_scores'].keys())}")
    print(f"  Cycle Analysis Keys: {list(results['cycle_analysis'].keys())}")
    print(f"  Recommendation Keys: {list(results['recommendation'].keys())}")
    
    print("\n🔄 Cycle Analysis Details:")
    cycle = results['cycle_analysis']
    for key, value in cycle.items():
        print(f"  {key}: {value} (type: {type(value)})")
    
    print("\n🎯 Recommendation Details:")
    rec = results['recommendation']
    for key, value in rec.items():
        print(f"  {key}: {value} (type: {type(value)})")
    
    print("\n📄 Testing HTML Template...")
    
    # Test the HTML template creation
    try:
        from interactive_menu import TradingSystemMenu
        menu = TradingSystemMenu()
        
        # Test HTML template
        html_content = menu._create_html_report(results, 'MU', 180)
        print("✅ HTML template created successfully!")
        print(f"  HTML length: {len(html_content)} characters")
        
        # Test Markdown template
        md_content = menu._create_markdown_report(results, 'MU', 180)
        print("✅ Markdown template created successfully!")
        print(f"  Markdown length: {len(md_content)} characters")
        
        # Test saving
        os.makedirs("reports", exist_ok=True)
        
        html_path = "reports/debug_test.html"
        with open(html_path, 'w') as f:
            f.write(html_content)
        print(f"✅ HTML saved: {html_path}")
        
        md_path = "reports/debug_test.md"
        with open(md_path, 'w') as f:
            f.write(md_content)
        print(f"✅ Markdown saved: {md_path}")
        
    except Exception as e:
        print(f"❌ Error in template creation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_report_generation()
