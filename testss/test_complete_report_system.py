#!/usr/bin/env python3
"""
test_complete_report_system.py

Test the complete interactive menu report generation system.
"""

import sys
import os
import subprocess
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_complete_report_system():
    """Test the complete report generation system."""
    print('🧪 Testing Complete Report Generation System')
    print('=' * 60)
    
    # Test with a sample ticker
    ticker = 'MU'
    print(f'\n📰 Testing complete report generation for {ticker}...')
    
    try:
        # Test the interactive menu directly
        cmd = [
            'python', 'interactive_menu.py'
        ]
        
        # We'll simulate user input for testing
        user_input = f'{ticker}\n180\nboth\n'
        
        # Use subprocess to send input
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd='/Users/seanbaker/codex'
        )
        
        # Send the simulated input
        stdout, stderr = process.communicate(input=user_input, timeout=30)
        
        if process.returncode == 0:
            print('✅ Report generation test completed successfully!')
            print('\n📋 Output:')
            print(stdout)
        else:
            print(f'❌ Error: {stderr}')
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_report_system()
