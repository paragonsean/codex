#!/usr/bin/env python3
"""
stock_report_generator.py

Generate comprehensive HTML and PDF reports for stock analysis using the market_news_analyzer data.
Creates professional-looking reports with charts, news analysis, and technical indicators.

Usage:
    python stock_report_generator.py --tickers MU WDC AMD --days 180 --output-dir reports
    python stock_report_generator.py --tickers AAPL --days 365 --format pdf --output-dir reports
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import yfinance as yf

# Import the news analyzer functionality
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from news import (
    fetch_prices, summarize_prices, fetch_headlines_for_ticker,
    compute_combined_signal, TickerReport, Headline, PriceSummary
)


class StockReportGenerator:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_advanced_single_html(self, results: Dict, ticker: str, days: int) -> str:
        market_data = results["market_data"]
        dual_scores = results["dual_scores"]
        cycle_analysis = results["cycle_analysis"]
        recommendation = results["recommendation"]
        good_news_analysis = results.get("good_news_analysis")
        news_catalysts_data = results.get("news_catalysts_data", {})

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
                <span class="metric-value">${market_data.current_price:.2f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Opportunity Score:</span>
                <span class="score opportunity">{dual_scores.opportunity_score:.1f}/100</span>
            </div>
            <div class="metric">
                <span class="metric-label">Sell-Risk Score:</span>
                <span class="score sell-risk">{dual_scores.sell_risk_score:.1f}/100</span>
            </div>
            <div class="metric">
                <span class="metric-label">Overall Bias:</span>
                <span class="metric-value">{dual_scores.overall_bias}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Confidence:</span>
                <span class="metric-value">{dual_scores.confidence:.1f}%</span>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Price & Volume Data</h2>
            <div class="metric">
                <span class="metric-label">20-Day High:</span>
                <span class="metric-value">${market_data.indicators.get('high_20d', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">20-Day Low:</span>
                <span class="metric-value">${market_data.indicators.get('low_20d', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">50-Day High:</span>
                <span class="metric-value">${market_data.indicators.get('high_50d', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">50-Day Low:</span>
                <span class="metric-value">${market_data.indicators.get('low_50d', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Volume Z-Score:</span>
                <span class="metric-value">{market_data.indicators.get('volume_z_score', 'N/A'):.2f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">ATR (14):</span>
                <span class="metric-value">{market_data.indicators.get('atr_14', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Position vs 20D High:</span>
                <span class="metric-value">{market_data.indicators.get('position_20d_high', 'N/A'):.1f}%</span>
            </div>
        </div>
        
        <div class="section">
            <h2>📰 News Sentiment Analysis</h2>
            <div class="metric">
                <span class="metric-label">Total Headlines:</span>
                <span class="metric-value">{news_catalysts_data.get('total_headlines', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Positive Catalysts:</span>
                <span class="metric-value">{news_catalysts_data.get('positive_catalysts', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Negative Catalysts:</span>
                <span class="metric-value">{news_catalysts_data.get('negative_catalysts', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Neutral Headlines:</span>
                <span class="metric-value">{news_catalysts_data.get('neutral_catalysts', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Good News Effectiveness:</span>
                <span class="metric-value">{good_news_analysis.effectiveness_score:.1f}/100</span>
            </div>
            <div class="metric">
                <span class="metric-label">Good News Failure Rate:</span>
                <span class="metric-value">{good_news_analysis.failure_rate:.1%}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Positive Headlines:</span>
                <span class="metric-value">{len(good_news_analysis.positive_headlines)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Alert Triggered:</span>
                <span class="metric-value">{good_news_analysis.alert_triggered}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Consecutive Failures:</span>
                <span class="metric-value">{good_news_analysis.consecutive_failures}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>📰 Recent News Headlines</h2>
            {self._advanced_news_headlines_section(good_news_analysis)}
        </div>
        
        <div class="section">
            <h2>📈 News Sentiment Breakdown</h2>
            {self._advanced_sentiment_breakdown_section(news_catalysts_data, good_news_analysis)}
        </div>
        
        <div class="section">
            <h2>📈 News Price Impact Analysis</h2>
            {self._advanced_news_impact_section(good_news_analysis)}
        </div>
        
        <div class="section">
            <h2>🔄 Cycle Analysis</h2>
            <div class="metric">
                <span class="metric-label">Cycle Phase:</span>
                <span class="metric-value">{cycle_analysis.cycle_phase.replace('_', ' ').title()}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Cycle Confidence:</span>
                <span class="metric-value">{cycle_analysis.cycle_confidence:.1%}</span>
            </div>
            <div class="metric">
                <span class="metric-label">News Risk Score:</span>
                <span class="metric-value">{cycle_analysis.news_risk_score:.1f}/100</span>
            </div>
            <div class="metric">
                <span class="metric-label">Good News Effectiveness:</span>
                <span class="metric-value">{cycle_analysis.good_news_effectiveness:.1f}/100</span>
            </div>
            <div class="metric">
                <span class="metric-label">Transition Risk:</span>
                <span class="metric-value">{cycle_analysis.phase_transition_risk if hasattr(cycle_analysis, 'phase_transition_risk') else 'N/A'}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Recommendation</h2>
            <div class="recommendation {self._advanced_recommendation_class(recommendation['tier'])}">
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
                <span class="metric-value">{market_data.indicators.get('rsi_14', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">21D Return:</span>
                <span class="metric-value">{market_data.indicators.get('ret_21d', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">63D Return:</span>
                <span class="metric-value">{market_data.indicators.get('ret_63d', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Volume Z-Score:</span>
                <span class="metric-value">{market_data.indicators.get('volume_z_score', 'N/A'):.2f}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>⚠️ Risk Metrics</h2>
            <div class="metric">
                <span class="metric-label">Current Drawdown:</span>
                <span class="metric-value">{market_data.risk_metrics.get('current_drawdown', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Max Drawdown:</span>
                <span class="metric-value">{market_data.risk_metrics.get('max_drawdown', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Volatility (20D):</span>
                <span class="metric-value">{market_data.risk_metrics.get('volatility_20d', 'N/A')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Volatility Regime:</span>
                <span class="metric-value">{market_data.risk_metrics.get('volatility_regime', 'N/A')}</span>
            </div>
        </div>
    </div>
</body>
</html>
        """
        return html_content

    def generate_advanced_single_markdown(self, results: Dict, ticker: str, days: int) -> str:
        market_data = results["market_data"]
        dual_scores = results["dual_scores"]
        cycle_analysis = results["cycle_analysis"]
        recommendation = results["recommendation"]
        good_news_analysis = results.get("good_news_analysis")
        news_catalysts_data = results.get("news_catalysts_data", {})

        md_content = f"""# 🎯 Advanced Stock Analysis Report - {ticker}

**Analysis Period:** {days} days  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Key Metrics

| Metric | Value |
|--------|-------|
| **Current Price** | ${market_data.current_price:.2f} |
| **Opportunity Score** | {dual_scores.opportunity_score:.1f}/100 |
| **Sell-Risk Score** | {dual_scores.sell_risk_score:.1f}/100 |
| **Overall Bias** | {dual_scores.overall_bias} |
| **Confidence** | {dual_scores.confidence:.1%} |

---

## 📈 Price & Volume Data

| Metric | Value |
|--------|-------|
| **20-Day High** | ${market_data.indicators.get('high_20d', 'N/A')} |
| **20-Day Low** | ${market_data.indicators.get('low_20d', 'N/A')} |
| **50-Day High** | ${market_data.indicators.get('high_50d', 'N/A')} |
| **50-Day Low** | ${market_data.indicators.get('low_50d', 'N/A')} |
| **Volume Z-Score** | {market_data.indicators.get('volume_z_score', 'N/A'):.2f} |
| **ATR (14)** | {market_data.indicators.get('atr_14', 'N/A'):.2f} |
| **Position vs 20D High** | {market_data.indicators.get('position_20d_high', 'N/A'):.1%} |

---

## 📰 News Sentiment Analysis

| Metric | Value |
|--------|-------|
| **Total Headlines** | {news_catalysts_data.get('total_headlines', 'N/A')} |
| **Positive Catalysts** | {news_catalysts_data.get('positive_catalysts', 'N/A')} |
| **Negative Catalysts** | {news_catalysts_data.get('negative_catalysts', 'N/A')} |
| **Neutral Headlines** | {news_catalysts_data.get('neutral_catalysts', 'N/A')} |
| **Good News Effectiveness** | {good_news_analysis.effectiveness_score:.1f}/100 |
| **Good News Failure Rate** | {good_news_analysis.failure_rate:.1%} |
| **Positive Headlines** | {len(good_news_analysis.positive_headlines)} |
| **Alert Triggered** | {good_news_analysis.alert_triggered} |
| **Consecutive Failures** | {good_news_analysis.consecutive_failures} |

---

## 📰 Recent News Headlines

{self._advanced_news_headlines_markdown(good_news_analysis)}

---

## 📈 News Sentiment Breakdown

{self._advanced_sentiment_breakdown_markdown(news_catalysts_data, good_news_analysis)}

---

## 📈 News Price Impact Analysis

{self._advanced_news_impact_markdown(good_news_analysis)}

---

## 🔄 Cycle Analysis

| Metric | Value |
|--------|-------|
| **Cycle Phase** | {cycle_analysis.cycle_phase.replace('_', ' ').title()} |
| **Cycle Confidence** | {cycle_analysis.cycle_confidence:.1%} |
| **News Risk Score** | {cycle_analysis.news_risk_score:.1f}/100 |
| **Good News Effectiveness** | {cycle_analysis.good_news_effectiveness:.1f}/100 |
| **Transition Risk** | {cycle_analysis.phase_transition_risk if hasattr(cycle_analysis, 'phase_transition_risk') else 'N/A'} |

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
| **RSI (14)** | {market_data.indicators.get('rsi_14', 'N/A'):.1f} |
| **21D Return** | {market_data.indicators.get('ret_21d', 'N/A')} |
| **63D Return** | {market_data.indicators.get('ret_63d', 'N/A')} |
| **Volume Z-Score** | {market_data.indicators.get('volume_z_score', 'N/A'):.2f} |

---

## ⚠️ Risk Metrics

| Metric | Value |
|--------|-------|
| **Current Drawdown** | {market_data.risk_metrics.get('current_drawdown', 'N/A')} |
| **Max Drawdown** | {market_data.risk_metrics.get('max_drawdown', 'N/A')} |
| **Volatility (20D)** | {market_data.risk_metrics.get('volatility_20d', 'N/A')} |
| **Volatility Regime** | {market_data.risk_metrics.get('volatility_regime', 'N/A')} |

---

*Report generated by Advanced Trading System*
"""
        return md_content

    def _advanced_recommendation_class(self, tier: str) -> str:
        if "BUY" in tier:
            return "buy"
        if "SELL" in tier:
            return "sell"
        return "hold"

    def _advanced_impact_color(self, impact_class: str) -> str:
        colors = {
            "strong-positive": "#28a745",
            "moderate-positive": "#17a2b8",
            "weak-positive": "#ffc107",
            "negative": "#dc3545",
        }
        return colors.get(impact_class, "#6c757d")

    def _advanced_news_impact_section(self, good_news_analysis) -> str:
        forward_returns = good_news_analysis.forward_return_analysis if hasattr(good_news_analysis, 'forward_return_analysis') else {}
        if not forward_returns:
            return "<p>No forward return analysis available</p>"

        impact_html = ""
        sorted_headlines = sorted(forward_returns.items(), key=lambda x: x[0], reverse=True)
        for i, (headline, returns) in enumerate(sorted_headlines[:10]):
            if returns and len(returns) > 0:
                avg_1d = returns.get('1d', 0) * 100
                avg_2d = returns.get('2d', 0) * 100
                avg_3d = returns.get('3d', 0) * 100

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
                <div class="metric" style="border-left: 4px solid {self._advanced_impact_color(impact_class)}; padding-left: 10px;">
                    <div style="font-weight: bold; margin-bottom: 5px;">{i+1}. {headline[:50]}...</div>
                    <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                        <span style="color: #666;">1D:</span>
                        <span class="metric-value" style="color: {self._advanced_impact_color(impact_class)};">{avg_1d:+.1f}%</span>
                        <span style="color: #666;">2D:</span>
                        <span class="metric-value" style="color: {self._advanced_impact_color(impact_class)};">{avg_2d:+.1f}%</span>
                        <span style="color: #666;">3D:</span>
                        <span class="metric-value" style="color: {self._advanced_impact_color(impact_class)};">{avg_3d:+.1f}%</span>
                    </div>
                    <div style="font-style: italic; color: #666; margin-top: 5px;">{impact_strength}</div>
                </div>
                """

        return impact_html

    def _advanced_sentiment_breakdown_section(self, news_catalysts_data: Dict, good_news_analysis) -> str:
        total_catalysts = news_catalysts_data.get('total_headlines', 0)
        positive_catalysts = news_catalysts_data.get('positive_catalysts', 0)
        negative_catalysts = news_catalysts_data.get('negative_catalysts', 0)
        neutral_catalysts = news_catalysts_data.get('neutral_catalysts', 0)

        if total_catalysts > 0:
            positive_pct = (positive_catalysts / total_catalysts) * 100
            negative_pct = (negative_catalysts / total_catalysts) * 100
            neutral_pct = (neutral_catalysts / total_catalysts) * 100
        else:
            positive_pct = negative_pct = neutral_pct = 0

        failure_rate = getattr(good_news_analysis, 'failure_rate', 0)
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
            <span class="metric-value">{100 - failure_rate:.1f}%</span>
        </div>
        """
        return breakdown_html

    def _advanced_news_headlines_section(self, good_news_analysis) -> str:
        forward_returns = good_news_analysis.forward_return_analysis if hasattr(good_news_analysis, 'forward_return_analysis') else {}
        headlines_html = ""
        if forward_returns and len(forward_returns) > 0:
            sorted_headlines = sorted(forward_returns.items(), key=lambda x: x[0], reverse=True)
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
            for i, (headline, returns) in enumerate(sorted_headlines[:10]):
                if returns and len(returns) > 0:
                    avg_1d = returns.get('1d', 0) * 100
                    avg_2d = returns.get('2d', 0) * 100
                    avg_3d = returns.get('3d', 0) * 100

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

                    impact_color = self._advanced_impact_color(impact_class)
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

    def _advanced_news_impact_markdown(self, good_news_analysis) -> str:
        forward_returns = good_news_analysis.forward_return_analysis if hasattr(good_news_analysis, 'forward_return_analysis') else {}
        if not forward_returns:
            return "No forward return analysis available"

        impact_md = "\n### Recent News Price Impact (Top 10)\n\n"
        sorted_headlines = sorted(forward_returns.items(), key=lambda x: x[0], reverse=True)
        impact_md += "| # | Headline | 1D Return | 2D Return | 3D Return | Impact |\n"
        impact_md += "|---|---|---|---|---|---|\n"

        for i, (headline, returns) in enumerate(sorted_headlines[:10]):
            if returns and len(returns) > 0:
                avg_1d = returns.get('1d', 0) * 100
                avg_2d = returns.get('2d', 0) * 100
                avg_3d = returns.get('3d', 0) * 100

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

    def _advanced_news_headlines_markdown(self, good_news_analysis) -> str:
        forward_returns = good_news_analysis.forward_return_analysis if hasattr(good_news_analysis, 'forward_return_analysis') else {}
        if not forward_returns:
            return "No forward return analysis available"
        sorted_headlines = sorted(forward_returns.items(), key=lambda x: x[0], reverse=True)
        lines = []
        for i, (headline, returns) in enumerate(sorted_headlines[:10], 1):
            avg_1d = returns.get('1d', 0) * 100 if returns else 0
            avg_2d = returns.get('2d', 0) * 100 if returns else 0
            avg_3d = returns.get('3d', 0) * 100 if returns else 0
            lines.append(f"{i}. {headline} (1D {avg_1d:+.1f}%, 2D {avg_2d:+.1f}%, 3D {avg_3d:+.1f}%)")
        return "\n".join(lines)

    def _advanced_sentiment_breakdown_markdown(self, news_catalysts_data: Dict, good_news_analysis) -> str:
        total_catalysts = news_catalysts_data.get('total_headlines', 0)
        positive_catalysts = news_catalysts_data.get('positive_catalysts', 0)
        negative_catalysts = news_catalysts_data.get('negative_catalysts', 0)
        neutral_catalysts = news_catalysts_data.get('neutral_catalysts', 0)

        if total_catalysts > 0:
            positive_pct = (positive_catalysts / total_catalysts) * 100
            negative_pct = (negative_catalysts / total_catalysts) * 100
            neutral_pct = (neutral_catalysts / total_catalysts) * 100
        else:
            positive_pct = negative_pct = neutral_pct = 0
        failure_rate = getattr(good_news_analysis, 'failure_rate', 0)
        return (
            f"Total Articles: {total_catalysts}\n\n"
            f"Positive Articles: {positive_catalysts} ({positive_pct:.1f}%)\n"
            f"Negative Articles: {negative_catalysts} ({negative_pct:.1f}%)\n"
            f"Neutral Articles: {neutral_catalysts} ({neutral_pct:.1f}%)\n"
            f"Good News Success Rate: {100 - failure_rate:.1f}%\n"
        )
        
    def generate_html_report(self, reports: List[TickerReport], days: int) -> str:
        """Generate a comprehensive HTML report."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analysis Report - {timestamp}</title>
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
            border-bottom: 3px solid #007acc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #007acc;
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            color: #666;
            margin: 10px 0;
            font-size: 1.1em;
        }}
        .summary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 15px;
        }}
        .summary-item {{
            text-align: center;
        }}
        .summary-item .value {{
            font-size: 2em;
            font-weight: bold;
            display: block;
        }}
        .summary-item .label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .stock-section {{
            margin-bottom: 40px;
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }}
        .stock-header {{
            background: #007acc;
            color: white;
            padding: 20px;
            font-size: 1.3em;
            font-weight: bold;
        }}
        .stock-content {{
            padding: 20px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .metric {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }}
        .metric .value {{
            font-size: 1.4em;
            font-weight: bold;
            color: #007acc;
        }}
        .metric .label {{
            font-size: 0.8em;
            color: #666;
            margin-top: 5px;
        }}
        .positive {{ color: #28a745; }}
        .negative {{ color: #dc3545; }}
        .neutral {{ color: #6c757d; }}
        
        .news-section {{
            margin-top: 20px;
        }}
        .news-summary {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
        }}
        .headline {{
            border-left: 4px solid #007acc;
            padding: 10px 15px;
            margin-bottom: 10px;
            background: white;
        }}
        .headline-title {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .headline-meta {{
            font-size: 0.85em;
            color: #666;
        }}
        .categories {{
            display: inline-block;
            background: #e9ecef;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            margin-right: 5px;
        }}
        .impact-high {{ background: #dc3545; color: white; }}
        .impact-medium {{ background: #ffc107; color: black; }}
        .impact-low {{ background: #28a745; color: white; }}
        
        .notes {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
        }}
        .notes h4 {{
            margin-top: 0;
            color: #856404;
        }}
        .notes ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .chart-placeholder {{
            background: #f8f9fa;
            border: 2px dashed #dee2e6;
            height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #6c757d;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Stock Analysis Report</h1>
            <p>Generated on {timestamp}</p>
            <p>Analysis Period: {days} days | {len(reports)} tickers analyzed</p>
        </div>
        
        <div class="summary">
            <h2>Portfolio Summary</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <span class="value">{len(reports)}</span>
                    <span class="label">Stocks Analyzed</span>
                </div>
                <div class="summary-item">
                    <span class="value">{sum(1 for r in reports if r.combined_signal > 0)}</span>
                    <span class="label">Bullish Signals</span>
                </div>
                <div class="summary-item">
                    <span class="value">{sum(1 for r in reports if r.combined_signal < 0)}</span>
                    <span class="label">Bearish Signals</span>
                </div>
                <div class="summary-item">
                    <span class="value">{sum(len(r.headlines) for r in reports)}</span>
                    <span class="label">News Headlines</span>
                </div>
            </div>
        </div>
"""

        # Generate individual stock sections
        for report in reports:
            html_content += self._generate_stock_section(report)
        
        html_content += f"""
        <div class="footer">
            <p>Report generated by Stock Market Analyzer | Data sources: Yahoo Finance, Google News RSS</p>
            <p>This report is for informational purposes only and should not be considered as investment advice.</p>
        </div>
    </div>
</body>
</html>
"""
        return html_content
    
    def _generate_stock_section(self, report: TickerReport) -> str:
        """Generate HTML section for a single stock."""
        price = report.price
        signal_class = "positive" if report.combined_signal > 0 else "negative" if report.combined_signal < 0 else "neutral"
        
        # Calculate news statistics
        avg_quality = sum(h.quality for h in report.headlines) / len(report.headlines) if report.headlines else 0
        high_impact = sum(1 for h in report.headlines if h.impact == 2)
        categories = {}
        for h in report.headlines:
            for cat in h.categories:
                categories[cat] = categories.get(cat, 0) + 1
        
        html = f"""
        <div class="stock-section">
            <div class="stock-header">
                {report.ticker} - Combined Signal: <span class="{signal_class}">{report.combined_signal:+.2f}</span>
            </div>
            <div class="stock-content">
"""
        
        if price:
            html += f"""
                <div class="metrics-grid">
                    <div class="metric">
                        <div class="value">${price.last_close:.2f}</div>
                        <div class="label">Last Price</div>
                    </div>
                    <div class="metric">
                        <div class="value {'positive' if price.ret_5d > 0 else 'negative'}">{price.ret_5d:+.2%}</div>
                        <div class="label">5 Day Return</div>
                    </div>
                    <div class="metric">
                        <div class="value {'positive' if price.ret_21d > 0 else 'negative'}">{price.ret_21d:+.2%}</div>
                        <div class="label">21 Day Return</div>
                    </div>
                    <div class="metric">
                        <div class="value {'positive' if price.ret_63d > 0 else 'negative'}">{price.ret_63d:+.2%}</div>
                        <div class="label">63 Day Return</div>
                    </div>
                    <div class="metric">
                        <div class="value">{price.vol_21d_ann:.1%}</div>
                        <div class="label">Volatility (21d)</div>
                    </div>
                    <div class="metric">
                        <div class="value {'negative' if price.max_drawdown < -0.1 else 'neutral'}">{price.max_drawdown:.1%}</div>
                        <div class="label">Max Drawdown</div>
                    </div>
                    <div class="metric">
                        <div class="value">{price.rsi_14:.1f}</div>
                        <div class="label">RSI (14)</div>
                    </div>
                    <div class="metric">
                        <div class="value">{price.trend_50_200}</div>
                        <div class="label">Trend (50/200)</div>
                    </div>
                </div>
                
                <div class="chart-placeholder">
                    📊 Price Chart Placeholder (Integration with charting library needed)
                </div>
"""
        
        # News analysis section
        if report.headlines:
            html += f"""
                <div class="news-section">
                    <h3>News Analysis</h3>
                    <div class="news-summary">
                        <strong>{len(report.headlines)} headlines analyzed</strong> | 
                        Average Quality: {avg_quality:.2f} | 
                        High Impact: {high_impact} | 
                        Sentiment: {report.news_sentiment_total:+d} | 
                        Keyword Hits: {report.news_keyword_total}
                        <br>
                        Categories: {', '.join([f'{cat}({count})' for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]])}
                    </div>
"""
            
            # Top headlines
            for headline in report.headlines[:5]:
                impact_class = f"impact-{['low', 'medium', 'high'][headline.impact]}"
                cats_html = ' '.join([f'<span class="categories">{cat}</span>' for cat in list(headline.categories.keys())[:3]])
                
                html += f"""
                    <div class="headline">
                        <div class="headline-title">
                            <span class="{impact_class}">{['Low', 'Medium', 'High'][headline.impact]} Impact</span>
                            {headline.title}
                        </div>
                        <div class="headline-meta">
                            Sentiment: {headline.sentiment:+d} | 
                            Quality: {headline.quality:.2f} | 
                            {cats_html}
                            {f' | {headline.source}' if headline.source else ''}
                            {f' | {headline.published_ts[:10]}' if headline.published_ts else ''}
                        </div>
                    </div>
"""
            html += "</div>"
        
        # Notes section
        if report.notes:
            html += f"""
                <div class="notes">
                    <h4>📝 Analysis Notes</h4>
                    <ul>
                        {''.join([f'<li>{note}</li>' for note in report.notes])}
                    </ul>
                </div>
"""
        
        html += """
            </div>
        </div>
"""
        return html
    
    def generate_markdown_report(self, reports: List[TickerReport], days: int) -> str:
        """Generate a markdown report."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        
        md = f"""# Stock Analysis Report

