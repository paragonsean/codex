#!/usr/bin/env python3
"""
alerts_system.py

Alerts monitoring system with daily scanning and threshold-based notifications.
Supports multiple output formats and state tracking for trend analysis.

Features:
- Daily end-of-day scanning
- Threshold-based alerts (sell-risk, cycle phase changes, good news failures)
- State file tracking for trend analysis
- Multiple output formats (terminal, JSON, CSV)
- Alert history and trend monitoring
"""

import argparse
import csv
import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from actionable_recommendations import ActionableRecommendationsEngine, Recommendation
from advanced_news_interpreter import AdvancedNewsInterpreter, CycleAnalysis, GoodNewsAnalysis
from dual_scoring_system import DualScoringSystem
from market_data_processor import MarketDataProcessor


@dataclass
class Alert:
    """Alert with detailed information and trend tracking."""
    ticker: str
    alert_type: str  # "SELL_RISK_HIGH", "CYCLE_PHASE_CHANGE", "GOOD_NEWS_FAILURE", "RECOMMENDATION_CHANGE"
    severity: str  # "INFO", "WARNING", "CRITICAL", "ALERT"
    message: str
    current_value: float
    previous_value: Optional[float]
    threshold: float
    timestamp: str
    trend_direction: str  # "improving", "worsening", "stable"
    additional_data: Dict[str, any]


@dataclass
class AlertState:
    """State tracking for trend analysis."""
    ticker: str
    last_sell_risk_score: float
    last_cycle_phase: str
    last_recommendation_tier: str
    last_good_news_effectiveness: float
    last_update: str
    alert_history: List[Alert]


