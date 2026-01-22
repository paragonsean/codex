#!/usr/bin/env python3
"""
advanced_trading_system.py

Main integration system that combines all advanced features:
- News interpretation as catalysts and risk flags
- Cycle peak detection for semiconductor/memory stocks
- "Good news not working" analysis
- Actionable recommendations with portfolio awareness
- Alerts monitoring with multiple output formats

Usage:
    python advanced_trading_system.py --portfolio portfolio.json --alerts
    python advanced_trading_system.py --watchlist AAPL TSLA NVDA --output json,csv
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from actionable_recommendations import ActionableRecommendationsEngine, Recommendation, PortfolioSuggestion
from advanced_news_interpreter import AdvancedNewsInterpreter, CycleAnalysis, GoodNewsAnalysis
from alerts_system import AlertsSystem
from dual_scoring_system import DualScoringSystem
from market_data_processor import MarketDataProcessor
from news import fetch_headlines_for_ticker
from trading_strategy_analyzer import Position, TradingStrategy, TRADING_STRATEGIES


class AdvancedTradingSystem:
    """Main integration system for advanced trading analysis."""
    
    def __init__(self, state_file: str = "trading_state.json"):
        self.state_file = state_file
        self.news_interpreter = AdvancedNewsInterpreter()
        self.recommendations_engine = ActionableRecommendationsEngine()
        self.alerts_system = AlertsSystem()
        self.dual_scorer = DualScoringSystem()
        self.market_processor = MarketDataProcessor()
        
        # Load portfolio if available
        self.portfolio = self._load_portfolio()
    
    def analyze_ticker(self, ticker: str, days: int = 180, max_headlines: int = 25) -> Dict:
        """Perform comprehensive analysis of a single ticker."""
        print(f"\n🔄 Analyzing {ticker}...")
        
        try:
            # Fetch market data
            market_data = self._fetch_market_data(ticker, days)
            if not market_data:
                return {"error": f"No market data available for {ticker}"}
            
            # Fetch news headlines
            headlines = fetch_headlines_for_ticker(
                ticker=ticker,
                max_items=max_headlines,
                keywords=["AI", "HBM", "DRAM", "NAND", "capex", "guidance", "inventory", "datacenter"]
            )
            
            # Perform dual scoring analysis
            dual_scores = self.dual_scorer.calculate_scores(market_data)
            
            # Perform advanced news interpretation
            news_catalysts = self.news_interpreter.analyze_news_catalysts(headlines, market_data)
            cycle_analysis = self.news_interpreter.analyze_cycle_conditions(ticker, headlines, market_data)
            good_news_analysis = self.news_interpreter.analyze_good_news_effectiveness(headlines, market_data)
            
            # Generate actionable recommendation
            recommendation = self.recommendations_engine.generate_recommendation(
                ticker, dual_scores, cycle_analysis, good_news_analysis, market_data
            )
            
            # Compile results
            results = {
                "ticker": ticker,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "market_data": {
                    "current_price": market_data.current_price,
                    "indicators": market_data.indicators,
                    "risk_metrics": market_data.risk_metrics
                },
                "dual_scores": {
                    "opportunity_score": dual_scores.opportunity_score,
                    "sell_risk_score": dual_scores.sell_risk_score,
                    "overall_bias": dual_scores.overall_bias,
                    "confidence": dual_scores.confidence
                },
                "cycle_analysis": {
                    "cycle_phase": cycle_analysis.cycle_phase,
                    "cycle_confidence": cycle_analysis.cycle_confidence,
                    "news_risk_score": cycle_analysis.news_risk_score,
                    "good_news_effectiveness": cycle_analysis.good_news_effectiveness,
                    "key_signals": cycle_analysis.key_cycle_signals,
                    "transition_risk": cycle_analysis.phase_transition_risk
                },
                "good_news_analysis": {
                    "positive_headlines": len(good_news_analysis.positive_headlines),
                    "failure_rate": good_news_analysis.failure_rate,
                    "effectiveness_score": good_news_analysis.effectiveness_score,
                    "alert_triggered": good_news_analysis.alert_triggered,
                    "consecutive_failures": good_news_analysis.consecutive_failures
                },
                "recommendation": {
                    "tier": recommendation.tier,
                    "confidence": recommendation.confidence,
                    "urgency": recommendation.urgency,
                    "top_3_reasons": recommendation.top_3_reasons,
                    "key_levels": recommendation.key_levels,
                    "next_review_date": recommendation.next_review_date,
                    "position_sizing": recommendation.position_sizing,
                    "hedge_suggestions": recommendation.hedge_suggestions
                },
                "news_catalysts": {
                    "total_headlines": len(headlines),
                    "positive_catalysts": len([c for c in news_catalysts if c.catalyst_type == "positive_catalyst"]),
                    "negative_catalysts": len([c for c in news_catalysts if c.catalyst_type == "negative_catalyst"]),
                    "risk_flags": len([c for c in news_catalysts if c.catalyst_type == "risk_flag"])
                }
            }
            
            return results
            
        except Exception as e:
            return {"error": f"Analysis failed for {ticker}: {str(e)}"}
    
    def analyze_portfolio(self, portfolio_file: str, days: int = 180) -> Dict:
        """Analyze entire portfolio with portfolio-aware suggestions."""
        print(f"\n📚 Analyzing portfolio from {portfolio_file}...")
        
        try:
            # Load portfolio
            with open(portfolio_file, 'r') as f:
                portfolio_data = json.load(f)
            
            positions = []
            for pos_data in portfolio_data.get('positions', []):
                position = Position(
                    ticker=pos_data['ticker'],
                    shares=pos_data['shares'],
                    cost_basis=pos_data['cost_basis']
                )
                positions.append(position)
            
            # Analyze each position
            results = {
                "portfolio_name": portfolio_data.get('portfolio_name', 'Unknown Portfolio'),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "positions": [],
                "portfolio_suggestions": None,
                "summary": {}
            }
            
            recommendations = []
            
            for position in positions:
                ticker_analysis = self.analyze_ticker(position.ticker, days)
                if "error" not in ticker_analysis:
                    # Add position information
                    ticker_analysis["position"] = {
                        "shares": position.shares,
                        "cost_basis": position.cost_basis,
                        "current_value": position.shares * ticker_analysis["market_data"]["current_price"],
                        "unrealized_pnl": (ticker_analysis["market_data"]["current_price"] - position.cost_basis) * position.shares,
                        "unrealized_pnl_pct": ((ticker_analysis["market_data"]["current_price"] - position.cost_basis) / position.cost_basis) * 100
                    }
                    results["positions"].append(ticker_analysis)
                    
                    # Create recommendation object for portfolio analysis
                    rec = Recommendation(
                        ticker=position.ticker,
                        tier=ticker_analysis["recommendation"]["tier"],
                        confidence=ticker_analysis["recommendation"]["confidence"],
                        urgency=ticker_analysis["recommendation"]["urgency"],
                        top_3_reasons=ticker_analysis["recommendation"]["top_3_reasons"],
                        key_levels=ticker_analysis["recommendation"]["key_levels"],
                        next_review_date=ticker_analysis["recommendation"]["next_review_date"],
                        position_sizing=ticker_analysis["recommendation"]["position_sizing"],
                        hedge_suggestions=ticker_analysis["recommendation"]["hedge_suggestions"]
                    )
                    recommendations.append(rec)
            
            # Generate portfolio suggestions
            if recommendations:
                portfolio_weights = {pos.ticker: pos.shares for pos in positions}
                portfolio_suggestions = self.recommendations_engine.generate_portfolio_suggestions(
                    recommendations, portfolio_weights
                )
                results["portfolio_suggestions"] = {
                    "concentration_warnings": portfolio_suggestions.concentration_warnings,
                    "rotation_targets": portfolio_suggestions.rotation_targets,
                    "sector_adjustments": portfolio_suggestions.sector_adjustments,
                    "timing_guidance": portfolio_suggestions.timing_guidance
                }
            
            # Calculate portfolio summary
            total_value = sum(pos.get("position", {}).get("current_value", 0) for pos in results["positions"])
            total_pnl = sum(pos.get("position", {}).get("unrealized_pnl", 0) for pos in results["positions"])
            
            results["summary"] = {
                "total_positions": len(results["positions"]),
                "total_value": total_value,
                "total_unrealized_pnl": total_pnl,
                "total_unrealized_pnl_pct": (total_pnl / (total_value - total_pnl)) * 100 if total_value != total_pnl else 0,
                "high_risk_positions": len([pos for pos in results["positions"] if pos["recommendation"]["tier"] in ["EXIT/RISK OFF", "TRIM 25-50%"]]),
                "cycle_phase_distribution": self._analyze_cycle_distribution(results["positions"])
            }
            
            return results
            
        except Exception as e:
            return {"error": f"Portfolio analysis failed: {str(e)}"}
    
    def run_alerts_scan(self, tickers: List[str], output_formats: List[str] = ["terminal"]) -> List:
        """Run alerts monitoring scan."""
        return self.alerts_system.daily_scan(tickers, output_formats)
    
    def _fetch_market_data(self, ticker: str, days: int):
        """Fetch market data with fallback to mock data."""
        try:
            return self.market_processor.fetch_and_process(ticker, days)
        except Exception as e:
            print(f"Warning: Could not fetch real data for {ticker}, using mock data: {e}")
            # Fallback to mock data
            from test_dual_scoring import create_mock_market_data
            return create_mock_market_data(ticker)
    
    def _load_portfolio(self) -> Optional[Dict]:
        """Load portfolio from default location."""
        default_portfolio = "sample_portfolio.json"
        if os.path.exists(default_portfolio):
            try:
                with open(default_portfolio, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load portfolio file: {e}")
        return None
    
    def _analyze_cycle_distribution(self, positions: List[Dict]) -> Dict[str, int]:
        """Analyze cycle phase distribution across positions."""
        distribution = {"early": 0, "mid": 0, "late-mid": 0, "late": 0, "rollover_risk": 0}
        
        for position in positions:
            phase = position.get("cycle_analysis", {}).get("cycle_phase", "unknown")
            if phase in distribution:
                distribution[phase] += 1
        
        return distribution
    
    def output_results(self, results: Dict, output_formats: List[str], output_file: Optional[str] = None):
        """Output results in requested formats."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        
        if "terminal" in output_formats:
            self._output_terminal(results)
        
        if "json" in output_formats:
            filename = output_file or f"analysis_{timestamp}.json"
            self._output_json(results, filename)
        
        if "csv" in output_formats:
            filename = output_file or f"analysis_{timestamp}.csv"
            self._output_csv(results, filename)
    
    def _output_terminal(self, results: Dict):
        """Output results to terminal."""
        if "error" in results:
            print(f"❌ {results['error']}")
            return
        
        if "positions" in results:  # Portfolio analysis
            print(f"\n{'='*80}")
            print(f"📚 PORTFOLIO ANALYSIS - {results['portfolio_name']}")
            print(f"{'='*80}")
            
            summary = results["summary"]
            print(f"\n📊 Portfolio Summary:")
            print(f"  Total Positions: {summary['total_positions']}")
            print(f"  Total Value: ${summary['total_value']:,.2f}")
            print(f"  Total P&L: ${summary['total_unrealized_pnl']:,.2f} ({summary['total_unrealized_pnl_pct']:+.1%})")
            print(f"  High Risk Positions: {summary['high_risk_positions']}")
            
            # Cycle distribution
            if summary['cycle_phase_distribution']:
                print(f"\n🔄 Cycle Phase Distribution:")
                for phase, count in summary['cycle_phase_distribution'].items():
                    if count > 0:
                        print(f"  {phase.replace('_', ' ').title()}: {count}")
            
            # Portfolio suggestions
            if results.get("portfolio_suggestions"):
                suggestions = results["portfolio_suggestions"]
                print(f"\n💡 Portfolio Suggestions:")
                print(f"  Timing: {suggestions['timing_guidance']}")
                
                if suggestions["concentration_warnings"]:
                    print(f"\n⚠️  Concentration Warnings:")
                    for warning in suggestions["concentration_warnings"]:
                        print(f"    • {warning}")
                
                if suggestions["rotation_targets"]:
                    print(f"\n🔄 Rotation Targets:")
                    for target in suggestions["rotation_targets"][:5]:
                        print(f"    • {target['ticker']}: {target['reason']}")
            
            # Individual positions
            print(f"\n📈 Position Analysis:")
            for position in results["positions"]:
                pos_data = position["position"]
                rec_data = position["recommendation"]
                
                print(f"\n  {position['ticker']}:")
                print(f"    Shares: {pos_data['shares']} @ ${pos_data['cost_basis']:.2f}")
                print(f"    Current: ${pos_data['current_value']/pos_data['shares']:.2f} ({pos_data['unrealized_pnl_pct']:+.1%})")
                print(f"    Recommendation: {rec_data['tier']} ({rec_data['urgency']})")
                if rec_data['top_3_reasons']:
                    print(f"    Reasons:")
                    for reason in rec_data['top_3_reasons']:
                        print(f"      • {reason}")
        
        else:  # Single ticker analysis
            ticker = results["ticker"]
            print(f"\n{'='*80}")
            print(f"🎯 ADVANCED ANALYSIS - {ticker}")
            print(f"{'='*80}")
            
            # Key metrics
            print(f"\n📊 Key Metrics:")
            print(f"  Current Price: ${results['market_data']['current_price']:.2f}")
            print(f"  Opportunity Score: {results['dual_scores']['opportunity_score']:.1f}/100")
            print(f"  Sell-Risk Score: {results['dual_scores']['sell_risk_score']:.1f}/100")
            print(f"  Overall Bias: {results['dual_scores']['overall_bias']}")
            
            # Cycle analysis
            cycle = results["cycle_analysis"]
            print(f"\n🔄 Cycle Analysis:")
            print(f"  Phase: {cycle['cycle_phase'].replace('_', ' ').title()}")
            print(f"  Confidence: {cycle['cycle_confidence']:.1%}")
            print(f"  News Risk: {cycle['news_risk_score']:.1f}/100")
            print(f"  Good News Effectiveness: {cycle['good_news_effectiveness']:.1f}/100")
            
            if cycle['key_signals']:
                print(f"  Key Signals:")
                for signal in cycle['key_signals']:
                    print(f"    • {signal}")
            
            # Recommendation
            rec = results["recommendation"]
            print(f"\n🎯 Recommendation:")
            print(f"  Tier: {rec['tier']}")
            print(f"  Confidence: {rec['confidence']:.1%}")
            print(f"  Urgency: {rec['urgency']}")
            
            if rec['top_3_reasons']:
                print(f"  Top 3 Reasons:")
                for reason in rec['top_3_reasons']:
                    print(f"    • {reason}")
            
            if rec['key_levels']:
                print(f"\n📍 Key Levels:")
                for level_type, level_value in rec['key_levels'].items():
                    print(f"    {level_type.replace('_', ' ').title()}: {level_value}")
            
            print(f"\n📅 Next Review: {rec['next_review_date']}")
    
    def _output_json(self, results: Dict, filename: str):
        """Output results to JSON file."""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 JSON report saved: {filename}")
    
    def _output_csv(self, results: Dict, filename: str):
        """Output results to CSV file."""
        import csv
        
        if "positions" in results:  # Portfolio analysis
            fieldnames = ['ticker', 'shares', 'cost_basis', 'current_price', 'unrealized_pnl_pct', 
                         'recommendation_tier', 'cycle_phase', 'sell_risk_score', 'opportunity_score']
            
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for position in results["positions"]:
                    row = {
                        'ticker': position['ticker'],
                        'shares': position['position']['shares'],
                        'cost_basis': position['position']['cost_basis'],
                        'current_price': position['market_data']['current_price'],
                        'unrealized_pnl_pct': position['position']['unrealized_pnl_pct'],
                        'recommendation_tier': position['recommendation']['tier'],
                        'cycle_phase': position['cycle_analysis']['cycle_phase'],
                        'sell_risk_score': position['dual_scores']['sell_risk_score'],
                        'opportunity_score': position['dual_scores']['opportunity_score']
                    }
                    writer.writerow(row)
        
        print(f"\n📊 CSV report saved: {filename}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Advanced trading system with comprehensive analysis")
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--portfolio", help="Portfolio JSON file to analyze")
    input_group.add_argument("--tickers", nargs="+", help="Individual tickers to analyze")
    input_group.add_argument("--alerts", nargs="+", help="Run alerts scan for tickers")
    
    # Analysis options
    parser.add_argument("--days", type=int, default=180, help="Analysis period in days")
    parser.add_argument("--max-headlines", type=int, default=25, help="Max headlines to analyze")
    parser.add_argument("--strategy", choices=["swing", "position", "income", "momentum"], 
                       help="Trading strategy for analysis")
    
    # Output options
    parser.add_argument("--output", nargs="+", choices=["terminal", "json", "csv"], 
                       default=["terminal"], help="Output formats")
    parser.add_argument("--output-file", help="Output file name (without extension)")
    
    # Alerts options
    parser.add_argument("--state-file", default="alerts_state.json", help="Alerts state file")
    
    args = parser.parse_args()
    
    system = AdvancedTradingSystem(args.state_file)
    
    if args.alerts:
        # Run alerts scan
        alerts = system.run_alerts_scan(args.alerts, args.output)
        print(f"\n📊 Generated {len(alerts)} alerts")
    
    elif args.portfolio:
        # Portfolio analysis
        results = system.analyze_portfolio(args.portfolio, args.days)
        system.output_results(results, args.output, args.output_file)
    
    elif args.tickers:
        # Individual ticker analysis
        for ticker in args.tickers:
            results = system.analyze_ticker(ticker, args.days, args.max_headlines)
            system.output_results(results, args.output, args.output_file)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