**Generated:** {timestamp}  
**Analysis Period:** {days} days  
**Tickers:** {', '.join([r.ticker for r in reports])}

## Portfolio Summary

- **Stocks Analyzed:** {len(reports)}
- **Bullish Signals:** {sum(1 for r in reports if r.combined_signal > 0)}
- **Bearish Signals:** {sum(1 for r in reports if r.combined_signal < 0)}
- **Total Headlines:** {sum(len(r.headlines) for r in reports)}

---

"""
        
        # Sort by combined signal
        reports.sort(key=lambda r: r.combined_signal, reverse=True)
        
        for report in reports:
            md += self._generate_markdown_section(report)
        
        md += f"""
---

## Methodology

This report combines technical analysis with news sentiment analysis:

**Technical Indicators:**
- Price momentum (5d, 21d, 63d returns)
- Volatility and maximum drawdown
- RSI and moving average trends
- Volume analysis

**News Analysis:**
- Sentiment scoring using financial lexicon
- Keyword relevance detection
- Source quality assessment
- News categorization (earnings, products, M&A, etc.)
- Impact level assessment

**Combined Signal:**
Weighted scoring system that considers both technical and fundamental factors.

---

*Report generated by Stock Market Analyzer | Data sources: Yahoo Finance, Google News RSS*
*This report is for informational purposes only and should not be considered as investment advice.*
"""
        return md
    
    def _generate_markdown_section(self, report: TickerReport) -> str:
        """Generate markdown section for a single stock."""
        price = report.price
        signal_emoji = "📈" if report.combined_signal > 0 else "📉" if report.combined_signal < 0 else "➡️"
        
        md = f"""
