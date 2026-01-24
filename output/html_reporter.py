from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

from domain.models import ReactionRecord
from output.graph_builder import GraphBuilder


class HTMLReporter:
    
    def __init__(self):
        self.graph_builder = GraphBuilder()
    
    def render_analysis_report(self, report_data: Dict[str, any], price_df: pd.DataFrame = None) -> str:
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Stock Analysis Report - {report_data['ticker']}</title>
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
        }}
        .section {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .section h2 {{
            color: #007bff;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 10px;
            margin: 5px 0;
            background: white;
            border-radius: 5px;
        }}
        .metric-label {{
            font-weight: bold;
            color: #666;
        }}
        .metric-value {{
            color: #333;
        }}
        .score {{
            font-size: 1.2em;
            font-weight: bold;
        }}
        .score.opportunity {{
            color: #28a745;
        }}
        .score.sell-risk {{
            color: #dc3545;
        }}
        .positive {{
            color: #28a745;
        }}
        .negative {{
            color: #dc3545;
        }}
        .recommendation {{
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            font-size: 1.5em;
            font-weight: bold;
            margin: 20px 0;
        }}
        .recommendation.buy {{
            background: #d4edda;
            color: #155724;
            border: 2px solid #28a745;
        }}
        .recommendation.sell {{
            background: #f8d7da;
            color: #721c24;
            border: 2px solid #dc3545;
        }}
        .recommendation.hold {{
            background: #fff3cd;
            color: #856404;
            border: 2px solid #ffc107;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #007bff;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .reasons ul {{
            list-style-type: none;
            padding: 0;
        }}
        .reasons li {{
            padding: 10px;
            margin: 5px 0;
            background: white;
            border-left: 4px solid #007bff;
            border-radius: 4px;
        }}
        .levels .level {{
            padding: 8px;
            margin: 5px 0;
            background: white;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Advanced Stock Analysis Report</h1>
            <p>{report_data['ticker']} Analysis</p>
            <p>Generated: {report_data['timestamp']}</p>
            <p>Regime: <strong>{report_data['regime'].upper()}</strong></p>
        </div>
        
        <div class="section">
            <h2>📊 Signal Scores</h2>
            <div class="metric">
                <span class="metric-label">Opportunity Score:</span>
                <span class="score opportunity">{report_data['signal_scores']['opportunity']:.1f}/100</span>
            </div>
            <div class="metric">
                <span class="metric-label">Sell-Risk Score:</span>
                <span class="score sell-risk">{report_data['signal_scores']['sell_risk']:.1f}/100</span>
            </div>
            <div class="metric">
                <span class="metric-label">Overall Bias:</span>
                <span class="metric-value">{report_data['signal_scores']['bias'].upper()}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Confidence:</span>
                <span class="metric-value">{report_data['signal_scores']['confidence'].upper()}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Recommendation</h2>
            <div class="recommendation {self._get_recommendation_class(report_data['recommendation']['action'])}">
                {report_data['recommendation']['action'].upper()}
            </div>
            <div class="metric">
                <span class="metric-label">Confidence:</span>
                <span class="metric-value">{report_data['recommendation']['confidence']:.1%}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Urgency:</span>
                <span class="metric-value">{report_data['recommendation'].get('urgency', 'normal').upper()}</span>
            </div>
            {self._render_tier(report_data['recommendation'])}            
            <h3>💡 Key Reasons:</h3>
            <div class="reasons">
                <ul>
"""
        
        for reason in report_data['recommendation']['reasons'][:5]:
            html += f"                    <li>{reason}</li>\n"
        
        html += """                </ul>
            </div>
        </div>
"""
        
        if report_data['recommendation'].get('key_levels'):
            html += """
        <div class="section">
            <h2>📍 Key Levels</h2>
            <div class="levels">
"""
            for level_type, level_value in report_data['recommendation']['key_levels'].items():
                if level_value and level_value != 0.0:
                    html += f"""                <div class="level"><strong>{level_type.replace('_', ' ').title()}:</strong> ${level_value:.2f}</div>\n"""
            html += """            </div>
        </div>
"""
        
        # Charts Section
        if price_df is not None and not price_df.empty and self.graph_builder.is_available():
            html += """
        <div class="section">
            <h2>📊 Price Charts</h2>
            <div style="display: grid; gap: 20px;">
"""
            # Combined chart
            combined_chart = self.graph_builder.create_combined_chart(
                price_df, report_data['ticker'], days=90
            )
            if combined_chart:
                html += f"""
                <div>
                    {self.graph_builder.embed_in_html(combined_chart, "Technical Analysis Chart")}
                </div>
"""
            html += """
            </div>
        </div>
"""
        
        html += """
        <div class="section">
            <h2>📈 Technical Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Indicator</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for key, value in report_data.get('technical_summary', {}).items():
            if isinstance(value, float):
                html += f"                    <tr><td>{key.replace('_', ' ').title()}</td><td>{value:.4f}</td></tr>\n"
            else:
                html += f"                    <tr><td>{key.replace('_', ' ').title()}</td><td>{value}</td></tr>\n"
        
        html += """                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>📰 News Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for key, value in report_data.get('news_summary', {}).items():
            if isinstance(value, float):
                html += f"                    <tr><td>{key.replace('_', ' ').title()}</td><td>{value:.4f}</td></tr>\n"
            else:
                html += f"                    <tr><td>{key.replace('_', ' ').title()}</td><td>{value}</td></tr>\n"
        
        html += """                </tbody>
            </table>
        </div>
"""
        
        # Add news articles section
        if report_data.get('news_events'):
            num_articles = len(report_data['news_events'])
            html += f"""
        <div class="section">
            <h2>📰 Recent News Articles ({num_articles} articles)</h2>
            <table>
                <thead>
                    <tr>
                        <th style="width: 45%;">Headline</th>
                        <th>Published</th>
                        <th>Source</th>
                        <th>Sentiment</th>
                        <th>Price Change</th>
                        <th>Quality</th>
                    </tr>
                </thead>
                <tbody>
"""
            for event in report_data['news_events']:
                sentiment_label = event['sentiment']
                sentiment_color = '#28a745' if sentiment_label == 'Positive' else '#dc3545' if sentiment_label == 'Negative' else '#6c757d'
                sentiment_emoji = '📈' if sentiment_label == 'Positive' else '📉' if sentiment_label == 'Negative' else '➡️'
                quality_color = '#28a745' if event['quality'] > 0.7 else '#ffc107' if event['quality'] > 0.4 else '#6c757d'
                
                # Format price change if available (for articles > 1 day old)
                price_change_display = "-"
                if event.get('price_change') is not None:
                    price_change = event['price_change']
                    change_color = '#28a745' if price_change > 0 else '#dc3545' if price_change < 0 else '#6c757d'
                    change_emoji = '🟢' if price_change > 0 else '🔴' if price_change < 0 else '⚪'
                    price_change_display = f'<span style="color: {change_color}; font-weight: bold;">{change_emoji} {price_change:+.2f}%</span>'
                
                html += f"""
                    <tr>
                        <td><a href="{event['url']}" target="_blank" style="color: #007bff; text-decoration: none;">{event['title']}</a></td>
                        <td style="white-space: nowrap;">{event['published_ts']}</td>
                        <td>{event['source']}</td>
                        <td style="color: {sentiment_color}; font-weight: bold;">{sentiment_emoji} {sentiment_label}</td>
                        <td style="text-align: center;">{price_change_display}</td>
                        <td style="color: {quality_color};">{event['quality']:.2f}</td>
                    </tr>
"""
            
            html += """                </tbody>
            </table>
            <p style="font-size: 0.9em; color: #6c757d; margin-top: 10px;">* Price change shown for articles published more than 1 day ago</p>
        </div>
"""
        
        # Add weekly news metrics section
        if report_data.get('news_weekly_metrics') and report_data['news_weekly_metrics'].get('weeks'):
            weekly_metrics = report_data['news_weekly_metrics']
            html += """
        <div class="section">
            <h2>📈 Weekly News Trends (Last 4 Weeks)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Week</th>
                        <th>Period</th>
                        <th>Total</th>
                        <th>Positive</th>
                        <th>Negative</th>
                        <th>Neutral</th>
                        <th>Sentiment Balance</th>
                        <th>Avg Quality</th>
                        <th>Price Change</th>
                        <th>RSI</th>
                    </tr>
                </thead>
                <tbody>
"""
            
            for week in weekly_metrics['weeks']:
                balance = week['sentiment_balance']
                balance_color = '#28a745' if balance > 0 else '#dc3545' if balance < 0 else '#6c757d'
                balance_emoji = '📈' if balance > 0 else '📉' if balance < 0 else '➡️'
                quality_color = '#28a745' if week['avg_quality'] > 0.7 else '#ffc107' if week['avg_quality'] > 0.4 else '#6c757d'
                
                # Format price change
                price_change_str = "-"
                price_change_color = "#6c757d"
                if week.get('price_change') is not None:
                    pc = week['price_change']
                    price_change_emoji = '📈' if pc > 0 else '📉' if pc < 0 else '➡️'
                    price_change_color = '#28a745' if pc > 0 else '#dc3545' if pc < 0 else '#6c757d'
                    price_change_str = f"{price_change_emoji} {pc:+.2f}%"
                
                # Format RSI
                rsi_str = "-"
                rsi_color = "#6c757d"
                if week.get('rsi') is not None:
                    rsi = week['rsi']
                    if rsi > 70:
                        rsi_color = '#dc3545'  # Overbought - red
                    elif rsi < 30:
                        rsi_color = '#28a745'  # Oversold - green
                    else:
                        rsi_color = '#ffc107'  # Neutral - yellow
                    rsi_str = f"{rsi:.1f}"
                
                html += f"""
                    <tr>
                        <td><strong>{week['week_label']}</strong></td>
                        <td style="font-size: 0.85em;">{week['week_start']} to {week['week_end']}</td>
                        <td style="text-align: center; font-weight: bold;">{week['total_count']}</td>
                        <td style="text-align: center; color: #28a745;">{week['positive_count']}</td>
                        <td style="text-align: center; color: #dc3545;">{week['negative_count']}</td>
                        <td style="text-align: center; color: #6c757d;">{week['neutral_count']}</td>
                        <td style="text-align: center; color: {balance_color}; font-weight: bold;">{balance_emoji} {balance:+d}</td>
                        <td style="text-align: center; color: {quality_color};">{week['avg_quality']:.2f}</td>
                        <td style="color: {price_change_color};"><strong>{price_change_str}</strong></td>
                        <td style="color: {rsi_color};"><strong>{rsi_str}</strong></td>
                    </tr>
"""
            
            html += """                </tbody>
            </table>
            
            <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px;">
                <h3 style="margin-top: 0;">Week-over-Week Changes</h3>
"""
            
            wow = weekly_metrics['week_over_week']
            total_change = wow['total_change']
            positive_change = wow['positive_change']
            negative_change = wow['negative_change']
            sentiment_change = wow['sentiment_change']
            
            total_color = '#28a745' if total_change > 0 else '#dc3545' if total_change < 0 else '#6c757d'
            pos_color = '#28a745' if positive_change > 0 else '#dc3545' if positive_change < 0 else '#6c757d'
            neg_color = '#dc3545' if negative_change > 0 else '#28a745' if negative_change < 0 else '#6c757d'
            sent_color = '#28a745' if sentiment_change > 0 else '#dc3545' if sentiment_change < 0 else '#6c757d'
            
            html += f"""
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px;">
                    <div>
                        <div style="font-size: 0.9em; color: #6c757d;">Total Articles</div>
                        <div style="font-size: 1.5em; font-weight: bold; color: {total_color};">{total_change:+d}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.9em; color: #6c757d;">Positive</div>
                        <div style="font-size: 1.5em; font-weight: bold; color: {pos_color};">{positive_change:+d}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.9em; color: #6c757d;">Negative</div>
                        <div style="font-size: 1.5em; font-weight: bold; color: {neg_color};">{negative_change:+d}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.9em; color: #6c757d;">Avg Sentiment</div>
                        <div style="font-size: 1.5em; font-weight: bold; color: {sent_color};">{sentiment_change:+.3f}</div>
                    </div>
                </div>
            </div>
        </div>
"""
        
        if report_data.get('semiconductor_analysis'):
            semi = report_data['semiconductor_analysis']
            rsi_data = semi['rsi_analysis']
            html += f"""
        <div class="section">
            <h2>🔴 Semiconductor Cycle Risk Analysis</h2>
            <div class="metric">
                <span class="metric-label">Stock Type:</span>
                <span class="metric-value">{'Memory Stock' if semi['is_memory_stock'] else 'Non-Memory Semiconductor'}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Cycle Risk Score:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#dc3545' if semi['cycle_risk_score'] >= 30 else '#ffc107' if semi['cycle_risk_score'] >= 15 else '#28a745'};">{semi['cycle_risk_score']} ({semi['risk_level'].upper()})</span>
            </div>
            
            <h3>📊 RSI Trend Analysis (Past 8 Weeks)</h3>
            <div class="metric">
                <span class="metric-label">Current RSI:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#dc3545' if rsi_data.evidence.get('current_rsi', 50) > 75 else '#28a745' if rsi_data.evidence.get('current_rsi', 50) < 25 else '#333'};">{rsi_data.evidence.get('current_rsi', 50):.1f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">RSI Trend:</span>
                <span class="metric-value">{rsi_data.evidence.get('trend_direction', 'neutral').upper()}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Weeks Above 75:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#dc3545' if rsi_data.evidence.get('weeks_above_75', 0) >= 2 else '#333'};">{rsi_data.evidence.get('weeks_above_75', 0)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Risk Points:</span>
                <span class="metric-value">{rsi_data.risk_points}</span>
            </div>
            
            <h3>📊 Position vs 20-Day High (Exhaustion Signal)</h3>
            <div class="metric">
                <span class="metric-label">Current Position:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#dc3545' if semi['exhaustion_analysis'].evidence.get('position_vs_20d_high', 0) > 0.98 else '#333'};">{semi['exhaustion_analysis'].evidence.get('position_vs_20d_high', 0):.1%}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Days Above 98%:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#dc3545' if semi['exhaustion_analysis'].evidence.get('days_above_threshold', 0) >= 10 else '#ffc107' if semi['exhaustion_analysis'].evidence.get('days_above_threshold', 0) >= 5 else '#333'};">{semi['exhaustion_analysis'].evidence.get('days_above_threshold', 0)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Exhaustion Status:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#dc3545' if semi['exhaustion_analysis'].evidence.get('is_exhausted', False) else '#28a745'};">{'EXHAUSTED' if semi['exhaustion_analysis'].evidence.get('is_exhausted', False) else 'NORMAL'}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Exhaustion Risk Points:</span>
                <span class="metric-value">{semi['exhaustion_analysis'].risk_points}</span>
            </div>
"""
            
            if semi['exhaustion_analysis'].alert:
                alert_color = '#dc3545' if '🔴' in semi['exhaustion_analysis'].alert else '#ffc107'
                html += f"""
            <div style="background: {alert_color}20; border-left: 4px solid {alert_color}; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <strong>{semi['exhaustion_analysis'].alert}</strong>
            </div>
"""
            
            html += f"""
            
            <h3>📉 RSI Divergence (Early Momentum Decay)</h3>
            <div class="metric">
                <span class="metric-label">Divergence Type:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#dc3545' if semi['divergence_analysis'].evidence.get('divergence_type') == 'bearish' else '#28a745' if semi['divergence_analysis'].evidence.get('divergence_type') == 'bullish' else '#333'};">{semi['divergence_analysis'].evidence.get('divergence_type', 'none').upper() if semi['divergence_analysis'].evidence.get('divergence_type') != 'none' else 'NONE DETECTED'}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Bearish Divergence:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#dc3545' if semi['divergence_analysis'].evidence.get('divergence_type') == 'bearish' else '#28a745'};">{'YES - Smart money leaving' if semi['divergence_analysis'].evidence.get('divergence_type') == 'bearish' else 'NO'}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Bullish Divergence:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#28a745' if semi['divergence_analysis'].evidence.get('divergence_type') == 'bullish' else '#333'};">{'YES - Potential reversal' if semi['divergence_analysis'].evidence.get('divergence_type') == 'bullish' else 'NO'}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Divergence Risk Points:</span>
                <span class="metric-value">{semi['divergence_analysis'].risk_points}</span>
            </div>
"""
            
            if semi['divergence_analysis'].alert:
                alert_color = '#dc3545' if '🔴' in semi['divergence_analysis'].alert else '#28a745'
                html += f"""
            <div style="background: {alert_color}20; border-left: 4px solid {alert_color}; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <strong>{semi['divergence_analysis'].alert}</strong>
            </div>
"""
            
            html += f"""
            
            <h3>📉 ROC Compression (Cycle Aging)</h3>
            <div class="metric">
                <span class="metric-label">Compression Status:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#dc3545' if semi['roc_compression_analysis'].evidence.get('severity') in ['severe', 'moderate', 'mild'] else '#28a745'};">{semi['roc_compression_analysis'].evidence.get('severity', 'none').upper()}</span>
            </div>
"""
            
            if semi['roc_compression_analysis'].evidence.get('current_roc'):
                html += """            <h4>Current ROC vs Baseline:</h4>
            <div style="background: white; padding: 10px; border-radius: 5px;">
"""
                for period_key, current_val in semi['roc_compression_analysis'].evidence.get('current_roc', {}).items():
                    period_label = period_key.replace('roc_', '').replace('d', 'D')
                    early_val = semi['roc_compression_analysis'].evidence.get('baseline_roc', {}).get(period_key, 0)
                    ratio = semi['roc_compression_analysis'].evidence.get('compression_ratio', {}).get(period_key, 0)
                    
                    color = '#dc3545' if ratio < 0.5 else '#ffc107' if ratio < 0.8 else '#28a745'
                    html += f"""                <div class="metric">
                    <span class="metric-label">{period_label}:</span>
                    <span class="metric-value">Current: {current_val:.2f}% | Baseline: {early_val:.2f}% | Ratio: <span style="color: {color}; font-weight: bold;">{ratio:.2f}</span></span>
                </div>
"""
                html += """            </div>
"""
            
            html += f"""
            <div class="metric">
                <span class="metric-label">ROC Risk Points:</span>
                <span class="metric-value">{semi['roc_compression_analysis'].risk_points}</span>
            </div>
"""
            
            if semi['roc_compression_analysis'].alert:
                alert_color = '#dc3545' if '🔴' in semi['roc_compression_analysis'].alert else '#ffc107'
                html += f"""
            <div style="background: {alert_color}20; border-left: 4px solid {alert_color}; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <strong>{semi['roc_compression_analysis'].alert}</strong>
            </div>
"""
            
            html += f"""
            
            <h3>💚 RSI 55-70 Zone (Institutional Accumulation Band)</h3>
            <div class="metric">
                <span class="metric-label">Trend Health:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#28a745' if semi['accumulation_zone_analysis'].evidence.get('trend_health') == 'healthy' else '#dc3545' if semi['accumulation_zone_analysis'].evidence.get('trend_health') in ['broken', 'overheated'] else '#ffc107'};">{semi['accumulation_zone_analysis'].evidence.get('trend_health', 'unknown').upper()}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Current RSI:</span>
                <span class="metric-value">{semi['accumulation_zone_analysis'].evidence.get('current_rsi', 50):.1f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Zone Visits (Last 20D):</span>
                <span class="metric-value">{semi['accumulation_zone_analysis'].evidence.get('zone_visits_last_20d', 0)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Days Since Zone:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#dc3545' if semi['accumulation_zone_analysis'].evidence.get('days_since_zone', 0) > 15 else '#ffc107' if semi['accumulation_zone_analysis'].evidence.get('days_since_zone', 0) > 10 else '#28a745'};">{semi['accumulation_zone_analysis'].evidence.get('days_since_zone', 0)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Zone Risk Points:</span>
                <span class="metric-value">{semi['accumulation_zone_analysis'].risk_points}</span>
            </div>
"""
            
            if semi['accumulation_zone_analysis'].alert:
                alert_color = '#28a745' if '💚' in semi['accumulation_zone_analysis'].alert or '✅' in semi['accumulation_zone_analysis'].alert else '#dc3545' if '🔴' in semi['accumulation_zone_analysis'].alert else '#ffc107'
                html += f"""
            <div style="background: {alert_color}20; border-left: 4px solid {alert_color}; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <strong>{semi['accumulation_zone_analysis'].alert}</strong>
            </div>
"""
            
            html += f"""
            
            <h3>📊 Trend Persistence (% Time Above 50DMA)</h3>
            <div class="metric">
                <span class="metric-label">Trend Strength:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#28a745' if semi['trend_persistence_analysis'].evidence.get('trend_strength') == 'strong' else '#dc3545' if semi['trend_persistence_analysis'].evidence.get('trend_strength') in ['broken', 'weak'] else '#ffc107'};">{semi['trend_persistence_analysis'].evidence.get('trend_strength', 'unknown').upper()}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Persistence Declining:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#dc3545' if semi['trend_persistence_analysis'].evidence.get('persistence_declining', False) else '#28a745'};">{('YES - Internal Erosion' if semi['trend_persistence_analysis'].evidence.get('persistence_declining', False) else 'NO')}</span>
            </div>
"""
            
            if semi['trend_persistence_analysis'].evidence.get('pct_above_50dma'):
                html += """            <h4>% Time Above 50DMA:</h4>
            <div style="background: white; padding: 10px; border-radius: 5px;">
"""
                for period_key, pct_val in semi['trend_persistence_analysis'].evidence.get('pct_above_50dma', {}).items():
                    period_label = period_key.replace('d', 'D')
                    color = '#28a745' if pct_val >= 80 else '#ffc107' if pct_val >= 60 else '#dc3545'
                    html += f"""                <div class="metric">
                    <span class="metric-label">{period_label}:</span>
                    <span class="metric-value" style="color: {color}; font-weight: bold;">{pct_val:.1f}%</span>
                </div>
"""
                html += """            </div>
"""
            
            html += f"""
            <div class="metric">
                <span class="metric-label">Persistence Risk Points:</span>
                <span class="metric-value">{semi['trend_persistence_analysis'].risk_points}</span>
            </div>
"""
            
            if semi['trend_persistence_analysis'].alert:
                alert_color = '#28a745' if '💚' in semi['trend_persistence_analysis'].alert else '#dc3545' if '🔴' in semi['trend_persistence_analysis'].alert else '#ffc107'
                html += f"""
            <div style="background: {alert_color}20; border-left: 4px solid {alert_color}; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <strong>{semi['trend_persistence_analysis'].alert}</strong>
            </div>
"""
            
            html += f"""
            
            <h3>🔴 First 50DMA Failure (Cycle Turn Trigger)</h3>
            <div class="metric">
                <span class="metric-label">Currently Below 50DMA:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#dc3545' if semi['dma_failure_analysis'].evidence.get('currently_below_50dma', False) else '#28a745'};">{('YES' if semi['dma_failure_analysis'].evidence.get('currently_below_50dma', False) else 'NO')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">First Failure After Long Uptrend:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#dc3545' if semi['dma_failure_analysis'].evidence.get('is_first_failure', False) else '#28a745'};">{('YES - Cycle Turn' if semi['dma_failure_analysis'].evidence.get('is_first_failure', False) else 'NO')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Previous Uptrend Days:</span>
                <span class="metric-value">{semi['dma_failure_analysis'].evidence.get('previous_uptrend_days', 0)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Days in Current Streak:</span>
                <span class="metric-value">{semi['dma_failure_analysis'].evidence.get('days_in_current_streak', 0)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Failure Severity:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#dc3545' if semi['dma_failure_analysis'].evidence.get('failure_severity') in ['critical', 'severe'] else '#ffc107' if semi['dma_failure_analysis'].evidence.get('failure_severity') == 'significant' else '#28a745'};">{semi['dma_failure_analysis'].evidence.get('failure_severity', 'none').upper()}</span>
            </div>
            <div class="metric">
                <span class="metric-label">50DMA Failure Risk Points:</span>
                <span class="metric-value">{semi['dma_failure_analysis'].risk_points}</span>
            </div>
"""
            
            if semi['dma_failure_analysis'].alert:
                alert_color = '#dc3545'
                html += f"""
            <div style="background: {alert_color}20; border-left: 4px solid {alert_color}; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <strong>{semi['dma_failure_analysis'].alert}</strong>
            </div>
"""
            
            html += f"""
            
            <h3>📊 ATR Expansion (Distribution Signature)</h3>
            <div class="metric">
                <span class="metric-label">ATR (14-day):</span>
                <span class="metric-value">${semi['atr_expansion_analysis'].evidence.get('atr_14', 0):.2f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">ATR % of Price:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#dc3545' if semi['atr_expansion_analysis'].evidence.get('atr_pct_price', 0) > 6.0 else '#ffc107' if semi['atr_expansion_analysis'].evidence.get('atr_pct_price', 0) > 4.0 else '#28a745'};">{semi['atr_expansion_analysis'].evidence.get('atr_pct_price', 0):.2f}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">ATR Z-Score:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#dc3545' if semi['atr_expansion_analysis'].evidence.get('atr_zscore_60d', 0) > 1.5 else '#28a745'};">{semi['atr_expansion_analysis'].evidence.get('atr_zscore_60d', 0):.2f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Position vs 20D High:</span>
                <span class="metric-value">{semi['atr_expansion_analysis'].evidence.get('near_highs', 0):.1%}</span>
            </div>
            <div class="metric">
                <span class="metric-label">ATR Risk Points:</span>
                <span class="metric-value">{semi['atr_expansion_analysis'].risk_points}</span>
            </div>
"""
            
            if semi['atr_expansion_analysis'].alert:
                alert_color = '#28a745' if '💚' in semi['atr_expansion_analysis'].alert else '#dc3545' if '🔴' in semi['atr_expansion_analysis'].alert else '#ffc107'
                html += f"""
            <div style="background: {alert_color}20; border-left: 4px solid {alert_color}; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <strong>{semi['atr_expansion_analysis'].alert}</strong>
            </div>
"""
            
            html += f"""
            
            <h3>📏 MA Extension (Rubber-Band Risk)</h3>
            <div class="metric">
                <span class="metric-label">Extension Level:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#dc3545' if semi['ma_extension_analysis'].evidence.get('extension_level') == 'extreme' else '#ffc107' if semi['ma_extension_analysis'].evidence.get('extension_level') in ['elevated', 'moderate'] else '#28a745'};">{semi['ma_extension_analysis'].evidence.get('extension_level', 'unknown').upper()}</span>
            </div>
            <div class="metric">
                <span class="metric-label">% Above 21DMA:</span>
                <span class="metric-value">{f"{semi['ma_extension_analysis'].evidence.get('pct_above_21dma'):.1f}%" if semi['ma_extension_analysis'].evidence.get('pct_above_21dma') is not None else 'N/A'}</span>
            </div>
            <div class="metric">
                <span class="metric-label">% Above 50DMA:</span>
                <span class="metric-value" style="font-weight: bold;">{f"{semi['ma_extension_analysis'].evidence.get('pct_above_50dma'):.1f}%" if semi['ma_extension_analysis'].evidence.get('pct_above_50dma') is not None else 'N/A'}</span>
            </div>
            <div class="metric">
                <span class="metric-label">% Above 200DMA:</span>
                <span class="metric-value">{f"{semi['ma_extension_analysis'].evidence.get('pct_above_200dma'):.1f}%" if semi['ma_extension_analysis'].evidence.get('pct_above_200dma') is not None else 'N/A'}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Extension Risk Points:</span>
                <span class="metric-value">{semi['ma_extension_analysis'].risk_points}</span>
            </div>
"""
            
            if semi['ma_extension_analysis'].alert:
                alert_color = '#28a745' if '💚' in semi['ma_extension_analysis'].alert else '#dc3545' if '🔴' in semi['ma_extension_analysis'].alert else '#ffc107'
                html += f"""
            <div style="background: {alert_color}20; border-left: 4px solid {alert_color}; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <strong>{semi['ma_extension_analysis'].alert}</strong>
            </div>
"""
            
            html += f"""
            
            <h3>📈 Volatility Regime (Two-Way Trade Detector)</h3>
            <div class="metric">
                <span class="metric-label">Vol Regime:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#dc3545' if semi['vol_regime_analysis'].evidence.get('regime') == 'high' else '#ffc107' if 'medium' in semi['vol_regime_analysis'].evidence.get('regime', '') else '#28a745'};">{semi['vol_regime_analysis'].evidence.get('regime', 'unknown').upper()}</span>
            </div>
            <div class="metric">
                <span class="metric-label">20D Annualized Vol:</span>
                <span class="metric-value">{semi['vol_regime_analysis'].evidence.get('vol_20_ann', 0):.1f}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Baseline Vol:</span>
                <span class="metric-value">{semi['vol_regime_analysis'].evidence.get('vol_baseline_120', 0):.1f}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Vol Ratio:</span>
                <span class="metric-value" style="font-weight: bold; color: {'#dc3545' if semi['vol_regime_analysis'].evidence.get('vol_ratio', 0) >= 1.3 else '#ffc107' if semi['vol_regime_analysis'].evidence.get('vol_ratio', 0) >= 1.1 else '#28a745'};">{semi['vol_regime_analysis'].evidence.get('vol_ratio', 0):.2f}x</span>
            </div>
            <div class="metric">
                <span class="metric-label">Vol Risk Points:</span>
                <span class="metric-value">{semi['vol_regime_analysis'].risk_points}</span>
            </div>
"""
            
            if semi['vol_regime_analysis'].alert:
                alert_color = '#28a745' if '💚' in semi['vol_regime_analysis'].alert else '#dc3545' if '🔴' in semi['vol_regime_analysis'].alert else '#ffc107'
                html += f"""
            <div style="background: {alert_color}20; border-left: 4px solid {alert_color}; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <strong>{semi['vol_regime_analysis'].alert}</strong>
            </div>
"""
            
            html += """
"""
            
            if rsi_data.evidence.get('weekly_rsi'):
                html += """            <h4>Weekly RSI Values:</h4>
            <div style="background: white; padding: 10px; border-radius: 5px; font-family: monospace;">
"""
                for i, val in enumerate(rsi_data.evidence.get('weekly_rsi', []), 1):
                    color = '#dc3545' if val > 75 else '#28a745' if val < 25 else '#333'
                    html += f"                Week {i}: <span style='color: {color}; font-weight: bold;'>{val:.1f}</span><br>\n"
                html += """            </div>
"""
            
            if rsi_data.alert:
                alert_color = '#dc3545' if '🔴' in rsi_data.alert else '#ffc107'
                html += f"""
            <div style="background: {alert_color}20; border-left: 4px solid {alert_color}; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <strong>{rsi_data.alert}</strong>
            </div>
"""
            
            if semi.get('recommendations'):
                html += """            <h4>💡 Cycle-Based Recommendations:</h4>
            <ul style="background: white; padding: 15px; border-radius: 5px;">
"""
                for rec in semi['recommendations']:
                    html += f"                <li>{rec}</li>\n"
                html += """            </ul>
"""
            
            html += """        </div>
"""
        
        # Mining Stock Analysis Section
        if report_data.get('mining_stock_analysis'):
            mining = report_data['mining_stock_analysis']
            stock_info = mining['stock_info']
            momentum = mining['momentum']
            semi_demand = mining['semi_demand']
            composite = mining['composite']
            
            # Sensitivity icon
            sensitivity_icons = {
                "Very High": "🔥🔥",
                "High": "🔥",
                "Medium": "🟡",
                "Low": "🔴",
            }
            sens_icon = sensitivity_icons.get(stock_info['semi_sensitivity'], "")
            
            # Direction color
            direction_colors = {
                "bullish": "#28a745",
                "bearish": "#dc3545",
                "neutral": "#6c757d",
            }
            
            html += f"""
        <div class="section" style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white;">
            <h2 style="color: #ffc107;">⛏️ Mining Stock Analysis - {stock_info['name']}</h2>
            
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 20px;">
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px;">
                    <h4 style="color: #ffc107; margin-top: 0;">Stock Info</h4>
                    <div class="metric">
                        <span class="metric-label" style="color: #ccc;">Mineral:</span>
                        <span class="metric-value" style="color: white;">{stock_info['mineral']}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label" style="color: #ccc;">Semi Sensitivity:</span>
                        <span class="metric-value" style="color: white;">{sens_icon} {stock_info['semi_sensitivity']}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label" style="color: #ccc;">Exposure:</span>
                        <span class="metric-value" style="color: white; font-size: 0.9em;">{stock_info['primary_exposure']}</span>
                    </div>
                </div>
                
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px;">
                    <h4 style="color: #ffc107; margin-top: 0;">Price Momentum</h4>
                    <div class="metric">
                        <span class="metric-label" style="color: #ccc;">Current Price:</span>
                        <span class="metric-value" style="color: white;">${momentum['current_price']:.2f}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label" style="color: #ccc;">RSI:</span>
                        <span class="metric-value" style="color: {'#dc3545' if momentum['rsi'] > 70 else '#28a745' if momentum['rsi'] < 30 else 'white'};">{momentum['rsi']:.1f}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label" style="color: #ccc;">Trend:</span>
                        <span class="metric-value" style="color: white;">{momentum['trend'].replace('_', ' ').title()}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label" style="color: #ccc;">vs MA20:</span>
                        <span class="metric-value" style="color: {'#28a745' if momentum['vs_ma20_pct'] > 0 else '#dc3545'};">{momentum['vs_ma20_pct']:+.1f}%</span>
                    </div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px;">
                    <h4 style="color: #ffc107; margin-top: 0;">Semi Demand Score</h4>
                    <div style="text-align: center; margin: 15px 0;">
                        <div style="font-size: 2.5em; font-weight: bold; color: {'#28a745' if semi_demand['score'] >= 60 else '#ffc107' if semi_demand['score'] >= 40 else '#dc3545'};">
                            {semi_demand['score']:.0f}/100
                        </div>
                        <div style="color: #ccc;">Semiconductor Demand Score</div>
                    </div>
                    <div class="metric">
                        <span class="metric-label" style="color: #ccc;">Direction:</span>
                        <span class="metric-value" style="color: {direction_colors.get(semi_demand['direction'], 'white')};">{semi_demand['direction'].upper()}</span>
                    </div>
                </div>
                
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px;">
                    <h4 style="color: #ffc107; margin-top: 0;">Composite Signal</h4>
                    <div style="text-align: center; margin: 15px 0;">
                        <div style="font-size: 1.8em; font-weight: bold; color: {'#28a745' if 'BUY' in composite['overall_direction'] else '#dc3545' if 'SELL' in composite['overall_direction'] else '#ffc107'};">
                            {composite['overall_direction']}
                        </div>
                        <div style="color: #ccc;">Net Signal: {composite['net_signal']:+d}</div>
                    </div>
                    <div class="metric">
                        <span class="metric-label" style="color: #ccc;">Risk Points:</span>
                        <span class="metric-value" style="color: #dc3545;">{composite['total_risk_points']}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label" style="color: #ccc;">Opportunity Points:</span>
                        <span class="metric-value" style="color: #28a745;">{composite['total_opportunity_points']}</span>
                    </div>
                </div>
            </div>
"""
            
            # Alerts
            if composite.get('alerts'):
                html += """
            <div style="margin-top: 20px;">
                <h4 style="color: #ffc107;">⚠️ Alerts</h4>
"""
                for alert in composite['alerts']:
                    html += f"""
                <div style="background: rgba(255,193,7,0.2); border-left: 4px solid #ffc107; padding: 10px 15px; margin: 10px 0; border-radius: 0 5px 5px 0;">
                    {alert}
                </div>
"""
                html += """
            </div>
"""
            
            # Key Assets
            if stock_info.get('key_assets'):
                html += f"""
            <div style="margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 5px;">
                <strong style="color: #ffc107;">Key Assets:</strong> 
                <span style="color: #ccc;">{', '.join(stock_info['key_assets'])}</span>
            </div>
"""
            
            html += """
        </div>
"""
        
        if report_data.get('reaction_summary', {}).get('count', 0) > 0:
            html += f"""
        <div class="section">
            <h2>📊 News Reaction Analysis</h2>
            <div class="metric">
                <span class="metric-label">Total Reactions Analyzed:</span>
                <span class="metric-value">{report_data['reaction_summary']['count']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Worked:</span>
                <span class="metric-value positive">{report_data['reaction_summary']['worked']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Failed:</span>
                <span class="metric-value negative">{report_data['reaction_summary']['failed']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Absorbed:</span>
                <span class="metric-value">{report_data['reaction_summary']['absorbed']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Effectiveness:</span>
                <span class="metric-value">{report_data['reaction_summary']['effectiveness']:.1%}</span>
            </div>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        
        return html

    def render_reaction_table(self, reactions: list[ReactionRecord]) -> str:
        if not reactions:
            return "<p>No reaction data available.</p>"
        
        html = """
<table>
    <thead>
        <tr>
            <th>Published (ET)</th>
            <th>Headline</th>
            <th>Sentiment</th>
            <th>Session</th>
            <th>0→Close</th>
            <th>1D</th>
            <th>3D</th>
            <th>5D</th>
            <th>Verdict</th>
        </tr>
    </thead>
    <tbody>
"""
        
        for reaction in reactions:
            published_et = reaction.event.published_ts.strftime("%Y-%m-%d %H:%M ET")
            headline = reaction.event.title[:80] + "..." if len(reaction.event.title) > 80 else reaction.event.title
            sentiment = f"{reaction.event.sentiment:.2f}"
            session = reaction.session
            
            ret_0 = self._format_return(reaction.forward_returns.get("0_close"))
            ret_1d = self._format_return(reaction.forward_returns.get("1d"))
            ret_3d = self._format_return(reaction.forward_returns.get("3d"))
            ret_5d = self._format_return(reaction.forward_returns.get("5d"))
            
            verdict = reaction.verdict or "N/A"
            
            html += f"""
        <tr>
            <td>{published_et}</td>
            <td>{headline}</td>
            <td>{sentiment}</td>
            <td>{session}</td>
            <td>{ret_0}</td>
            <td>{ret_1d}</td>
            <td>{ret_3d}</td>
            <td>{ret_5d}</td>
            <td>{verdict}</td>
        </tr>
"""
        
        html += """
    </tbody>
</table>
"""
        
        return html

    def _format_return(self, value: float | None) -> str:
        if value is None:
            return "N/A"
        
        pct = value * 100
        color = "positive" if value > 0 else "negative" if value < 0 else ""
        return f'<span class="{color}">{pct:+.2f}%</span>'

    def _get_recommendation_class(self, action: str) -> str:
        action_lower = action.lower()
        if "buy" in action_lower:
            return "buy"
        elif "sell" in action_lower:
            return "sell"
        else:
            return "hold"

    def _render_tier(self, recommendation: Dict[str, Any]) -> str:
        tier = recommendation.get('tier')
        if tier:
            return f"""
            <div class="metric">
                <span class="metric-label">Tier:</span>
                <span class="metric-value">{tier.replace('_', ' ').upper()}</span>
            </div>
"""
        return ""
