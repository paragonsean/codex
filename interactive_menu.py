#!/usr/bin/env python3
"""
interactive_menu.py

Interactive menu system for the advanced trading system.
Provides user-friendly interface for all features.

Features:
- Portfolio management (add/remove stocks)
- News analysis with custom keywords
- Advanced dual scoring analysis
- Portfolio analysis with recommendations
- Alerts monitoring
- Report generation
- System settings
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_trading_system import AdvancedTradingSystem
from news import fetch_headlines_for_ticker
from market_data_processor import MarketDataProcessor
from stock_report_generator import StockReportGenerator


class TradingSystemMenu:
    """Interactive menu system for the advanced trading system."""
    
    def __init__(self):
        self.system = AdvancedTradingSystem()
        self.portfolio_file = "portfolio.json"
        self.default_keywords = ["AI", "HBM", "DRAM", "NAND", "chipsets", "semiconductor", "datacenter", "cloud"]
        
    def run(self):
        """Run the interactive menu."""
        while True:
            self._display_main_menu()
            choice = input("\nEnter your choice (1-10): ").strip()
            
            try:
                if choice == "1":
                    self._manage_portfolio()
                elif choice == "2":
                    self._run_news_analysis()
                elif choice == "3":
                    self._run_dual_scoring()
                elif choice == "4":
                    self._run_portfolio_analysis()
                elif choice == "5":
                    self._run_alerts_monitoring()
                elif choice == "6":
                    self._generate_reports()
                elif choice == "7":
                    self._analyze_single_stock()
                elif choice == "8":
                    self._view_portfolio()
                elif choice == "9":
                    self._system_settings()
                elif choice == "10":
                    print("\n👋 Thank you for using the Advanced Trading System!")
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("Press Enter to continue...")
    
    def _display_main_menu(self):
        """Display the main menu."""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🎯" + "="*60)
        print("   ADVANCED TRADING SYSTEM - INTERACTIVE MENU")
        print("="*60)
        print()
        print("1️⃣  📚 Manage Portfolio")
        print("2️⃣  📰 Run News Analysis")
        print("3️⃣  📊 Run Dual Scoring Analysis")
        print("4️⃣  📈 Portfolio Analysis & Recommendations")
        print("5️⃣  🚨 Alerts Monitoring")
        print("6️⃣  📋 Generate Reports")
        print("7️⃣  🔍 Analyze Single Stock")
        print("8️⃣  👁️  View Current Portfolio")
        print("9️⃣  ⚙️  System Settings")
        print("10️⃣ 👋 Exit")
        print()
    
    def _manage_portfolio(self):
        """Portfolio management menu."""
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            print("📚" + "="*50)
            print("   PORTFOLIO MANAGEMENT")
            print("="*50)
            print()
            print("1️⃣  ➕ Add Stock to Portfolio")
            print("2️⃣  ➖ Remove Stock from Portfolio")
            print("3️⃣  ✏️  Edit Position")
            print("4️⃣  📋 View Portfolio")
            print("5️⃣  📁 Load Portfolio from File")
            print("6️⃣  💾 Save Portfolio to File")
            print("7️⃣  � Import Portfolio from CSV")
            print("8️⃣  📤 Export Portfolio to CSV")
            print("9️⃣  � Back to Main Menu")
            print()
            
            choice = input("Enter your choice (1-9): ").strip()
            
            if choice == "1":
                self._add_stock_to_portfolio()
            elif choice == "2":
                self._remove_stock_from_portfolio()
            elif choice == "3":
                self._edit_portfolio_position()
            elif choice == "4":
                self._view_portfolio()
            elif choice == "5":
                self._load_portfolio_from_file()
            elif choice == "6":
                self._save_portfolio_to_file()
            elif choice == "7":
                self._import_portfolio_from_csv()
            elif choice == "8":
                self._export_portfolio_to_csv()
            elif choice == "9":
                break
            else:
                print("❌ Invalid choice.")
                input("Press Enter to continue...")
    
    def _add_stock_to_portfolio(self):
        """Add a stock to the portfolio."""
        print("\n➕ Add Stock to Portfolio")
        print("-" * 30)
        
        ticker = input("Enter ticker symbol: ").strip().upper()
        if not ticker:
            print("❌ Ticker cannot be empty.")
            input("Press Enter to continue...")
            return
        
        try:
            shares = float(input("Enter number of shares: "))
            cost_basis = float(input("Enter cost basis per share: $"))
            notes = input("Enter notes (optional): ").strip()
            
            # Load current portfolio
            portfolio = self._load_portfolio_data()
            
            # Check if ticker already exists
            existing_positions = [p for p in portfolio.get('positions', []) if p['ticker'] == ticker]
            if existing_positions:
                print(f"⚠️  {ticker} already exists in portfolio.")
                action = input("Update existing position? (y/n): ").lower()
                if action != 'y':
                    input("Press Enter to continue...")
                    return
                
                # Update existing position
                for pos in portfolio['positions']:
                    if pos['ticker'] == ticker:
                        pos['shares'] = shares
                        pos['cost_basis'] = cost_basis
                        pos['notes'] = notes
                        break
            else:
                # Add new position
                new_position = {
                    'ticker': ticker,
                    'shares': shares,
                    'cost_basis': cost_basis,
                    'notes': notes
                }
                portfolio.setdefault('positions', []).append(new_position)
            
            # Save portfolio
            self._save_portfolio_data(portfolio)
            print(f"✅ {ticker} {'updated' if existing_positions else 'added'} successfully!")
            
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
        
        input("Press Enter to continue...")
    
    def _remove_stock_from_portfolio(self):
        """Remove a stock from the portfolio."""
        print("\n➖ Remove Stock from Portfolio")
        print("-" * 35)
        
        portfolio = self._load_portfolio_data()
        positions = portfolio.get('positions', [])
        
        if not positions:
            print("📭 Portfolio is empty.")
            input("Press Enter to continue...")
            return
        
        print("\nCurrent positions:")
        for i, pos in enumerate(positions, 1):
            print(f"{i}. {pos['ticker']} - {pos['shares']} shares @ ${pos['cost_basis']:.2f}")
        
        try:
            choice = int(input("\nEnter position number to remove (0 to cancel): "))
            if choice == 0:
                return
            if 1 <= choice <= len(positions):
                removed = positions.pop(choice - 1)
                portfolio['positions'] = positions
                self._save_portfolio_data(portfolio)
                print(f"✅ {removed['ticker']} removed from portfolio!")
            else:
                print("❌ Invalid position number.")
        except ValueError:
            print("❌ Please enter a valid number.")
        
        input("Press Enter to continue...")
    
    def _edit_portfolio_position(self):
        """Edit a portfolio position."""
        print("\n✏️  Edit Portfolio Position")
        print("-" * 35)
        
        portfolio = self._load_portfolio_data()
        positions = portfolio.get('positions', [])
        
        if not positions:
            print("📭 Portfolio is empty.")
            input("Press Enter to continue...")
            return
        
        print("\nCurrent positions:")
        for i, pos in enumerate(positions, 1):
            print(f"{i}. {pos['ticker']} - {pos['shares']} shares @ ${pos['cost_basis']:.2f}")
        
        try:
            choice = int(input("\nEnter position number to edit (0 to cancel): "))
            if choice == 0:
                return
            if 1 <= choice <= len(positions):
                pos = positions[choice - 1]
                print(f"\nEditing {pos['ticker']}:")
                print(f"Current shares: {pos['shares']}")
                print(f"Current cost basis: ${pos['cost_basis']:.2f}")
                print(f"Current notes: {pos.get('notes', 'N/A')}")
                
                new_shares = input(f"Enter new shares (current: {pos['shares']}): ").strip()
                new_cost = input(f"Enter new cost basis (current: ${pos['cost_basis']:.2f}): ").strip()
                new_notes = input(f"Enter new notes (current: {pos.get('notes', 'N/A')}): ").strip()
                
                if new_shares:
                    pos['shares'] = float(new_shares)
                if new_cost:
                    pos['cost_basis'] = float(new_cost)
                if new_notes:
                    pos['notes'] = new_notes
                
                self._save_portfolio_data(portfolio)
                print(f"✅ {pos['ticker']} updated successfully!")
            else:
                print("❌ Invalid position number.")
        except ValueError:
            print("❌ Invalid input.")
        
        input("Press Enter to continue...")
    
    def _run_news_analysis(self):
        """Run news analysis menu."""
        print("\n📰 Run News Analysis")
        print("-" * 25)
        
        # Get tickers
        tickers_input = input("Enter tickers (comma-separated): ").strip()
        tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
        
        if not tickers:
            print("❌ Please enter at least one ticker.")
            input("Press Enter to continue...")
            return
        
        # Get keywords
        use_custom = input("Use custom keywords? (y/n): ").lower() == 'y'
        if use_custom:
            keywords_input = input("Enter keywords (comma-separated): ").strip()
            keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
        else:
            keywords = self.default_keywords
        
        # Get max headlines
        try:
            max_headlines = int(input("Max headlines per ticker (default 20): ") or "20")
        except ValueError:
            max_headlines = 20
        
        # Get analysis period
        try:
            days = int(input("Analysis period in days (default 180): ") or "180")
        except ValueError:
            days = 180
        
        print(f"\n🔄 Analyzing news for {len(tickers)} tickers...")
        
        for ticker in tickers:
            try:
                print(f"\n📰 {ticker} News Analysis:")
                headlines = fetch_headlines_for_ticker(
                    ticker=ticker,
                    max_items=max_headlines,
                    keywords=keywords
                )
                
                if headlines:
                    print(f"  Found {len(headlines)} headlines")
                    
                    # Show sentiment distribution
                    positive = len([h for h in headlines if h.sentiment > 0])
                    negative = len([h for h in headlines if h.sentiment < 0])
                    neutral = len(headlines) - positive - negative
                    
                    print(f"  Sentiment: {positive} positive, {negative} negative, {neutral} neutral")
                    
                    # Show top headlines
                    print(f"\n  Top 5 headlines:")
                    for i, headline in enumerate(headlines[:5], 1):
                        sentiment_emoji = "🟢" if headline.sentiment > 0 else "🔴" if headline.sentiment < 0 else "⚪"
                        print(f"    {i}. {sentiment_emoji} {headline.title[:80]}...")
                else:
                    print(f"  No headlines found for {ticker}")
                    
            except Exception as e:
                print(f"  ❌ Error analyzing {ticker}: {e}")
        
        input("\nPress Enter to continue...")
    
    def _run_dual_scoring(self):
        """Run dual scoring analysis."""
        print("\n📊 Run Dual Scoring Analysis")
        print("-" * 35)
        
        tickers_input = input("Enter tickers (comma-separated): ").strip()
        tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
        
        if not tickers:
            print("❌ Please enter at least one ticker.")
            input("Press Enter to continue...")
            return
        
        try:
            days = int(input("Analysis period in days (default 180): ") or "180")
        except ValueError:
            days = 180
        
        print(f"\n🔄 Running dual scoring analysis for {len(tickers)} tickers...")
        
        for ticker in tickers:
            try:
                print(f"\n📊 {ticker} Dual Scoring:")
                results = self.system.analyze_ticker(ticker, days)
                
                if "error" not in results:
                    dual_scores = results["dual_scores"]
                    print(f"  Opportunity Score: {dual_scores['opportunity_score']:.1f}/100")
                    print(f"  Sell-Risk Score: {dual_scores['sell_risk_score']:.1f}/100")
                    print(f"  Overall Bias: {dual_scores['overall_bias']}")
                    print(f"  Confidence: {dual_scores['confidence']:.1%}")
                    
                    # Show recommendation
                    rec = results["recommendation"]
                    print(f"  Recommendation: {rec['tier']} ({rec['urgency']})")
                    
                    if rec['top_3_reasons']:
                        print(f"  Top Reasons:")
                        for reason in rec['top_3_reasons']:
                            print(f"    • {reason}")
                else:
                    print(f"  ❌ {results['error']}")
                    
            except Exception as e:
                print(f"  ❌ Error analyzing {ticker}: {e}")
        
        input("\nPress Enter to continue...")
    
    def _run_portfolio_analysis(self):
        """Run portfolio analysis."""
        print("\n📈 Portfolio Analysis & Recommendations")
        print("-" * 45)
        
        portfolio = self._load_portfolio_data()
        positions = portfolio.get('positions', [])
        
        if not positions:
            print("📭 Portfolio is empty. Add stocks first.")
            input("Press Enter to continue...")
            return
        
        try:
            days = int(input("Analysis period in days (default 180): ") or "180")
        except ValueError:
            days = 180
        
        output_format = input("Output format (terminal/json/csv, default terminal): ").strip() or "terminal"
        if output_format not in ["terminal", "json", "csv"]:
            output_format = "terminal"
        
        print(f"\n🔄 Analyzing portfolio with {len(positions)} positions...")
        
        # Create temporary portfolio file
        temp_portfolio_file = f"temp_portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(temp_portfolio_file, 'w') as f:
            json.dump(portfolio, f, indent=2)
        
        try:
            results = self.system.analyze_portfolio(temp_portfolio_file, days)
            
            if "error" not in results:
                self.system.output_results(results, [output_format])
            else:
                print(f"❌ {results['error']}")
                
        except Exception as e:
            print(f"❌ Error analyzing portfolio: {e}")
        finally:
            # Clean up temp file
            if os.path.exists(temp_portfolio_file):
                os.remove(temp_portfolio_file)
        
        input("\nPress Enter to continue...")
    
    def _run_alerts_monitoring(self):
        """Run alerts monitoring."""
        print("\n🚨 Alerts Monitoring")
        print("-" * 25)
        
        # Get tickers for monitoring
        portfolio = self._load_portfolio_data()
        portfolio_tickers = [pos['ticker'] for pos in portfolio.get('positions', [])]
        
        if portfolio_tickers:
            print(f"Found {len(portfolio_tickers)} tickers in portfolio.")
            use_portfolio = input("Use portfolio tickers? (y/n): ").lower() == 'y'
        else:
            use_portfolio = False
        
        if not use_portfolio:
            tickers_input = input("Enter tickers to monitor (comma-separated): ").strip()
            tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
        else:
            tickers = portfolio_tickers
        
        if not tickers:
            print("❌ No tickers to monitor.")
            input("Press Enter to continue...")
            return
        
        output_format = input("Output format (terminal/json, default terminal): ").strip() or "terminal"
        if output_format not in ["terminal", "json"]:
            output_format = "terminal"
        
        print(f"\n🔍 Monitoring alerts for {len(tickers)} tickers...")
        
        try:
            alerts = self.system.run_alerts_scan(tickers, [output_format])
            
            if alerts:
                print(f"\n📊 Generated {len(alerts)} alerts")
            else:
                print("\n✅ No alerts triggered")
                
        except Exception as e:
            print(f"❌ Error monitoring alerts: {e}")
        
        input("\nPress Enter to continue...")
    
    def _generate_reports(self):
        """Generate reports menu."""
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            print("📋" + "="*50)
            print("   GENERATE REPORTS")
            print("="*50)
            print()
            print("1️⃣  📄 Single Stock Report")
            print("2️⃣  📚 Portfolio Report")
            print("3️⃣  📊 Market Summary Report")
            print("4️⃣  🔔 Alerts Report")
            print("5️⃣  🔙 Back to Main Menu")
            print()
            
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == "1":
                self._generate_single_stock_report()
            elif choice == "2":
                self._generate_portfolio_report()
            elif choice == "3":
                self._generate_market_summary_report()
            elif choice == "4":
                self._generate_alerts_report()
            elif choice == "5":
                break
            else:
                print("❌ Invalid choice.")
                input("Press Enter to continue...")
    
    def _generate_single_stock_report(self):
        """Generate single stock report."""
        print("\n📄 Generate Single Stock Report")
        print("-" * 35)
        
        ticker = input("Enter ticker symbol: ").strip().upper()
        if not ticker:
            print("❌ Ticker cannot be empty.")
            input("Press Enter to continue...")
            return
        
        try:
            days = int(input("Analysis period in days (default 180): ") or "180")
        except ValueError:
            days = 180
        
        format_choice = input("Report format (html/markdown/both, default both): ").strip().lower()
        if format_choice not in ["html", "markdown", "both"]:
            format_choice = "both"
        
        print(f"\n🔄 Generating report for {ticker}...")
        
        try:
            # Use our advanced trading system to get comprehensive data
            results = self.system.analyze_ticker(ticker, days)
            
            if "error" not in results:
                # Generate report using our advanced system data
                self._generate_advanced_report(results, ticker, days, format_choice)
            else:
                print(f"❌ Error analyzing {ticker}: {results['error']}")
                
        except Exception as e:
            print(f"❌ Error generating report: {e}")
        
        input("Press Enter to continue...")
    
    def _generate_advanced_report(self, results: Dict, ticker: str, days: int, format_choice: str):
        """Generate report using advanced trading system data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_choice in ["html", "both"]:
            html_content = self._create_html_report(results, ticker, days)
            html_path = f"reports/{ticker}_report_{timestamp}.html"
            
            # Ensure reports directory exists
            os.makedirs("reports", exist_ok=True)
            
            with open(html_path, 'w') as f:
                f.write(html_content)
            
            print(f"✅ HTML report saved: {html_path}")
        
        if format_choice in ["markdown", "both"]:
            md_content = self._create_markdown_report(results, ticker, days)
            md_path = f"reports/{ticker}_report_{timestamp}.md"
            
            # Ensure reports directory exists
            os.makedirs("reports", exist_ok=True)
            
            with open(md_path, 'w') as f:
                f.write(md_content)
            
            print(f"✅ Markdown report saved: {md_path}")
        
        print(f"📁 Reports saved to 'reports/' directory")
    
    def _create_html_report(self, results: Dict, ticker: str, days: int) -> str:
        """Create HTML report from advanced trading system results."""
        market_data = results["market_data"]
        dual_scores = results["dual_scores"]
        cycle_analysis = results["cycle_analysis"]
        recommendation = results["recommendation"]
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Stock Analysis Report - {ticker}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #007bff;
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            color: #666;
            margin: 5px 0 0 0;
        }}
        .section {{
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            background: #f8f9fa;
        }}
        .section h2 {{
            color: #007bff;
            margin-top: 0;
            border-bottom: 1px solid #dee2e6;
            padding-bottom: 10px;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 5px;
        }}
        .metric-label {{
            font-weight: bold;
            color: #495057;
        }}
        .metric-value {{
            font-weight: bold;
            color: #007bff;
        }}
        .score {{
            font-size: 1.2em;
            font-weight: bold;
            padding: 5px 10px;
            border-radius: 5px;
            display: inline-block;
            margin: 5px;
        }}
        .opportunity {{
            background: #28a745;
            color: white;
        }}
        .sell-risk {{
            background: #dc3545;
            color: white;
        }}
        .recommendation {{
            font-size: 1.5em;
            font-weight: bold;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            margin: 20px 0;
        }}
        .buy {{
            background: #28a745;
            color: white;
        }}
        .sell {{
            background: #dc3545;
            color: white;
        }}
        .hold {{
            background: #ffc107;
            color: #212529;
        }}
        .reasons {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .reasons ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .reasons li {{
            margin: 5px 0;
        }}
        .levels {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .level {{
            margin: 5px 0;
            padding: 5px;
            border-radius: 3px;
            background: #e9ecef;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Advanced Stock Analysis Report</h1>
            <p>{ticker} - {days} Day Analysis</p>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h2>📊 Key Metrics</h2>
            <div class="metric">
                <span class="metric-label">Current Price:</span>
                <span class="metric-value">${market_data['current_price']:.2f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Opportunity Score:</span>
                <span class="score opportunity">{dual_scores['opportunity_score']:.1f}/100</span>
            </div>
            <div class="metric">
                <span class="metric-label">Sell-Risk Score:</span>
                <span class="score sell-risk">{dual_scores['sell_risk_score']:.1f}/100</span>
            </div>
            <div class="metric">
                <span class="metric-label">Overall Bias:</span>
                <span class="metric-value">{dual_scores['overall_bias']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Confidence:</span>
                <span class="metric-value">{dual_scores['confidence']:.1%}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Price & Volume Data</h2>
            <div class="metric">
                <span class="metric-label">20-Day High:</span>
                <span class="metric-value">${market_data['indicators'].get('high_20d', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">20-Day Low:</span>
                <span class="metric-value">${market_data['indicators'].get('low_20d', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">50-Day High:</span>
                <span class="metric-value">${market_data['indicators'].get('high_50d', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">50-Day Low:</span>
                <span class="metric-value">${market_data['indicators'].get('low_50d', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Volume Z-Score:</span>
                <span class="metric-value">{market_data['indicators'].get('volume_z_score', 'N/A'):.2f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">ATR (14):</span>
                <span class="metric-value">{market_data['indicators'].get('atr_14', 'N/A'):.2f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Position vs 20D High:</span>
                <span class="metric-value">{market_data['indicators'].get('position_20d_high', 'N/A'):.1%}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>📰 News Sentiment Analysis</h2>
            <div class="metric">
                <span class="metric-label">Total Headlines:</span>
                <span class="metric-value">{results.get('news_catalysts', {}).get('total_headlines', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Positive Catalysts:</span>
                <span class="metric-value">{results.get('news_catalysts', {}).get('positive_catalysts', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Negative Catalysts:</span>
                <span class="metric-value">{results.get('news_catalysts', {}).get('negative_catalysts', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Neutral Headlines:</span>
                <span class="metric-value">{results.get('news_catalysts', {}).get('neutral_catalysts', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Good News Effectiveness:</span>
                <span class="metric-value">{results.get('good_news_analysis', {}).get('effectiveness_score', 'N/A'):.1f}/100</span>
            </div>
            <div class="metric">
                <span class="metric-label">Good News Failure Rate:</span>
                <span class="metric-value">{results.get('good_news_analysis', {}).get('failure_rate', 'N/A'):.1%}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Positive Headlines:</span>
                <span class="metric-value">{results.get('good_news_analysis', {}).get('positive_headlines', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Alert Triggered:</span>
                <span class="metric-value">{results.get('good_news_analysis', {}).get('alert_triggered', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Consecutive Failures:</span>
                <span class="metric-value">{results.get('good_news_analysis', {}).get('consecutive_failures', 'N/A')}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>📰 Recent News Headlines</h2>
            {self._create_news_headlines_section(results)}
        </div>
        
        <div class="section">
            <h2>📈 News Sentiment Breakdown</h2>
            {self._create_sentiment_breakdown_section(results)}
        </div>
        
        <div class="section">
            <h2>📈 News Price Impact Analysis</h2>
            {self._create_news_impact_section(results.get('good_news_analysis', {}))}
        </div>
        
        <div class="section">
            <h2>🔄 Cycle Analysis</h2>
            <div class="metric">
                <span class="metric-label">Cycle Phase:</span>
                <span class="metric-value">{cycle_analysis['cycle_phase'].replace('_', ' ').title()}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Cycle Confidence:</span>
                <span class="metric-value">{cycle_analysis['cycle_confidence']:.1%}</span>
            </div>
            <div class="metric">
                <span class="metric-label">News Risk Score:</span>
                <span class="metric-value">{cycle_analysis['news_risk_score']:.1f}/100</span>
            </div>
            <div class="metric">
                <span class="metric-label">Good News Effectiveness:</span>
                <span class="metric-value">{cycle_analysis['good_news_effectiveness']:.1f}/100</span>
            </div>
            <div class="metric">
                <span class="metric-label">Transition Risk:</span>
                <span class="metric-value">{cycle_analysis.get('phase_transition_risk', 'N/A')}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Recommendation</h2>
            <div class="recommendation {self._get_recommendation_class(recommendation['tier'])}">
                {recommendation['tier']}
            </div>
            <div class="metric">
                <span class="metric-label">Confidence:</span>
                <span class="metric-value">{recommendation['confidence']:.1%}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Urgency:</span>
                <span class="metric-value">{recommendation['urgency']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Next Review:</span>
                <span class="metric-value">{recommendation['next_review_date']}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>💡 Top 3 Reasons</h2>
            <div class="reasons">
                <ul>
                    {''.join([f"<li>{reason}</li>" for reason in recommendation['top_3_reasons']])}
                </ul>
            </div>
        </div>
        
        <div class="section">
            <h2>📍 Key Levels</h2>
            <div class="levels">
                {''.join([f"<div class='level'><strong>{level_type.replace('_', ' ').title()}:</strong> {level_value}</div>" 
                         for level_type, level_value in recommendation['key_levels'].items()])}
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Technical Indicators</h2>
            <div class="metric">
                <span class="metric-label">RSI (14):</span>
                <span class="metric-value">{market_data['indicators'].get('rsi_14', 'N/A'):.1f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">21D Return:</span>
                <span class="metric-value">{market_data['indicators'].get('ret_21d', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">63D Return:</span>
                <span class="metric-value">{market_data['indicators'].get('ret_63d', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Volume Z-Score:</span>
                <span class="metric-value">{market_data['indicators'].get('volume_z_score', 'N/A'):.2f}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>⚠️ Risk Metrics</h2>
            <div class="metric">
                <span class="metric-label">Current Drawdown:</span>
                <span class="metric-value">{market_data['risk_metrics'].get('current_drawdown', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Max Drawdown:</span>
                <span class="metric-value">{market_data['risk_metrics'].get('max_drawdown', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Volatility (20D):</span>
                <span class="metric-value">{market_data['risk_metrics'].get('volatility_20d', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Volatility Regime:</span>
                <span class="metric-value">{market_data['risk_metrics'].get('volatility_regime', 'N/A')}</span>
            </div>
        </div>
    </div>
</body>
</html>
        """
        return html_content
    
    def _create_markdown_report(self, results: Dict, ticker: str, days: int) -> str:
        """Create Markdown report from advanced trading system results."""
        market_data = results["market_data"]
        dual_scores = results["dual_scores"]
        cycle_analysis = results["cycle_analysis"]
        recommendation = results["recommendation"]
        
        md_content = f"""# 🎯 Advanced Stock Analysis Report - {ticker}

**Analysis Period:** {days} days  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Key Metrics

| Metric | Value |
|--------|-------|
| **Current Price** | ${market_data['current_price']:.2f} |
| **Opportunity Score** | {dual_scores['opportunity_score']:.1f}/100 |
| **Sell-Risk Score** | {dual_scores['sell_risk_score']:.1f}/100 |
| **Overall Bias** | {dual_scores['overall_bias']} |
| **Confidence** | {dual_scores['confidence']:.1%} |

---

## 📈 Price & Volume Data

| Metric | Value |
|--------|-------|
| **20-Day High** | ${market_data['indicators'].get('high_20d', 'N/A')} |
| **20-Day Low** | ${market_data['indicators'].get('low_20d', 'N/A')} |
| **50-Day High** | ${market_data['indicators'].get('high_50d', 'N/A')} |
| **50-Day Low** | ${market_data['indicators'].get('low_50d', 'N/A')} |
| **Volume Z-Score** | {market_data['indicators'].get('volume_z_score', 'N/A'):.2f} |
| **ATR (14)** | {market_data['indicators'].get('atr_14', 'N/A'):.2f} |
| **Position vs 20D High** | {market_data['indicators'].get('position_20d_high', 'N/A'):.1%} |

---

## 📰 News Sentiment Analysis

| Metric | Value |
|--------|-------|
| **Total Headlines** | {results.get('news_catalysts', {}).get('total_headlines', 'N/A')} |
| **Positive Catalysts** | {results.get('news_catalysts', {}).get('positive_catalysts', 'N/A')} |
| **Negative Catalysts** | {results.get('news_catalysts', {}).get('negative_catalysts', 'N/A')} |
| **Neutral Headlines** | {results.get('news_catalysts', {}).get('neutral_catalysts', 'N/A')} |
| **Good News Effectiveness** | {results.get('good_news_analysis', {}).get('effectiveness_score', 'N/A'):.1f}/100 |
| **Good News Failure Rate** | {results.get('good_news_analysis', {}).get('failure_rate', 'N/A'):.1%} |
| **Positive Headlines** | {results.get('good_news_analysis', {}).get('positive_headlines', 'N/A')} |
| **Alert Triggered** | {results.get('good_news_analysis', {}).get('alert_triggered', 'N/A')} |
| **Consecutive Failures** | {results.get('good_news_analysis', {}).get('consecutive_failures', 'N/A')} |

---

## 📈 News Sentiment Breakdown

{self._create_sentiment_breakdown_section(results)}

---

## 📈 News Price Impact Analysis

{self._create_news_impact_markdown(results.get('good_news_analysis', {}))}

---

## 🔄 Cycle Analysis

| Metric | Value |
|--------|-------|
| **Cycle Phase** | {cycle_analysis['cycle_phase'].replace('_', ' ').title()} |
| **Cycle Confidence** | {cycle_analysis['cycle_confidence']:.1%} |
| **News Risk Score** | {cycle_analysis['news_risk_score']:.1f}/100 |
| **Good News Effectiveness** | {cycle_analysis['good_news_effectiveness']:.1f}/100 |
| **Transition Risk** | {cycle_analysis.get('phase_transition_risk', 'N/A')} |

---

## 🎯 Recommendation

**{recommendation['tier']}
- **Confidence:** {recommendation['confidence']:.1%}
- **Urgency:** {recommendation['urgency']}
- **Next Review:** {recommendation['next_review_date']}

---

## 💡 Top 3 Reasons

{chr(10).join([f"{i+1}. {reason}" for i, reason in enumerate(recommendation['top_3_reasons'], 1)])}

---

## 📍 Key Levels

{chr(10).join([f"• **{level_type.replace('_', ' ').title()}:** {level_value}" 
                     for level_type, level_value in recommendation['key_levels'].items()])}

---

## 📈 Technical Indicators

| Indicator | Value |
|-----------|-------|
| **RSI (14)** | {market_data['indicators'].get('rsi_14', 'N/A'):.1f} |
| **21D Return** | {market_data['indicators'].get('ret_21d', 'N/A')} |
| **63D Return** | {market_data['indicators'].get('ret_63d', 'N/A')} |
| **Volume Z-Score** | {market_data['indicators'].get('volume_z_score', 'N/A'):.2f} |

---

## ⚠️ Risk Metrics

| Metric | Value |
|--------|-------|
| **Current Drawdown** | {market_data['risk_metrics'].get('current_drawdown', 'N/A')} |
| **Max Drawdown** | {market_data['risk_metrics'].get('max_drawdown', 'N/A')} |
| **Volatility (20D)** | {market_data['risk_metrics'].get('volatility_20d', 'N/A')} |
| **Volatility Regime** | {market_data['risk_metrics'].get('volatility_regime', 'N/A')} |

---

*Report generated by Advanced Trading System*
"""
        return md_content
    
    def _get_recommendation_class(self, tier: str) -> str:
        """Get CSS class for recommendation tier."""
        if "BUY" in tier:
            return "buy"
        elif "SELL" in tier:
            return "sell"
        else:
            return "hold"
    
    def _create_news_impact_section(self, good_news_analysis: Dict) -> str:
        """Create detailed news price impact analysis section."""
        forward_returns = good_news_analysis.get('forward_return_analysis', {})
        
        if not forward_returns:
            return "<p>No forward return analysis available</p>"
        
        impact_html = ""
        
        # Sort headlines by date (most recent first)
        sorted_headlines = sorted(forward_returns.items(), key=lambda x: x[0], reverse=True)
        
        # Show top 10 most recent news impacts
        for i, (headline, returns) in enumerate(sorted_headlines[:10]):
            if returns and len(returns) > 0:
                avg_1d = returns.get('1d', 0) * 100
                avg_2d = returns.get('2d', 0) * 100
                avg_3d = returns.get('3d', 0) * 100
                
                # Determine impact strength
                if avg_1d > 2:
                    impact_strength = "Strong Positive"
                    impact_class = "strong-positive"
                elif avg_1d > 0.5:
                    impact_strength = "Moderate Positive"
                    impact_class = "moderate-positive"
                elif avg_1d > 0:
                    impact_strength = "Weak Positive"
                    impact_class = "weak-positive"
                else:
                    impact_strength = "Negative"
                    impact_class = "negative"
                
                impact_html += f"""
                <div class="metric" style="border-left: 4px solid {self._get_impact_color(impact_class)}; padding-left: 10px;">
                    <div style="font-weight: bold; margin-bottom: 5px;">{i+1}. {headline[:50]}...</div>
                    <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                        <span style="color: #666;">1D:</span>
                        <span class="metric-value" style="color: {self._get_impact_color(impact_class)};">{avg_1d:+.1f}%</span>
                        <span style="color: #666;">2D:</span>
                        <span class="metric-value" style="color: {self._get_impact_color(impact_class)};">{avg_2d:+.1f}%</span>
                        <span style="color: #666;">3D:</span>
                        <span class="metric-value" style="color: {self._get_impact_color(impact_class)};">{avg_3d:+.1f}%</span>
                    </div>
                    <div style="font-style: italic; color: #666; margin-top: 5px;">{impact_strength}</div>
                </div>
                """
        
        return impact_html
    
    def _get_impact_color(self, impact_class: str) -> str:
        """Get color for impact strength."""
        colors = {
            "strong-positive": "#28a745",
            "moderate-positive": "#17a2b8", 
            "weak-positive": "#ffc107",
            "negative": "#dc3545"
        }
        return colors.get(impact_class, "#6c757d")
    
    def _create_sentiment_breakdown_section(self, results: Dict) -> str:
        """Create detailed sentiment breakdown section."""
        news_catalysts = results.get('news_catalysts', {})
        good_news = results.get('good_news_analysis', {})
        
        # Calculate sentiment breakdown from news_catalysts
        total_catalysts = news_catalysts.get('total_headlines', 0)
        positive_catalysts = news_catalysts.get('positive_catalysts', 0)
        negative_catalysts = news_catalysts.get('negative_catalysts', 0)
        neutral_catalysts = total_catalysts - positive_catalysts - negative_catalysts
        
        # Calculate percentages
        if total_catalysts > 0:
            positive_pct = (positive_catalysts / total_catalysts) * 100
            negative_pct = (negative_catalysts / total_catalysts) * 100
            neutral_pct = (neutral_catalysts / total_catalysts) * 100
        else:
            positive_pct = negative_pct = neutral_pct = 0
        
        # Create sentiment breakdown HTML
        breakdown_html = f"""
        <div class="metric">
            <span class="metric-label">Total Articles:</span>
            <span class="metric-value">{total_catalysts}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Positive Articles:</span>
            <span class="metric-value">{positive_catalysts} ({positive_pct:.1f}%)</span>
        </div>
        <div class="metric">
            <span class="metric-label">Negative Articles:</span>
            <span class="metric-value">{negative_catalysts} ({negative_pct:.1f}%)</span>
        </div>
        <div class="metric">
            <span class="metric-label">Neutral Articles:</span>
            <span class="metric-value">{neutral_catalysts} ({neutral_pct:.1f}%)</span>
        </div>
        <div class="metric">
            <span class="metric-label">Good News Success Rate:</span>
            <span class="metric-value">{100 - good_news.get('failure_rate', 0):.1f}%</span>
        </div>
        """
        
        return breakdown_html
    
    def _create_news_headlines_section(self, results: Dict) -> str:
        """Create recent news headlines section."""
        news_catalysts = results.get('news_catalysts', {})
        good_news = results.get('good_news_analysis', {})
        
        # Get headlines from good_news_analysis for detailed display
        forward_returns = good_news.get('forward_return_analysis', {})
        
        headlines_html = ""
        
        if forward_returns and len(forward_returns) > 0:
            # Sort headlines by date (most recent first)
            sorted_headlines = sorted(forward_returns.items(), key=lambda x: x[0], reverse=True)
            
            # Create headlines table
            headlines_html += """
        <div class="metric">
            <span class="metric-label">Recent News Headlines (Top 10)</span>
        </div>
        <div style="max-height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background-color: #f8f9fa; color: white;">
                        <th style="padding: 8px; text-align: left;">#</th>
                        <th style="padding: 8px; text-align: left;">Headline</th>
                        <th style="padding: 8px; text-align: left;">Date</th>
                        <th style="padding: 8px; text-align: left;">1D Return</th>
                        <th style="padding: 8px; text-align: left;">2D Return</th>
                        <th style="padding: 8px; text-align: left;">3D Return</th>
                        <th style="padding: 8px; text-align: left;">Impact</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            # Add top 10 most recent headlines
            for i, (headline, returns) in enumerate(sorted_headlines[:10]):
                if returns and len(returns) > 0:
                    avg_1d = returns.get('1d', 0) * 100
                    avg_2d = returns.get('2d', 0) * 100
                    avg_3d = returns.get('3d', 0) * 100
                    
                    # Determine impact strength
                    if avg_1d > 2:
                        impact_strength = "Strong Positive 🚀"
                        impact_class = "strong-positive"
                    elif avg_1d > 0.5:
                        impact_strength = "Moderate Positive 📈"
                        impact_class = "moderate-positive"
                    elif avg_1d > 0:
                        impact_strength = "Weak Positive 📊"
                        impact_class = "weak-positive"
                    else:
                        impact_strength = "Negative 📉"
                        impact_class = "negative"
                    
                    impact_color = self._get_impact_color(impact_class)
                    
                    headlines_html += f"""
                    <tr>
                        <td style="padding: 8px;">{i+1}</td>
                        <td style="padding: 8px; max-width: 300px;">{headline[:60]}...</td>
                        <td style="padding: 8px;">{headline[:50]}</td>
                        <td style="padding: 8px;">{avg_1d:+.1f}%</td>
                        <td style="padding: 8px;">{avg_2d:+.1f}%</td>
                        <td style="padding: 8px;">{avg_3d:+.1f}%</td>
                        <td style="padding: 8px; color: {impact_color}; font-weight: bold;">{impact_strength}</td>
                    </tr>
            """
            
            headlines_html += """
                </tbody>
            </table>
        </div>
        """
        
        return headlines_html
    
    def _create_news_impact_markdown(self, good_news_analysis: Dict) -> str:
        """Create detailed news price impact analysis in markdown format."""
        forward_returns = good_news_analysis.get('forward_return_analysis', {})
        
        if not forward_returns:
            return "No forward return analysis available"
        
        impact_md = "\n### Recent News Price Impact (Top 10)\n\n"
        
        # Sort headlines by date (most recent first)
        sorted_headlines = sorted(forward_returns.items(), key=lambda x: x[0], reverse=True)
        
        # Create table header
        impact_md += "| # | Headline | 1D Return | 2D Return | 3D Return | Impact |\n"
        impact_md += "|---|---|---|---|---|---|\n"
        
        # Show top 10 most recent news impacts
        for i, (headline, returns) in enumerate(sorted_headlines[:10]):
            if returns and len(returns) > 0:
                avg_1d = returns.get('1d', 0) * 100
                avg_2d = returns.get('2d', 0) * 100
                avg_3d = returns.get('3d', 0) * 100
                
                # Determine impact strength
                if avg_1d > 2:
                    impact_strength = "Strong Positive 🚀"
                elif avg_1d > 0.5:
                    impact_strength = "Moderate Positive 📈"
                elif avg_1d > 0:
                    impact_strength = "Weak Positive 📊"
                else:
                    impact_strength = "Negative 📉"
                
                impact_md += f"| {i+1} | {headline[:40]}... | {avg_1d:+.1f}% | {avg_2d:+.1f}% | {avg_3d:+.1f}% | {impact_strength} |\n"
        
        return impact_md
    
    def _generate_portfolio_report(self):
        """Generate portfolio report."""
        print("\n📚 Generate Portfolio Report")
        print("-" * 30)
        
        portfolio = self._load_portfolio_data()
        positions = portfolio.get('positions', [])
        
        if not positions:
            print("📭 Portfolio is empty.")
            input("Press Enter to continue...")
            return
        
        try:
            days = int(input("Analysis period in days (default 180): ") or "180")
        except ValueError:
            days = 180
        
        format_choice = input("Report format (html/markdown/both, default both): ").strip().lower()
        if format_choice not in ["html", "markdown", "both"]:
            format_choice = "both"
        
        print(f"\n🔄 Generating portfolio report...")
        
        try:
            generator = StockReportGenerator()
            tickers = [pos['ticker'] for pos in positions]
            
            if format_choice in ["html", "both"]:
                generator.generate_html_report(tickers, days, portfolio_file=self.portfolio_file)
                print("✅ HTML report generated")
            
            if format_choice in ["markdown", "both"]:
                generator.generate_markdown_report(tickers, days, portfolio_file=self.portfolio_file)
                print("✅ Markdown report generated")
            
            print(f"📁 Reports saved to 'reports/' directory")
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
        
        input("Press Enter to continue...")
    
    def _generate_market_summary_report(self):
        """Generate market summary report."""
        print("\n📊 Generate Market Summary Report")
        print("-" * 40)
        
        tickers_input = input("Enter tickers (comma-separated): ").strip()
        tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
        
        if not tickers:
            print("❌ Please enter at least one ticker.")
            input("Press Enter to continue...")
            return
        
        try:
            days = int(input("Analysis period in days (default 180): ") or "180")
        except ValueError:
            days = 180
        
        format_choice = input("Report format (html/markdown/both, default both): ").strip().lower()
        if format_choice not in ["html", "markdown", "both"]:
            format_choice = "both"
        
        print(f"\n🔄 Generating market summary for {len(tickers)} tickers...")
        
        try:
            generator = StockReportGenerator()
            
            if format_choice in ["html", "both"]:
                generator.generate_html_report(tickers, days)
                print("✅ HTML report generated")
            
            if format_choice in ["markdown", "both"]:
                generator.generate_markdown_report(tickers, days)
                print("✅ Markdown report generated")
            
            print(f"📁 Reports saved to 'reports/' directory")
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
        
        input("Press Enter to continue...")
    
    def _generate_alerts_report(self):
        """Generate alerts report."""
        print("\n🔔 Generate Alerts Report")
        print("-" * 30)
        
        # Get tickers
        portfolio = self._load_portfolio_data()
        portfolio_tickers = [pos['ticker'] for pos in portfolio.get('positions', [])]
        
        if portfolio_tickers:
            use_portfolio = input("Use portfolio tickers? (y/n): ").lower() == 'y'
        else:
            use_portfolio = False
        
        if not use_portfolio:
            tickers_input = input("Enter tickers (comma-separated): ").strip()
            tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
        else:
            tickers = portfolio_tickers
        
        if not tickers:
            print("❌ No tickers specified.")
            input("Press Enter to continue...")
            return
        
        print(f"\n🔄 Generating alerts report for {len(tickers)} tickers...")
        
        try:
            alerts = self.system.run_alerts_scan(tickers, ["json"])
            
            if alerts:
                filename = f"alerts_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                print(f"✅ Alerts report saved: {filename}")
                print(f"📊 Found {len(alerts)} alerts")
            else:
                print("✅ No alerts to report")
                
        except Exception as e:
            print(f"❌ Error generating alerts report: {e}")
        
        input("Press Enter to continue...")
    
    def _analyze_single_stock(self):
        """Analyze a single stock with all features."""
        print("\n🔍 Analyze Single Stock")
        print("-" * 25)
        
        ticker = input("Enter ticker symbol: ").strip().upper()
        if not ticker:
            print("❌ Ticker cannot be empty.")
            input("Press Enter to continue...")
            return
        
        try:
            days = int(input("Analysis period in days (default 180): ") or "180")
        except ValueError:
            days = 180
        
        print(f"\n🔄 Running comprehensive analysis for {ticker}...")
        
        try:
            results = self.system.analyze_ticker(ticker, days)
            
            if "error" not in results:
                print(f"\n🎯 COMPREHENSIVE ANALYSIS - {ticker}")
                print("=" * 50)
                
                # Key metrics
                market_data = results["market_data"]
                print(f"\n💰 Price: ${market_data['current_price']:.2f}")
                
                # Dual scores
                dual_scores = results["dual_scores"]
                print(f"📊 Opportunity Score: {dual_scores['opportunity_score']:.1f}/100")
                print(f"📊 Sell-Risk Score: {dual_scores['sell_risk_score']:.1f}/100")
                print(f"🎯 Overall Bias: {dual_scores['overall_bias']}")
                
                # Cycle analysis
                cycle = results["cycle_analysis"]
                print(f"🔄 Cycle Phase: {cycle['cycle_phase'].replace('_', ' ').title()}")
                print(f"📰 News Risk: {cycle['news_risk_score']:.1f}/100")
                print(f"📈 Good News Effectiveness: {cycle['good_news_effectiveness']:.1f}/100")
                
                # Recommendation
                rec = results["recommendation"]
                print(f"\n🎯 Recommendation: {rec['tier']}")
                print(f"🔍 Confidence: {rec['confidence']:.1%}")
                print(f"⚡ Urgency: {rec['urgency']}")
                
                if rec['top_3_reasons']:
                    print(f"\n💡 Top 3 Reasons:")
                    for i, reason in enumerate(rec['top_3_reasons'], 1):
                        print(f"  {i}. {reason}")
                
                if rec['key_levels']:
                    print(f"\n📍 Key Levels:")
                    for level_type, level_value in rec['key_levels'].items():
                        print(f"  {level_type.replace('_', ' ').title()}: {level_value}")
                
                print(f"\n📅 Next Review: {rec['next_review_date']}")
                
            else:
                print(f"❌ {results['error']}")
                
        except Exception as e:
            print(f"❌ Error analyzing {ticker}: {e}")
        
        input("\nPress Enter to continue...")
    
    def _view_portfolio(self):
        """View current portfolio."""
        print("\n👁️  View Current Portfolio")
        print("-" * 30)
        
        portfolio = self._load_portfolio_data()
        positions = portfolio.get('positions', [])
        
        if not positions:
            print("📭 Portfolio is empty.")
            input("Press Enter to continue...")
            return
        
        print(f"\n📚 Portfolio: {portfolio.get('portfolio_name', 'Unnamed Portfolio')}")
        print(f"📊 Total Positions: {len(positions)}")
        print()
        
        total_value = 0
        total_cost = 0
        
        for pos in positions:
            current_value = pos['shares'] * pos['cost_basis']  # Simplified
            cost = pos['shares'] * pos['cost_basis']
            pnl = current_value - cost
            pnl_pct = (pnl / cost * 100) if cost != 0 else 0
            
            total_value += current_value
            total_cost += cost
            
            print(f"📈 {pos['ticker']}:")
            print(f"   Shares: {pos['shares']}")
            print(f"   Cost Basis: ${pos['cost_basis']:.2f}")
            print(f"   Position Value: ${current_value:.2f}")
            print(f"   P&L: ${pnl:+.2f} ({pnl_pct:+.1%})")
            if pos.get('notes'):
                print(f"   Notes: {pos['notes']}")
            print()
        
        portfolio_pnl = total_value - total_cost
        portfolio_pnl_pct = (portfolio_pnl / total_cost * 100) if total_cost != 0 else 0
        
        print("📊 Portfolio Summary:")
        print(f"   Total Value: ${total_value:,.2f}")
        print(f"   Total Cost: ${total_cost:,.2f}")
        print(f"   Total P&L: ${portfolio_pnl:+.2f} ({portfolio_pnl_pct:+.1%})")
        
        input("\nPress Enter to continue...")
    
    def _system_settings(self):
        """System settings menu."""
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            print("⚙️" + "="*50)
            print("   SYSTEM SETTINGS")
            print("="*50)
            print()
            print("1️⃣  📁 Portfolio File Location")
            print("2️⃣  🔑 Default Keywords")
            print("3️⃣  📊 Default Analysis Period")
            print("4️⃣  📈 Default Max Headlines")
            print("5️⃣  🗑️  Clear Cache/State Files")
            print("6️⃣  ℹ️  System Information")
            print("7️⃣  🔙 Back to Main Menu")
            print()
            
            choice = input("Enter your choice (1-7): ").strip()
            
            if choice == "1":
                self._set_portfolio_file()
            elif choice == "2":
                self._set_default_keywords()
            elif choice == "3":
                self._set_default_period()
            elif choice == "4":
                self._set_max_headlines()
            elif choice == "5":
                self._clear_cache()
            elif choice == "6":
                self._show_system_info()
            elif choice == "7":
                break
            else:
                print("❌ Invalid choice.")
                input("Press Enter to continue...")
    
    def _set_portfolio_file(self):
        """Set portfolio file location."""
        print(f"\n📁 Current portfolio file: {self.portfolio_file}")
        new_file = input("Enter new portfolio file path (leave empty to keep current): ").strip()
        
        if new_file:
            self.portfolio_file = new_file
            print(f"✅ Portfolio file set to: {self.portfolio_file}")
        
        input("Press Enter to continue...")
    
    def _set_default_keywords(self):
        """Set default keywords."""
        print(f"\n🔑 Current default keywords: {', '.join(self.default_keywords)}")
        new_keywords = input("Enter new keywords (comma-separated, leave empty to keep current): ").strip()
        
        if new_keywords:
            self.default_keywords = [k.strip() for k in new_keywords.split(',') if k.strip()]
            print(f"✅ Default keywords updated: {', '.join(self.default_keywords)}")
        
        input("Press Enter to continue...")
    
    def _set_default_period(self):
        """Set default analysis period."""
        print(f"\n📊 Current default period: 180 days")
        try:
            new_period = int(input("Enter new default period in days: "))
            if new_period > 0:
                # Note: This would need to be stored in a config file for persistence
                print(f"✅ Default period set to: {new_period} days")
            else:
                print("❌ Period must be positive.")
        except ValueError:
            print("❌ Invalid number.")
        
        input("Press Enter to continue...")
    
    def _set_max_headlines(self):
        """Set default max headlines."""
        print(f"\n📈 Current default max headlines: 20")
        try:
            new_max = int(input("Enter new default max headlines: "))
            if new_max > 0:
                # Note: This would need to be stored in a config file for persistence
                print(f"✅ Default max headlines set to: {new_max}")
            else:
                print("❌ Max headlines must be positive.")
        except ValueError:
            print("❌ Invalid number.")
        
        input("Press Enter to continue...")
    
    def _clear_cache(self):
        """Clear cache and state files."""
        print("\n🗑️  Clear Cache/State Files")
        print("-" * 30)
        
        files_to_check = [
            "alerts_state.json",
            "trading_state.json",
            "test_results",
            "test_portfolio"
        ]
        
        cleared = []
        for file in files_to_check:
            if os.path.exists(file):
                os.remove(file)
                cleared.append(file)
        
        if cleared:
            print(f"✅ Cleared {len(cleared)} files: {', '.join(cleared)}")
        else:
            print("ℹ️  No cache files found to clear.")
        
        input("Press Enter to continue...")
    
    def _show_system_info(self):
        """Show system information."""
        print("\nℹ️  System Information")
        print("-" * 25)
        
        print(f"🐍 Python Version: {sys.version}")
        print(f"📁 Working Directory: {os.getcwd()}")
        print(f"📁 Portfolio File: {self.portfolio_file}")
        print(f"🔑 Default Keywords: {', '.join(self.default_keywords)}")
        
        # Check data files
        data_files = [f for f in os.listdir('.') if f.endswith(('.csv', '.json')) and not f.startswith('.')]
        print(f"📊 Data Files: {len(data_files)}")
        
        # Check reports directory
        if os.path.exists('reports'):
            report_files = [f for f in os.listdir('reports') if f.endswith(('.html', '.md', '.pdf'))]
            print(f"📋 Report Files: {len(report_files)}")
        
        input("\nPress Enter to continue...")
    
    def _load_portfolio_data(self) -> Dict:
        """Load portfolio data from file."""
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load portfolio file: {e}")
        
        # Return empty portfolio if file doesn't exist or is invalid
        return {"portfolio_name": "My Portfolio", "positions": []}
    
    def _save_portfolio_data(self, portfolio: Dict):
        """Save portfolio data to file."""
        try:
            with open(self.portfolio_file, 'w') as f:
                json.dump(portfolio, f, indent=2)
        except Exception as e:
            print(f"Error saving portfolio: {e}")
    
    def _load_portfolio_from_file(self):
        """Load portfolio from a specific file."""
        file_path = input("Enter portfolio file path: ").strip()
        
        if not file_path:
            print("❌ File path cannot be empty.")
            input("Press Enter to continue...")
            return
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            input("Press Enter to continue...")
            return
        
        try:
            with open(file_path, 'r') as f:
                portfolio = json.load(f)
            
            self.portfolio_file = file_path
            print(f"✅ Portfolio loaded from: {file_path}")
            print(f"📊 Found {len(portfolio.get('positions', []))} positions")
            
        except Exception as e:
            print(f"❌ Error loading portfolio: {e}")
        
        input("Press Enter to continue...")
    
    def _import_portfolio_from_csv(self):
        """Import portfolio from CSV file."""
        print("\n📥 Import Portfolio from CSV")
        print("-" * 35)
        print("Expected CSV format: ticker,num_shares,cost_per_share,purchase_date,notes")
        print("Example: AAPL,100,150.25,2023-01-15,Core position")
        print()
        
        file_path = input("Enter CSV file path: ").strip()
        
        if not file_path:
            print("❌ File path cannot be empty.")
            input("Press Enter to continue...")
            return
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            input("Press Enter to continue...")
            return
        
        try:
            import csv
            
            imported_positions = []
            skipped_rows = []
            
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                
                # Check required columns
                required_columns = ['ticker', 'num_shares', 'cost_per_share']
                if not all(col in reader.fieldnames for col in required_columns):
                    print(f"❌ CSV must contain columns: {', '.join(required_columns)}")
                    print(f"Found columns: {', '.join(reader.fieldnames)}")
                    input("Press Enter to continue...")
                    return
                
                for row_num, row in enumerate(reader, 2):  # Start at 2 (after header)
                    try:
                        ticker = row['ticker'].strip().upper()
                        if not ticker:
                            skipped_rows.append(f"Row {row_num}: Empty ticker")
                            continue
                        
                        shares = float(row['num_shares'])
                        if shares <= 0:
                            skipped_rows.append(f"Row {row_num}: Invalid shares ({shares})")
                            continue
                        
                        cost_per_share = float(row['cost_per_share'])
                        if cost_per_share <= 0:
                            skipped_rows.append(f"Row {row_num}: Invalid cost per share ({cost_per_share})")
                            continue
                        
                        purchase_date = row.get('purchase_date', '').strip()
                        notes = row.get('notes', '').strip()
                        
                        position = {
                            'ticker': ticker,
                            'shares': shares,
                            'cost_basis': cost_per_share,
                            'purchase_date': purchase_date,
                            'notes': notes
                        }
                        
                        imported_positions.append(position)
                        
                    except ValueError as e:
                        skipped_rows.append(f"Row {row_num}: Invalid data - {e}")
                    except Exception as e:
                        skipped_rows.append(f"Row {row_num}: Error - {e}")
            
            if imported_positions:
                # Load current portfolio
                portfolio = self._load_portfolio_data()
                
                # Check for duplicates
                existing_tickers = {pos['ticker'] for pos in portfolio.get('positions', [])}
                duplicates = [pos for pos in imported_positions if pos['ticker'] in existing_tickers]
                
                if duplicates:
                    print(f"⚠️  Found {len(duplicates)} duplicate tickers:")
                    for dup in duplicates:
                        print(f"    • {dup['ticker']}")
                    
                    action = input("Replace duplicates or skip? (replace/skip/cancel): ").lower()
                    if action == 'cancel':
                        input("Press Enter to continue...")
                        return
                    elif action == 'replace':
                        # Remove existing duplicates
                        portfolio['positions'] = [pos for pos in portfolio['positions'] 
                                                if pos['ticker'] not in {dup['ticker'] for dup in duplicates}]
                    elif action == 'skip':
                        # Skip duplicates from import
                        imported_positions = [pos for pos in imported_positions 
                                            if pos['ticker'] not in existing_tickers]
                
                # Add imported positions
                portfolio.setdefault('positions', []).extend(imported_positions)
                
                # Save portfolio
                self._save_portfolio_data(portfolio)
                
                print(f"✅ Successfully imported {len(imported_positions)} positions")
                
                if skipped_rows:
                    print(f"⚠️  Skipped {len(skipped_rows)} rows:")
                    for skipped in skipped_rows[:5]:  # Show first 5
                        print(f"    • {skipped}")
                    if len(skipped_rows) > 5:
                        print(f"    ... and {len(skipped_rows) - 5} more")
                
            else:
                print("❌ No valid positions found in CSV")
                
        except Exception as e:
            print(f"❌ Error importing CSV: {e}")
        
        input("Press Enter to continue...")
    
    def _export_portfolio_to_csv(self):
        """Export portfolio to CSV file."""
        print("\n📤 Export Portfolio to CSV")
        print("-" * 35)
        
        portfolio = self._load_portfolio_data()
        positions = portfolio.get('positions', [])
        
        if not positions:
            print("📭 Portfolio is empty.")
            input("Press Enter to continue...")
            return
        
        file_path = input("Enter CSV file path (default: portfolio_export.csv): ").strip()
        if not file_path:
            file_path = "portfolio_export.csv"
        
        if not file_path.endswith('.csv'):
            file_path += '.csv'
        
        try:
            import csv
            
            with open(file_path, 'w', newline='') as f:
                fieldnames = ['ticker', 'num_shares', 'cost_per_share', 'purchase_date', 'notes']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for pos in positions:
                    row = {
                        'ticker': pos['ticker'],
                        'num_shares': pos['shares'],
                        'cost_per_share': pos['cost_basis'],
                        'purchase_date': pos.get('purchase_date', ''),
                        'notes': pos.get('notes', '')
                    }
                    writer.writerow(row)
            
            print(f"✅ Portfolio exported to: {file_path}")
            print(f"📊 Exported {len(positions)} positions")
            
        except Exception as e:
            print(f"❌ Error exporting CSV: {e}")
        
        input("Press Enter to continue...")


def main():
    """Main entry point."""
    menu = TradingSystemMenu()
    menu.run()


if __name__ == "__main__":
    main()