## {signal_emoji} {report.ticker} - Combined Signal: {report.combined_signal:+.2f}

"""
        
        if price:
            md += f"""### Price Metrics

| Metric | Value |
|--------|-------|
| Last Price | ${price.last_close:.2f} |
| 5D Return | {price.ret_5d:+.2%} |
| 21D Return | {price.ret_21d:+.2%} |
| 63D Return | {price.ret_63d:+.2%} |
| Volatility (21d) | {price.vol_21d_ann:.1%} |
| Max Drawdown | {price.max_drawdown:.1%} |
| RSI (14) | {price.rsi_14:.1f} |
| Trend (50/200) | {price.trend_50_200} |

"""
        
        if report.headlines:
            avg_quality = sum(h.quality for h in report.headlines) / len(report.headlines)
            high_impact = sum(1 for h in report.headlines if h.impact == 2)
            categories = {}
            for h in report.headlines:
                for cat in h.categories:
                    categories[cat] = categories.get(cat, 0) + 1
            
            md += f"""### News Analysis

- **Headlines:** {len(report.headlines)}
- **Average Quality:** {avg_quality:.2f}
- **High Impact:** {high_impact}
- **Sentiment:** {report.news_sentiment_total:+d}
- **Keyword Hits:** {report.news_keyword_total}
- **Categories:** {', '.join([f'{cat}({count})' for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]])}

