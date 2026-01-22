#!/usr/bin/env python3
"""
test_portfolio_analysis.py

Test portfolio analysis with improved mock data.
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_trading_system import AdvancedTradingSystem

def test_portfolio_analysis():
    """Test portfolio analysis with improved mock data."""
    print('📊 Testing Portfolio Analysis with Improved Mock Data')
    print('=' * 60)
    
    # Create a test portfolio with the CSV data
    portfolio_data = {
        'portfolio_name': 'Test Portfolio',
        'positions': [
            {'ticker': 'AAPL', 'shares': 100, 'cost_basis': 150.25, 'notes': 'Core position'},
            {'ticker': 'MSFT', 'shares': 50, 'cost_basis': 250.50, 'notes': 'Cloud exposure'},
            {'ticker': 'GOOGL', 'shares': 25, 'cost_basis': 2800.00, 'notes': 'Search dominance'},
            {'ticker': 'NVDA', 'shares': 75, 'cost_basis': 450.75, 'notes': 'AI play'},
            {'ticker': 'TSLA', 'shares': 30, 'cost_basis': 200.00, 'notes': 'Growth stock'},
            {'ticker': 'BRK.B', 'shares': 10, 'cost_basis': 350.00, 'notes': 'Value holding'}
        ]
    }
    
    # Save test portfolio
    with open('test_portfolio.json', 'w') as f:
        json.dump(portfolio_data, f, indent=2)
    
    # Run portfolio analysis
    system = AdvancedTradingSystem()
    
    try:
        results = system.analyze_portfolio('test_portfolio.json', 180)
        
        if 'error' not in results:
            print(f'Portfolio: {results["portfolio_name"]}')
            print(f'Total Positions: {results["summary"]["total_positions"]}')
            print(f'Total Value: ${results["summary"]["total_value"]:,.2f}')
            print(f'Total P&L: ${results["summary"]["total_unrealized_pnl"]:+,.2f}')
            
            print('\nTop 3 Positions:')
            for pos in results['positions'][:3]:
                pos_data = pos['position']
                print(f'  {pos["ticker"]}: ${pos_data["current_value"]:,.2f} ({pos_data["unrealized_pnl_pct"]:+.1%})')
            
            print(f'\nRecommendations:')
            high_risk = [pos for pos in results['positions'] if pos['recommendation']['tier'] == 'EXIT/RISK OFF']
            print(f'  High Risk: {len(high_risk)} positions')
            
            print('\nPosition Details:')
            for pos in results['positions']:
                pos_data = pos['position']
                rec = pos['recommendation']
                print(f'  {pos["ticker"]}: {rec["tier"]} ({rec["urgency"]})')
                print(f'    Price: ${pos_data["current_value"]/pos_data["shares"]:.2f} | P&L: {pos_data["unrealized_pnl_pct"]:+.1%}')
            
        else:
            print(f'Error: {results["error"]}')
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_portfolio_analysis()