class AlertsSystem:
    """Alerts monitoring and notification system."""
    
    def __init__(self, state_file: str = "alerts_state.json"):
        self.state_file = state_file
        self.state_data = self._load_state()
        
        # Alert thresholds
        self.thresholds = {
            "sell_risk_high": 70,
            "sell_risk_critical": 85,
            "cycle_transition_risk_high": 60,
            "good_news_failure_critical": 0.6,  # 60% failure rate
            "recommendation_change": True  # Any change in recommendation tier
        }
        
        # Alert types that trigger notifications
        self.alert_types = {
            "SELL_RISK_HIGH": "WARNING",
            "SELL_RISK_CRITICAL": "CRITICAL", 
            "CYCLE_PHASE_CHANGE": "ALERT",
            "GOOD_NEWS_FAILURE": "WARNING",
            "RECOMMENDATION_CHANGE": "INFO"
        }
    
    def daily_scan(self, tickers: List[str], output_formats: List[str] = ["terminal"]) -> List[Alert]:
        """Perform daily end-of-day scan and generate alerts."""
        print(f"🔍 Daily Scan - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"Analyzing {len(tickers)} tickers...")
        
        all_alerts = []
        
        for ticker in tickers:
            try:
                alerts = self._analyze_ticker(ticker)
                all_alerts.extend(alerts)
            except Exception as e:
                print(f"❌ Error analyzing {ticker}: {e}")
        
        # Filter alerts based on severity
        filtered_alerts = [alert for alert in all_alerts if alert.severity in ["WARNING", "CRITICAL", "ALERT"]]
        
        # Output alerts in requested formats
        if filtered_alerts:
            self._output_alerts(filtered_alerts, output_formats)
        else:
            print("✅ No alerts triggered")
        
        # Update state
        self._update_state(tickers)
        
        return filtered_alerts
    
    def _analyze_ticker(self, ticker: str) -> List[Alert]:
        """Analyze single ticker for alert conditions."""
        alerts = []
        
        # Get current state
        current_state = self.state_data.get(ticker, AlertState(
            ticker=ticker,
            last_sell_risk_score=0,
            last_cycle_phase="unknown",
            last_recommendation_tier="unknown",
            last_good_news_effectiveness=50,
            last_update="",
            alert_history=[]
        ))
        
        # Perform analysis (using mock data for demonstration)
        # In practice, this would fetch real data
        mock_data = self._create_mock_analysis(ticker)
        
        # Check sell risk alerts
        sell_risk_alert = self._check_sell_risk_alert(ticker, mock_data['sell_risk_score'], current_state)
        if sell_risk_alert:
            alerts.append(sell_risk_alert)
        
        # Check cycle phase change alerts
        cycle_alert = self._check_cycle_phase_alert(ticker, mock_data['cycle_phase'], current_state)
        if cycle_alert:
            alerts.append(cycle_alert)
        
        # Check good news failure alerts
        good_news_alert = self._check_good_news_alert(ticker, mock_data['good_news_effectiveness'], current_state)
        if good_news_alert:
            alerts.append(good_news_alert)
        
        # Check recommendation change alerts
        rec_alert = self._check_recommendation_alert(ticker, mock_data['recommendation_tier'], current_state)
        if rec_alert:
            alerts.append(rec_alert)
        
        return alerts
    
    def _check_sell_risk_alert(self, ticker: str, current_score: float, state: AlertState) -> Optional[Alert]:
        """Check for sell risk threshold alerts."""
        if current_score >= self.thresholds["sell_risk_critical"]:
            severity = "CRITICAL"
            threshold = self.thresholds["sell_risk_critical"]
        elif current_score >= self.thresholds["sell_risk_high"]:
            severity = "WARNING"
            threshold = self.thresholds["sell_risk_high"]
        else:
            return None
        
        # Determine trend direction
        trend = self._determine_trend(current_score, state.last_sell_risk_score)
        
        return Alert(
            ticker=ticker,
            alert_type="SELL_RISK_HIGH",
            severity=severity,
            message=f"Sell risk score at {current_score:.1f} (threshold: {threshold})",
            current_value=current_score,
            previous_value=state.last_sell_risk_score,
            threshold=threshold,
            timestamp=datetime.now(timezone.utc).isoformat(),
            trend_direction=trend,
            additional_data={"risk_category": "high" if current_score >= 85 else "elevated"}
        )
    
    def _check_cycle_phase_alert(self, ticker: str, current_phase: str, state: AlertState) -> Optional[Alert]:
        """Check for cycle phase change alerts."""
        if current_phase == state.last_cycle_phase:
            return None
        
        # Determine severity based on phase direction
        if current_phase in ["late", "rollover_risk"] and state.last_cycle_phase in ["early", "mid"]:
            severity = "ALERT"
        elif current_phase == "rollover_risk":
            severity = "CRITICAL"
        else:
            severity = "INFO"
        
        # Only return high-severity alerts
        if severity not in ["ALERT", "CRITICAL"]:
            return None
        
        return Alert(
            ticker=ticker,
            alert_type="CYCLE_PHASE_CHANGE",
            severity=severity,
            message=f"Cycle phase changed to {current_phase.replace('_', ' ').title()}",
            current_value=0,  # No numeric value for phase
            previous_value=0,
            threshold=0,
            timestamp=datetime.now(timezone.utc).isoformat(),
            trend_direction="worsening" if current_phase in ["late", "rollover_risk"] else "improving",
            additional_data={"from_phase": state.last_cycle_phase, "to_phase": current_phase}
        )
    
    def _check_good_news_alert(self, ticker: str, current_effectiveness: float, state: AlertState) -> Optional[Alert]:
        """Check for good news failure alerts."""
        if current_effectiveness <= self.thresholds["good_news_failure_critical"]:
            severity = "WARNING"
            threshold = self.thresholds["good_news_failure_critical"]
        else:
            return None
        
        trend = self._determine_trend(current_effectiveness, state.last_good_news_effectiveness)
        
        return Alert(
            ticker=ticker,
            alert_type="GOOD_NEWS_FAILURE",
            severity=severity,
            message=f"Good news effectiveness at {current_effectiveness:.1f}% (threshold: {threshold*100:.0f}%)",
            current_value=current_effectiveness,
            previous_value=state.last_good_news_effectiveness,
            threshold=threshold * 100,
            timestamp=datetime.now(timezone.utc).isoformat(),
            trend_direction=trend,
            additional_data={"failure_rate": 1 - (current_effectiveness / 100)}
        )
    
    def _check_recommendation_alert(self, ticker: str, current_tier: str, state: AlertState) -> Optional[Alert]:
        """Check for recommendation change alerts."""
        if current_tier == state.last_recommendation_tier:
            return None
        
        # Determine severity based on recommendation direction
        if current_tier in ["EXIT/RISK OFF", "TRIM 25-50%"]:
            severity = "WARNING"
        elif current_tier == "HOLD/ADD":
            severity = "INFO"
        else:
            severity = "INFO"
        
        return Alert(
            ticker=ticker,
            alert_type="RECOMMENDATION_CHANGE",
            severity=severity,
            message=f"Recommendation changed to {current_tier}",
            current_value=0,
            previous_value=0,
            threshold=0,
            timestamp=datetime.now(timezone.utc).isoformat(),
            trend_direction="worsening" if current_tier in ["EXIT/RISK OFF", "TRIM 25-50%"] else "improving",
            additional_data={"from_tier": state.last_recommendation_tier, "to_tier": current_tier}
        )
    
    def _determine_trend(self, current: float, previous: float) -> str:
        """Determine trend direction."""
        if previous == 0:
            return "stable"
        
        change = (current - previous) / abs(previous)
        
        if change > 0.05:  # 5% change
            return "improving" if current > previous else "worsening"
        elif change < -0.05:
            return "worsening" if current > previous else "improving"
        else:
            return "stable"
    
    def _output_alerts(self, alerts: List[Alert], formats: List[str]):
        """Output alerts in requested formats."""
        if "terminal" in formats:
            self._output_terminal(alerts)
        
        if "json" in formats:
            self._output_json(alerts)
        
        if "csv" in formats:
            self._output_csv(alerts)
    
    def _output_terminal(self, alerts: List[Alert]):
        """Output alerts to terminal in human-readable format."""
        print(f"\n{'='*80}")
        print(f"🚨 ALERTS SUMMARY")
        print(f"{'='*80}")
        
        # Group by severity
        critical_alerts = [a for a in alerts if a.severity == "CRITICAL"]
        alert_alerts = [a for a in alerts if a.severity == "ALERT"]
        warning_alerts = [a for a in alerts if a.severity == "WARNING"]
        info_alerts = [a for a in alerts if a.severity == "INFO"]
        
        severity_emoji = {"CRITICAL": "🔴", "ALERT": "🟠", "WARNING": "🟡", "INFO": "🔵"}
        
        for severity, alert_list, emoji in [
            ("CRITICAL", critical_alerts, "🔴"),
            ("ALERT", alert_alerts, "🟠"),
            ("WARNING", warning_alerts, "🟡"),
            ("INFO", info_alerts, "🔵")
        ]:
            if alert_list:
                print(f"\n{emoji} {severity} ({len(alert_list)}):")
                for alert in alert_list:
                    trend_emoji = {"improving": "📈", "worsening": "📉", "stable": "➡️"}.get(alert.trend_direction, "❓")
                    print(f"  {trend_emoji} {alert.ticker}: {alert.message}")
                    if alert.previous_value is not None:
                        print(f"      Previous: {alert.previous_value:.1f} → Current: {alert.current_value:.1f}")
    
    def _output_json(self, alerts: List[Alert]):
        """Output alerts to JSON file."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"alerts_{timestamp}.json"
        
        alert_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_alerts": len(alerts),
            "alerts": [asdict(alert) for alert in alerts]
        }
        
        with open(filename, 'w') as f:
            json.dump(alert_data, f, indent=2)
        
        print(f"\n📄 JSON report saved: {filename}")
    
    def _output_csv(self, alerts: List[Alert]):
        """Output alerts to CSV file."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"alerts_{timestamp}.csv"
        
        fieldnames = ['ticker', 'alert_type', 'severity', 'message', 'current_value', 
                     'previous_value', 'threshold', 'timestamp', 'trend_direction']
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for alert in alerts:
                row = {field: getattr(alert, field) for field in fieldnames}
                writer.writerow(row)
        
        print(f"\n📊 CSV report saved: {filename}")
    
    def _load_state(self) -> Dict[str, AlertState]:
        """Load state from file."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                
                state = {}
                for ticker, state_data in data.items():
                    state[ticker] = AlertState(**state_data)
                
                return state
            except Exception as e:
                print(f"Warning: Could not load state file: {e}")
        
        return {}
    
    def _update_state(self, tickers: List[str]):
        """Update state file with current values."""
        # In practice, this would fetch real current values
        # For demonstration, we'll use mock data
        for ticker in tickers:
            mock_data = self._create_mock_analysis(ticker)
            
            self.state_data[ticker] = AlertState(
                ticker=ticker,
                last_sell_risk_score=mock_data['sell_risk_score'],
                last_cycle_phase=mock_data['cycle_phase'],
                last_recommendation_tier=mock_data['recommendation_tier'],
                last_good_news_effectiveness=mock_data['good_news_effectiveness'],
                last_update=datetime.now(timezone.utc).isoformat(),
                alert_history=[]
            )
        
        # Save state
        state_dict = {ticker: asdict(state) for ticker, state in self.state_data.items()}
        
        with open(self.state_file, 'w') as f:
            json.dump(state_dict, f, indent=2)
    
    def _create_mock_analysis(self, ticker: str) -> Dict[str, any]:
        """Create mock analysis data for demonstration."""
        # Simulate different scenarios for different tickers
        scenarios = {
            'MU': {
                'sell_risk_score': 75.0,
                'cycle_phase': 'late',
                'recommendation_tier': 'TRIM 25-50%',
                'good_news_effectiveness': 25.0
            },
            'WDC': {
                'sell_risk_score': 85.0,
                'cycle_phase': 'rollover_risk',
                'recommendation_tier': 'EXIT/RISK OFF',
                'good_news_effectiveness': 15.0
            },
            'AAPL': {
                'sell_risk_score': 45.0,
                'cycle_phase': 'late-mid',
                'recommendation_tier': 'HOLD/ADD',
                'good_news_effectiveness': 60.0
            }
        }
        
        return scenarios.get(ticker, scenarios['MU'])
    
    def get_alert_history(self, ticker: str, days: int = 30) -> List[Alert]:
        """Get alert history for a specific ticker."""
        state = self.state_data.get(ticker)
        if not state:
            return []
        
        # Filter alerts by date
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        return [alert for alert in state.alert_history 
                if datetime.fromisoformat(alert.timestamp) > cutoff_date]
    
    def get_trend_summary(self, ticker: str) -> Dict[str, str]:
        """Get trend summary for a ticker."""
        state = self.state_data.get(ticker)
        if not state:
            return {}
        
        return {
            "sell_risk_trend": f"{state.last_sell_risk_score:.1f} (last updated: {state.last_update[:10]})",
            "cycle_phase": state.last_cycle_phase,
            "recommendation": state.last_recommendation_tier,
            "good_news_effectiveness": f"{state.last_good_news_effectiveness:.1f}%"
        }


def main():
    """Run alerts system."""
    parser = argparse.ArgumentParser(description="Alerts monitoring system")
    parser.add_argument("tickers", nargs="+", help="Tickers to monitor")
    parser.add_argument("--formats", nargs="+", choices=["terminal", "json", "csv"], 
                       default=["terminal"], help="Output formats")
    parser.add_argument("--state-file", default="alerts_state.json", help="State file location")
    parser.add_argument("--history", help="Show alert history for ticker")
    parser.add_argument("--trend", help="Show trend summary for ticker")
    
    args = parser.parse_args()
    
    alerts_system = AlertsSystem(args.state_file)
    
    if args.history:
        history = alerts_system.get_alert_history(args.history, days=30)
        print(f"\n📜 Alert History for {args.history} (last 30 days):")
        for alert in history:
            print(f"  {alert.timestamp[:10]}: {alert.message}")
    
    elif args.trend:
        trend = alerts_system.get_trend_summary(args.trend)
        print(f"\n📈 Trend Summary for {args.trend}:")
        for key, value in trend.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
    
    else:
        # Run daily scan
        alerts = alerts_system.daily_scan(args.tickers, args.formats)


if __name__ == "__main__":
    main()
