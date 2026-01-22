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
from portfolio_manager import PortfolioManager, PortfolioPosition
from settings_manager import SettingsManager


class TradingSystemMenu:
    """Interactive menu system for the advanced trading system."""
    
    def __init__(self):
        self.system = AdvancedTradingSystem()
        self.settings = SettingsManager()
        self.portfolio_file = self.settings.portfolio_file
        self.default_keywords = self.settings.default_keywords

    def _get_portfolio_manager(self) -> PortfolioManager:
        return PortfolioManager(self.portfolio_file)
        
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

    def _generate_advanced_report(self, results: Dict, ticker: str, days: int, format_choice: str = "both"):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if format_choice not in ["html", "markdown", "both"]:
            format_choice = "both"

        os.makedirs("reports", exist_ok=True)

        if format_choice in ["html", "both"]:
            html_content = self._create_html_report(results, ticker, days)
            html_path = f"reports/{ticker}_report_{timestamp}.html"
            with open(html_path, 'w') as f:
                f.write(html_content)
            print(f"✅ HTML report saved: {html_path}")

        if format_choice in ["markdown", "both"]:
            md_content = self._create_markdown_report(results, ticker, days)
            md_path = f"reports/{ticker}_report_{timestamp}.md"
            with open(md_path, 'w') as f:
                f.write(md_content)
            print(f"✅ Markdown report saved: {md_path}")

        print(f"📁 Reports saved to 'reports/' directory")

    def _create_html_report(self, results: Dict, ticker: str, days: int) -> str:
        generator = StockReportGenerator()
        return generator.generate_advanced_single_html(results, ticker, days)

    def _create_markdown_report(self, results: Dict, ticker: str, days: int) -> str:
        generator = StockReportGenerator()
        return generator.generate_advanced_single_markdown(results, ticker, days)

    def _create_news_impact_section(self, good_news_analysis) -> str:
        generator = StockReportGenerator()
        return generator._advanced_news_impact_section(good_news_analysis)

    def _create_news_impact_markdown(self, good_news_analysis) -> str:
        generator = StockReportGenerator()
        return generator._advanced_news_impact_markdown(good_news_analysis)

    def _create_news_headlines_section(self, results: Dict) -> str:
        generator = StockReportGenerator()
        return generator._advanced_news_headlines_section(results.get('good_news_analysis', {}))

    def _create_sentiment_breakdown_section(self, results: Dict) -> str:
        generator = StockReportGenerator()
        return generator._advanced_sentiment_breakdown_section(
            results.get('news_catalysts_data', {}),
            results.get('good_news_analysis', {}),
        )

    def _get_impact_color(self, impact_class: str) -> str:
        generator = StockReportGenerator()
        return generator._advanced_impact_color(impact_class)

    def _get_recommendation_class(self, tier: str) -> str:
        generator = StockReportGenerator()
        return generator._advanced_recommendation_class(tier)
    
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

    def _save_portfolio_to_file(self):
        """Save portfolio to a specific file."""
        print("\n💾 Save Portfolio to File")
        print("-" * 30)

        portfolio = self._load_portfolio_data()
        file_path = input("Enter destination file path (leave empty to use current): ").strip()

        if not file_path:
            try:
                self._save_portfolio_data(portfolio)
                print(f"✅ Portfolio saved to: {self.portfolio_file}")
            except Exception as e:
                print(f"❌ Error saving portfolio: {e}")
            input("Press Enter to continue...")
            return

        try:
            manager = PortfolioManager(file_path)
            manager.save(portfolio)
            self.portfolio_file = file_path
            self.settings.set("portfolio_file", file_path)
            self.settings.save()
            print(f"✅ Portfolio saved to: {file_path}")
        except Exception as e:
            print(f"❌ Error saving portfolio: {e}")

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

            existing_positions = [p for p in portfolio.get('positions', []) if p.get('ticker') == ticker]
            manager = self._get_portfolio_manager()

            if existing_positions:
                print(f"⚠️  {ticker} already exists in portfolio.")
                action = input("Update existing position? (y/n): ").lower()
                if action != 'y':
                    input("Press Enter to continue...")
                    return

                portfolio, _ = manager.edit_position(
                    portfolio,
                    ticker=ticker,
                    shares=shares,
                    cost_basis=cost_basis,
                    notes=notes,
                )
                self._save_portfolio_data(portfolio)
                print(f"✅ {ticker} updated successfully!")
            else:
                portfolio, status = manager.add_position(
                    portfolio,
                    PortfolioPosition(ticker=ticker, shares=shares, cost_basis=cost_basis, notes=notes),
                )
                if status != "ok":
                    print(f"⚠️  {status}")
                self._save_portfolio_data(portfolio)
                print(f"✅ {ticker} added successfully!")
            
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
                removed = positions[choice - 1]
                manager = self._get_portfolio_manager()
                portfolio, did_remove = manager.remove_position(portfolio, removed.get('ticker', ''))
                if did_remove:
                    self._save_portfolio_data(portfolio)
                    print(f"✅ {removed['ticker']} removed from portfolio!")
                else:
                    print("❌ Could not remove position.")
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

                manager = self._get_portfolio_manager()
                portfolio, updated = manager.edit_position(
                    portfolio,
                    ticker=pos.get('ticker', ''),
                    shares=float(new_shares) if new_shares else None,
                    cost_basis=float(new_cost) if new_cost else None,
                    notes=new_notes if new_notes else None,
                )
                if updated:
                    self._save_portfolio_data(portfolio)
                    print(f"✅ {pos['ticker']} updated successfully!")
                else:
                    print("❌ Could not update position.")
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
            max_headlines = int(input(f"Max headlines per ticker (default {self.settings.default_max_headlines}): ") or str(self.settings.default_max_headlines))
        except ValueError:
            max_headlines = self.settings.default_max_headlines
        
        # Get analysis period
        try:
            days = int(input(f"Analysis period in days (default {self.settings.default_days}): ") or str(self.settings.default_days))
        except ValueError:
            days = self.settings.default_days
        
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
            days = int(input(f"Analysis period in days (default {self.settings.default_days}): ") or str(self.settings.default_days))
        except ValueError:
            days = self.settings.default_days
        
        print(f"\n🔄 Running dual scoring analysis for {len(tickers)} tickers...")
        
        for ticker in tickers:
            try:
                print(f"\n📊 {ticker} Dual Scoring:")
                results = self.system.analyze_ticker(ticker, days)
                
                if "error" not in results:
                    dual_scores = results["dual_scores"]
                    print(f"  Opportunity Score: {dual_scores.opportunity_score:.1f}/100")
                    print(f"  Sell-Risk Score: {dual_scores.sell_risk_score:.1f}/100")
                    print(f"  Overall Bias: {dual_scores.overall_bias}")
                    print(f"  Confidence: {dual_scores.confidence:.1%}")
                    
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
            days = int(input(f"Analysis period in days (default {self.settings.default_days}): ") or str(self.settings.default_days))
        except ValueError:
            days = self.settings.default_days
        
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
        """Generate a report for a single stock."""
        print("\n📄 Generate Single Stock Report")
        print("-" * 35)
        
        ticker = input("Enter ticker symbol: ").strip().upper()
        if not ticker:
            print("❌ Ticker cannot be empty.")
            input("Press Enter to continue...")
            return
        
        try:
            days = int(input(f"Analysis period in days (default {self.settings.default_days}): ") or str(self.settings.default_days))
        except ValueError:
            days = self.settings.default_days
        
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
    
    def _generate_market_summary_report(self):
        """Generate market summary report."""
        print("\n📊 Generate Market Summary Report")
        print("-" * 35)
        
        tickers_input = input("Enter tickers (comma-separated): ").strip()
        tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
        
        if not tickers:
            print("❌ Please enter at least one ticker.")
            input("Press Enter to continue...")
            return
        
        try:
            days = int(input(f"Analysis period in days (default {self.settings.default_days}): ") or str(self.settings.default_days))
        except ValueError:
            days = self.settings.default_days
        
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
            days = int(input(f"Analysis period in days (default {self.settings.default_days}): ") or str(self.settings.default_days))
        except ValueError:
            days = self.settings.default_days
        
        print(f"\n🔄 Running comprehensive analysis for {ticker}...")
        
        try:
            results = self.system.analyze_ticker(ticker, days)
            
            if "error" not in results:
                print(f"\n🎯 COMPREHENSIVE ANALYSIS - {ticker}")
                print("=" * 50)
                
                # Key metrics
                market_data = results["market_data"]
                print(f"\n💰 Price: ${market_data.current_price:.2f}")
                
                # Dual scores
                dual_scores = results["dual_scores"]
                print(f"📊 Opportunity Score: {dual_scores.opportunity_score:.1f}/100")
                print(f"📊 Sell-Risk Score: {dual_scores.sell_risk_score:.1f}/100")
                print(f"🎯 Overall Bias: {dual_scores.overall_bias}")
                
                # Cycle analysis
                cycle = results["cycle_analysis"]
                print(f"🔄 Cycle Phase: {cycle.cycle_phase.replace('_', ' ').title()}")
                print(f"📰 News Risk: {cycle.news_risk_score:.1f}/100")
                print(f"📈 Good News Effectiveness: {cycle.good_news_effectiveness:.1f}/100")
                
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
            self.settings.set("portfolio_file", new_file)
            self.settings.save()
            print(f"✅ Portfolio file set to: {self.portfolio_file}")
        
        input("Press Enter to continue...")
    
    def _set_default_keywords(self):
        """Set default keywords."""
        print(f"\n🔑 Current default keywords: {', '.join(self.default_keywords)}")
        new_keywords = input("Enter new keywords (comma-separated, leave empty to keep current): ").strip()
        
        if new_keywords:
            self.default_keywords = [k.strip() for k in new_keywords.split(',') if k.strip()]
            self.settings.set("default_keywords", self.default_keywords)
            self.settings.save()
            print(f"✅ Default keywords updated: {', '.join(self.default_keywords)}")
        
        input("Press Enter to continue...")
    
    def _set_default_period(self):
        """Set default analysis period."""
        print(f"\n📊 Current default period: {self.settings.default_days} days")
        try:
            new_period = int(input("Enter new default period in days: "))
            if new_period > 0:
                self.settings.set("default_days", new_period)
                self.settings.save()
                print(f"✅ Default period set to: {new_period} days")
            else:
                print("❌ Period must be positive.")
        except ValueError:
            print("❌ Invalid number.")
        
        input("Press Enter to continue...")
    
    def _set_max_headlines(self):
        """Set default max headlines."""
        print(f"\n📈 Current default max headlines: {self.settings.default_max_headlines}")
        try:
            new_max = int(input("Enter new default max headlines: "))
            if new_max > 0:
                self.settings.set("default_max_headlines", new_max)
                self.settings.save()
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
        print(f"📊 Default Period: {self.settings.default_days} days")
        print(f"📈 Default Max Headlines: {self.settings.default_max_headlines}")
        
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
        manager = self._get_portfolio_manager()
        return manager.load()
    
    def _save_portfolio_data(self, portfolio: Dict):
        """Save portfolio data to file."""
        manager = self._get_portfolio_manager()
        try:
            manager.save(portfolio)
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
            self.settings.set("portfolio_file", file_path)
            self.settings.save()
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
            manager = self._get_portfolio_manager()
            imported_portfolio = manager.import_csv(file_path)
            imported_positions = imported_portfolio.get('positions', [])

            if imported_positions:
                portfolio = self._load_portfolio_data()

                existing_tickers = {pos.get('ticker') for pos in portfolio.get('positions', [])}
                duplicates = [pos for pos in imported_positions if pos.get('ticker') in existing_tickers]

                if duplicates:
                    print(f"⚠️  Found {len(duplicates)} duplicate tickers:")
                    for dup in duplicates:
                        print(f"    • {dup.get('ticker')}")

                    action = input("Replace duplicates or skip? (replace/skip/cancel): ").lower()
                    if action == 'cancel':
                        input("Press Enter to continue...")
                        return
                    if action == 'replace':
                        portfolio['positions'] = [
                            pos for pos in portfolio.get('positions', [])
                            if pos.get('ticker') not in {dup.get('ticker') for dup in duplicates}
                        ]
                    elif action == 'skip':
                        imported_positions = [pos for pos in imported_positions if pos.get('ticker') not in existing_tickers]

                portfolio.setdefault('positions', []).extend(imported_positions)
                self._save_portfolio_data(portfolio)
                print(f"✅ Successfully imported {len(imported_positions)} positions")
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
            manager = self._get_portfolio_manager()
            manager.export_csv(portfolio, file_path)
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
