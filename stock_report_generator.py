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
