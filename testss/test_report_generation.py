#!/usr/bin/env python3
"""
test_report_generation.py

Test the fixed report generation functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interactive_menu import TradingSystemMenu

def test_report_generation():
    """Test the fixed report generation."""
    print("🧪 Testing Fixed Report Generation")
    print("=" * 50)
    
    menu = TradingSystemMenu()
    
    # Test single stock report generation
    print("\n📄 Testing Single Stock Report...")
    
    try:
        # Simulate user input for MU
        user_input = "MU\n180\nmarkdown\n"
        
        import io
        import contextlib
        import builtins
        
        # Mock the input function
        original_input = builtins.input
        builtins.input = lambda prompt='': user_input.split('\n').pop(0) if user_input else ''
        
        # Capture the output
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            menu._generate_single_stock_report()
            
        output = f.getvalue()
        print(output)
        
        # Check if reports were generated
        if '✅ Markdown report saved' in output:
            print("✅ Report generation test completed successfully!")
            
            # Check if the file was created
            import glob
            mu_reports = glob.glob('reports/*MU*')
            if mu_reports:
                print(f"📁 Found MU reports: {len(mu_reports)} files")
                for report in mu_reports:
                    print(f"  • {report}")
            else:
                print("⚠️  No MU reports found (checking manually)")
        else:
            print("⚠️  Report generation may have issues")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Restore original input
        builtins.input = original_input

if __name__ == "__main__":
    test_report_generation()
