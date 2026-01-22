# Stock Market Analysis & Reporting System

A comprehensive Python-based system for analyzing stocks using technical indicators and enhanced news sentiment analysis with professional report generation.

## 🚀 Features

### Enhanced News Analysis
- **7 News Categories**: earnings, mergers, products, financial, operations, legal, market
- **Sentiment Scoring**: Positive/negative word analysis with financial lexicon
- **Quality Assessment**: Source credibility weighting (Reuters, Bloomberg, etc.)
- **Impact Detection**: High/Medium/Low impact news identification
- **Entity Extraction**: Company names and key entities recognition
- **Keyword Relevance**: Custom keyword matching for industry-specific terms

### Technical Analysis
- **Price Momentum**: 5d, 21d, 63d returns
- **Volatility Analysis**: Annualized volatility and maximum drawdown
- **Technical Indicators**: RSI, moving averages, trend analysis
- **Volume Analysis**: Volume spike detection
- **Risk Metrics**: Drawdown and volatility measurements

### Professional Reports
- **HTML Reports**: Interactive, styled reports with charts placeholders
- **Markdown Reports**: Clean, text-based reports for documentation
- **PDF Export**: Optional PDF conversion (requires weasyprint)
- **Portfolio Summary**: Multi-stock overview with comparative analysis

## 📁 Files Overview

```
├── news.py                    # Enhanced news analyzer with categorization
├── stock_report_generator.py  # Professional HTML/Markdown report generator
├── report_viewer.py           # Report viewing and PDF conversion utility
├── demo_workflow.py           # Complete workflow demonstration
├── reports/                   # Generated reports directory
└── README_SYSTEM.md           # This documentation
```

## 🛠 Installation

```bash
# Required packages
pip install pandas numpy yfinance requests feedparser

# Optional for PDF conversion
pip install weasyprint
```

## 📊 Usage Examples

### Basic News Analysis
```bash
# Enhanced news analysis with categorization
python news.py --tickers MU WDC AMD --days 180 --max-headlines 10

# Custom keywords and queries
python news.py --tickers MU --keywords "HBM,DRAM,AI" --extra-query "Micron earnings"
```

### Generate Professional Reports
```bash
# Generate both HTML and Markdown reports
python stock_report_generator.py --tickers MU WDC AMD --days 180 --format both

# HTML only with custom parameters
python stock_report_generator.py --tickers AAPL TSLA --days 90 --max-headlines 20 --format html
```

### View and Convert Reports
```bash
# List available reports
python report_viewer.py --list

# Open HTML report in browser
python report_viewer.py --open stock_report_20260122_191742.html

# Convert to PDF
python report_viewer.py --convert-pdf stock_report_20260122_191742.html
```

### Complete Workflow Demo
```bash
# Run the complete demonstration
python demo_workflow.py
```

## 📈 Analysis Components

### News Categorization System

The system automatically categorizes news into:
- **Earnings**: Quarterly results, EPS, revenue, guidance
- **Mergers**: Acquisitions, takeovers, partnerships
- **Products**: New launches, chips, AI, storage technologies
- **Financial**: Financing, debt, investments, dividends
- **Operations**: Manufacturing, supply chain, facilities
- **Legal**: Lawsuits, patents, regulations
- **Market**: Competition, pricing, industry trends

### Combined Signal Calculation

The scoring system combines:
- **Price Momentum** (40× 21d returns + 25× 63d returns)
- **News Sentiment** (quality-weighted sentiment + keyword relevance)
- **Impact Bonuses** (high-impact events + category-specific bonuses)
- **Technical Adjustments** (trend, RSI, volume spikes)

### Quality Assessment

News sources are rated by credibility:
- **High Quality** (0.8-1.0): Reuters, Bloomberg, WSJ, FT, AP
- **Medium Quality** (0.6-0.8): Seeking Alpha, IBT, Motley Fool
- **Base Quality** (0.5): Other sources

## 📋 Sample Output

### Analysis Summary
```
📈 MU       | Signal:  +54.12 | News: 15 headlines
📈 WDC      | Signal:  +49.44 | News: 15 headlines  
📈 AMD      | Signal:  +16.84 | News: 15 headlines
```

### News Analysis Example
```
News Analysis: 15 headlines | avg_quality=0.86 | high_impact=0
Categories: products(5), financial(4), earnings(3), market(2), mergers(1)
```

### Technical Metrics
```
Last Price: $389.11 | 5D: +15.08% | 21D: +56.55% | 63D: +88.18%
Volatility: 65.9% | Max Drawdown: -20.5% | RSI: 77.2 | Trend: unknown
```

## 🎯 Key Insights

### Enhanced Capabilities vs Basic Analysis

| Feature | Basic | Enhanced System |
|---------|-------|------------------|
| News Categorization | ❌ | ✅ 7 categories |
| Quality Scoring | ❌ | ✅ Source credibility |
| Impact Assessment | ❌ | ✅ High/Med/Low detection |
| Entity Extraction | ❌ | ✅ Company names |
| Professional Reports | ❌ | ✅ HTML/Markdown/PDF |
| Portfolio Overview | ❌ | ✅ Multi-stock summary |

### Signal Quality Improvements

- **Context-aware categorization** understands news type impact
- **Source quality weighting** reduces noise from low-quality sources  
- **Impact detection** highlights potentially market-moving events
- **Entity recognition** improves relevance scoring
- **Professional presentation** suitable for investment research

## 🔧 Customization

### Adding Custom Keywords
```python
# In news.py, modify the default keywords
DEFAULT_KEYWORDS = ["AI", "HBM", "DRAM", "NAND", "chipsets", "semiconductor"]
```

### Adding News Categories
```python
# Add new categories to NEWS_CATEGORIES
NEWS_CATEGORIES["regulatory"] = {
    "fda", "sec", "regulation", "compliance", "approval"
}
```

### Custom Styling
Edit the CSS in `stock_report_generator.py` to customize report appearance.

## 📊 Report Features

### HTML Reports Include
- **Responsive design** for mobile/desktop viewing
- **Interactive metrics** with color-coded indicators
- **News categorization** with impact level badges
- **Technical indicators** grid layout
- **Professional styling** suitable for presentations

### Markdown Reports Include
- **Structured tables** for technical metrics
- **Hierarchical sections** for easy reading
- **Bullet-point summaries** for quick insights
- **GitHub-compatible** formatting

## 🚀 Advanced Usage

### Batch Analysis
```bash
# Analyze entire sectors
python stock_report_generator.py --tickers $(cat semiconductor_stocks.txt) --days 90
```

### Custom Time Periods
```bash
# Earnings season analysis
python stock_report_generator.py --tickers MU WDC AMD --days 30 --max-headlines 30
```

### Integration with Other Tools
The system outputs structured data that can be easily integrated with:
- Trading algorithms
- Portfolio management systems
- Alert systems
- Database storage

## ⚠️ Disclaimer

This system is for informational and educational purposes only. It should not be considered as investment advice. Always conduct your own research and consult with financial professionals before making investment decisions.

## 🔗 Dependencies

- **yfinance**: Yahoo Finance API for price data
- **feedparser**: RSS feed parsing for news
- **pandas/numpy**: Data analysis and manipulation
- **requests**: HTTP client for news feeds
- **weasyprint** (optional): PDF generation

---

*Generated by Stock Market Analysis System*
