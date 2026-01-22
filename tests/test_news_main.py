#!/usr/bin/env python3
"""
test_news_main.py

Test the news.py main function directly.
"""

import sys
import os
import subprocess
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_news_main():
    """Test the news.py main function."""
    print('🧪 Testing News Main Function')
    print('=' * 50)
    
    # Test with a sample ticker
    ticker = 'MU'
    print(f'\n📰 Testing news main function for {ticker}...')
    
    try:
        # Call the news.py main function with arguments
        cmd = [
            'python', 'news.py',
            '--tickers', ticker,
            '--days', '180',
            '--max-headlines', '5'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd='/Users/seanbaker/codex')
        
        if result.returncode == 0:
            print('✅ News analysis completed successfully!')
            print('\n📋 Output:')
            print(result.stdout)
        else:
            print(f'❌ Error: {result.stderr}')
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_news_main()