#### Top Headlines

"""
            for i, headline in enumerate(report.headlines[:5], 1):
                impact_str = ['Low', 'Medium', 'High'][headline.impact]
                cats_str = ', '.join(list(headline.categories.keys())[:3])
                md += f"{i}. **{impact_str} Impact** ({headline.sentiment:+d}, Q:{headline.quality:.2f}) [{cats_str}] {headline.title}\n"
                if headline.source:
                    md += f"   *Source: {headline.source}*\n"
                md += "\n"
        
        if report.notes:
            md += "### 📝 Analysis Notes\n\n"
            for note in report.notes:
                md += f"- {note}\n"
            md += "\n"
        
        md += "---\n\n"
        return md
    
    def save_report(self, content: str, filename: str):
        """Save report to file."""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(filepath)


def analyze_tickers(tickers: List[str], days: int, max_headlines: int = 25) -> List[TickerReport]:
    """Analyze multiple tickers and return reports."""
    keywords = ["AI", "HBM", "DRAM", "NAND", "capex", "guidance", "inventory", "datacenter", "chip", "foundry"]
    
    reports = []
    for ticker in tickers:
        print(f"Analyzing {ticker}...")
        
        # Fetch price data
        df = fetch_prices(ticker, days)
        price_summary = summarize_prices(ticker, df)
        
        # Fetch news
        headlines = fetch_headlines_for_ticker(
            ticker=ticker,
            max_items=max_headlines,
            keywords=keywords
        )
        
        # Calculate combined signal
        news_sent_total = sum(h.sentiment for h in headlines)
        news_kw_total = sum(h.keyword_score for h in headlines)
        combined_signal, notes = compute_combined_signal(price_summary, headlines)
        
        reports.append(TickerReport(
            ticker=ticker,
            price=price_summary,
            headlines=headlines,
            news_sentiment_total=news_sent_total,
            news_keyword_total=news_kw_total,
            combined_signal=combined_signal,
            notes=notes
        ))
    
    return reports


def main():
    parser = argparse.ArgumentParser(description="Generate comprehensive stock analysis reports")
    parser.add_argument("--tickers", nargs="+", required=True, help="Tickers to analyze")
    parser.add_argument("--days", type=int, default=180, help="Analysis period in days")
    parser.add_argument("--max-headlines", type=int, default=25, help="Max headlines per ticker")
    parser.add_argument("--output-dir", type=str, default="reports", help="Output directory for reports")
    parser.add_argument("--format", choices=["html", "markdown", "both"], default="both", help="Report format")
    
    args = parser.parse_args()
    
    # Initialize report generator
    generator = StockReportGenerator(args.output_dir)
    
    # Analyze tickers
    print(f"Analyzing {len(args.tickers)} tickers over {args.days} days...")
    reports = analyze_tickers(args.tickers, args.days, args.max_headlines)
    
    # Sort by combined signal
    reports.sort(key=lambda r: r.combined_signal, reverse=True)
    
    # Generate reports
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    if args.format in ["html", "both"]:
        print("Generating HTML report...")
        html_content = generator.generate_html_report(reports, args.days)
        html_path = generator.save_report(html_content, f"stock_report_{timestamp}.html")
        print(f"✅ HTML report saved: {html_path}")
    
    if args.format in ["markdown", "both"]:
        print("Generating Markdown report...")
        md_content = generator.generate_markdown_report(reports, args.days)
        md_path = generator.save_report(md_content, f"stock_report_{timestamp}.md")
        print(f"✅ Markdown report saved: {md_path}")
    
    # Print summary
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)
    for report in reports:
        signal_emoji = "📈" if report.combined_signal > 0 else "📉" if report.combined_signal < 0 else "➡️"
        print(f"{signal_emoji} {report.ticker:8} | Signal: {report.combined_signal:+7.2f} | News: {len(report.headlines):2d} headlines")
    print("="*60)


if __name__ == "__main__":
    main()
