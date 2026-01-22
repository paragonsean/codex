# 🎯 Advanced Stock Market Analysis System

A comprehensive Python-based platform for sophisticated stock analysis, combining technical indicators, enhanced news sentiment, personalized trading strategies, and professional reporting.

## 🚀 Features Overview

### 📊 Market Data Processing
- **Daily OHLCV Data**: Clean, normalized price data from Yahoo Finance
- **50+ Technical Indicators**: RSI, DMA, ATR, volatility, drawdowns, volume analysis
- **Risk Metrics**: VaR, Sharpe ratio, downside deviation, beta estimation
- **"Good News Not Working" Proxies**: 8 different indicators of market health

### 📰 Enhanced News Analysis
- **7 News Categories**: earnings, mergers, products, financial, operations, legal, market
- **Sentiment Scoring**: Financial lexicon with positive/negative word analysis
- **Quality Assessment**: Source credibility weighting (Reuters, Bloomberg, etc.)
- **Impact Detection**: High/Medium/Low impact news identification
- **Entity Extraction**: Company names and key entities recognition

### 🎯 Dual Scoring System
- **Opportunity Score (0-100)**: Buy/hold bias from positive signal clusters
- **Sell-Risk Score (0-100)**: Trim/exit bias from negative signal clusters
- **Signal Clustering**: 7 clusters with multiple related indicators each
- **Dynamic Weighting**: Context-aware signal importance
- **Overall Bias**: STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL recommendations

### 💼 Personalized Trading Strategies
- **4 Trading Styles**: Swing, Position, Income/Covered Calls, Momentum
- **Portfolio Integration**: Cost basis awareness for trim vs exit decisions
- **Risk Management**: Strategy-specific stop losses and position sizing
- **Actionable Recommendations**: BUY/SELL/HOLD/TRIM/ADD with confidence levels

### 📋 Professional Reporting
- **HTML Reports**: Interactive, styled reports with charts placeholders
- **Markdown Reports**: Clean, structured text for documentation
- **PDF Export**: Optional conversion to professional PDF format
- **Portfolio Summary**: Multi-stock overview with comparative analysis

## 📁 System Architecture & File Descriptions

### 📊 Core Analysis Engines

#### **`market_data_processor.py`** - Market Data Processing Engine
**Purpose**: Fetches, cleans, and processes OHLCV data with 50+ technical indicators

**Key Functions**:
- Fetches daily OHLCV data from Yahoo Finance
- Calculates RSI, moving averages, ATR, volatility, drawdowns
- Computes risk metrics (VaR, Sharpe ratio, downside deviation)
- Analyzes "good news not working" proxies (8 different indicators)
- Provides normalized, clean data for all other components

**Usage**:
```bash
python market_data_processor.py AAPL --days 252 --save
```

#### **`news.py`** - Enhanced News Analysis Engine
**Purpose**: Fetches news headlines and performs sophisticated sentiment/categorization analysis

**Key Functions**:
- Fetches news from Google News RSS for any ticker/query
- Categorizes news into 7 types (earnings, mergers, products, financial, operations, legal, market)
- Calculates sentiment scores using financial lexicon
- Assesses news source quality and impact levels
- Extracts entities (companies, people, locations)

**Usage**:
```bash
python news.py --tickers MU WDC AMD --days 180 --max-headlines 10
```

#### **`dual_scoring_system.py`** - Opportunity vs Sell-Risk Scoring Engine
**Purpose**: Generates dual scores (opportunity + sell-risk) using signal clustering instead of single indicators

**Key Functions**:
- Calculates Opportunity Score (0-100) from positive signal clusters
- Calculates Sell-Risk Score (0-100) from negative signal clusters
- Uses 7 signal clusters with multiple related indicators each
- Provides overall bias (STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL)
- Includes confidence scoring based on cluster strength

**Usage**:
```bash
python dual_scoring_system.py MU WDC AAPL --days 180
```

### 💼 Trading & Strategy

#### **`trading_strategy_analyzer.py`** - Personalized Trading Strategy Engine
**Purpose**: Provides strategy-specific trading recommendations based on personal trading style and positions

**Key Functions**:
- Supports 4 trading strategies (Swing, Position, Income, Momentum)
- Analyzes current positions with cost basis awareness
- Recommends BUY/SELL/HOLD/TRIM/ADD with confidence levels
- Calculates strategy-specific stop losses and position sizes
- Integrates technical analysis with news sentiment

**Usage**:
```bash
python trading_strategy_analyzer.py --portfolio portfolio.json --strategy swing
python trading_strategy_analyzer.py --watchlist AAPL TSLA --strategy position
```

#### **`sample_portfolio.json`** - Portfolio Configuration Example
**Purpose**: Example configuration file for portfolio analysis

**Structure**:
```json
{
  "portfolio_name": "Tech Growth Portfolio",
  "positions": [
    {
      "ticker": "MU",
      "shares": 100,
      "cost_basis": 350.0,
      "notes": "Memory play - AI cycle"
    }
  ]
}
```

### 📋 Reporting & Visualization

#### **`stock_report_generator.py`** - Professional Report Generator
**Purpose**: Creates professional HTML and Markdown reports for stock analysis

**Key Functions**:
- Generates comprehensive HTML reports with professional styling
- Creates structured Markdown reports for documentation
- Includes portfolio summaries and comparative analysis
- Integrates all analysis components into unified reports
- Supports PDF export (with weasyprint)

**Usage**:
```bash
python stock_report_generator.py --tickers MU WDC AMD --format both
python stock_report_generator.py --portfolio portfolio.json --days 365
```

#### **`report_viewer.py`** - Report Management Utility
**Purpose**: Manages generated reports and provides viewing/conversion capabilities

**Key Functions**:
- Lists all available reports in the reports directory
- Opens HTML reports in default browser
- Converts HTML reports to PDF format
- Provides report metadata and file information

**Usage**:
```bash
python report_viewer.py --list
python report_viewer.py --open stock_report_20260122_191742.html
python report_viewer.py --convert-pdf stock_report_20260122_191742.html
```

#### **`demo_workflow.py`** - Complete System Demonstration
**Purpose**: Demonstrates the complete workflow from analysis to reporting

**Key Functions**:
- Runs end-to-end analysis demonstration
- Shows integration between all components
- Provides usage examples for different scenarios
- Generates sample reports and analysis

**Usage**:
```bash
python demo_workflow.py
```

### 🧪 Testing & Utilities

#### **`test_market_data.py`** - Market Data Processor Testing
**Purpose**: Tests the market data processing functionality with real data

**Key Functions**:
- Tests data fetching and processing pipeline
- Validates indicator calculations
- Demonstrates market data quality checks
- Provides debugging for data issues

**Usage**:
```bash
python test_market_data.py
```

#### **`test_dual_scoring.py`** - Dual Scoring System Testing
**Purpose**: Tests the dual scoring system with different market scenarios

**Key Functions**:
- Tests opportunity and sell-risk cluster analysis
- Demonstrates signal clustering logic
- Validates scoring calculations
- Shows different market condition responses

**Usage**:
```bash
python test_dual_scoring.py
```

### 📚 Documentation

#### **`README.md`** - This Comprehensive System Guide
**Purpose**: Complete documentation for the entire system

**Contents**:
- Installation and setup instructions
- Feature overview and usage examples
- File descriptions and system architecture
- Trading strategy explanations
- Technical indicator documentation

#### **`TRADING_GUIDE.md`** - Trading Strategy Usage Guide
**Purpose**: Detailed guide for using personalized trading strategies

**Contents**:
- Strategy selection guidance
- Portfolio configuration
- Risk management best practices
- Recommendation interpretation

#### **`MARKET_DATA_SUMMARY.md`** - Market Data Processing Documentation
**Purpose**: Technical documentation for market data processing

**Contents**:
- Indicator calculations and formulas
- Risk metric explanations
- Data quality considerations
- Performance optimization

#### **`DUAL_SCORING_SUMMARY.md`** - Dual Scoring System Documentation
**Purpose**: Detailed explanation of the dual scoring methodology

**Contents**:
- Signal clustering theory
- Cluster weightings and triggers
- Scoring algorithms
- Use case examples

---

## 🔄 Data Flow Between Components

```
1. market_data_processor.py
   ↓ (Provides technical indicators and risk metrics)
2. news.py
   ↓ (Provides sentiment and categorization)
3. dual_scoring_system.py
   ↓ (Generates opportunity/sell-risk scores)
4. trading_strategy_analyzer.py
   ↓ (Creates strategy-specific recommendations)
5. stock_report_generator.py
   ↓ (Produces professional reports)
6. report_viewer.py
   ↓ (Manages and displays reports)
```

## 🎯 Component Interactions

### **Data Processing Pipeline**:
- `market_data_processor.py` → All other components (provides indicators)
- `news.py` → `dual_scoring_system.py` & `trading_strategy_analyzer.py` (provides sentiment)

### **Analysis Flow**:
- `dual_scoring_system.py` → `trading_strategy_analyzer.py` (provides scores)
- `trading_strategy_analyzer.py` → `stock_report_generator.py` (provides recommendations)

### **Reporting Chain**:
- All analysis components → `stock_report_generator.py` (unified reporting)
- `stock_report_generator.py` → `report_viewer.py` (report management)

### **Testing Support**:
- `test_*.py` files → Validate corresponding main components
- `demo_workflow.py` → End-to-end system validation

## 🛠 Installation

### Required Packages
```bash
pip install pandas numpy yfinance requests feedparser
```

### Optional for PDF Export
```bash
pip install weasyprint
```

## 🚀 Quick Start

### 1. Basic News Analysis
```bash
# Enhanced news with categorization
python news.py --tickers MU WDC AMD --days 180 --max-headlines 10

# Custom keywords and queries
python news.py --tickers MU --keywords "HBM,DRAM,AI" --extra-query "Micron earnings"
```

### 2. Market Data Analysis
```bash
# Comprehensive technical analysis
python market_data_processor.py MU --days 252 --save

# Multiple tickers
python market_data_processor.py AAPL TSLA NVDA --days 180
```

### 3. Dual Scoring Analysis
```bash
# Opportunity vs sell-risk scoring
python dual_scoring_system.py MU WDC AAPL --days 180
```

### 4. Personalized Trading Analysis
```bash
# Analyze portfolio with swing trading strategy
python trading_strategy_analyzer.py --portfolio portfolio.json --strategy swing

# Analyze watchlist with position trading
python trading_strategy_analyzer.py --watchlist AAPL TSLA --strategy position
```

### 5. Professional Reports
```bash
# Generate HTML and Markdown reports
python stock_report_generator.py --tickers MU WDC AMD --format both

# Portfolio analysis report
python stock_report_generator.py --portfolio portfolio.json --days 365
```

### 6. Report Management
```bash
# List available reports
python report_viewer.py --list

# Open HTML report
python report_viewer.py --open stock_report_20260122_191742.html

# Convert to PDF
python report_viewer.py --convert-pdf stock_report_20260122_191742.html
```

## 📊 Usage Examples

### Portfolio Analysis
```json
{
  "portfolio_name": "Tech Growth Portfolio",
  "positions": [
    {
      "ticker": "MU",
      "shares": 100,
      "cost_basis": 350.0,
      "notes": "Memory play - AI cycle"
    },
    {
      "ticker": "WDC",
      "shares": 50,
      "cost_basis": 180.0,
      "notes": "Storage recovery story"
    }
  ]
}
```

### Trading Strategy Output
```
🎯 WDC | Signal: +49.44 | News: 15 headlines
Position: 50 shares @ $180.00
Current: $241.90 📈 +34.4% ($+3095.00)

🟠 RECOMMENDATION: TRIM
Confidence: 80%
Stop Loss: $165.60
Position Size: 50%

📝 Reasoning:
  1. Take profit: +34.4% exceeds target of 20%
  2. RSI suggests overbought (>=70)

🟡 RISK ASSESSMENT: MEDIUM (Score: 0.45)
Factors:
  • High volatility
  • Moderate drawdown
```

### Dual Scoring Results
```
📊 OVERALL ASSESSMENT:
  Opportunity Score: 100.0/100
  Sell-Risk Score:  100.0/100
  Overall Bias:      HOLD
  Confidence:        28.7%

🟢 OPPORTUNITY CLUSTERS:
  Technical Momentum: 80.0% strength ✅ ACTIVE
    • Strong 21D momentum
    • Bullish trend (50>200)
    • Volume confirms upside

🔴 SELL-RISK CLUSTERS:
  Technical Overheating: 90.0% strength ⚠️ ACTIVE
    • RSI overbought (>70)
    • Potential RSI divergence
    • Extended gains (>50% in 3mo)
```

## 🎯 Trading Strategies

### Swing Trading
- **Timeframe**: Weeks to months
- **Risk Tolerance**: High (0.7)
- **Stop Loss**: 8%
- **Take Profit**: 20%
- **Best for**: Active traders seeking medium-term moves

### Position Trading
- **Timeframe**: Months to years
- **Risk Tolerance**: Medium (0.5)
- **Stop Loss**: 15%
- **Take Profit**: 50%
- **Best for**: Long-term investors building core positions

### Income/Covered Calls
- **Timeframe**: 3-6 months
- **Risk Tolerance**: Low (0.3)
- **Stop Loss**: 12%
- **Take Profit**: 15%
- **Best for**: Income generation and options writing

### Momentum Trading
- **Timeframe**: Days to weeks
- **Risk Tolerance**: Very High (0.9)
- **Stop Loss**: 5%
- **Take Profit**: 15%
- **Best for**: Active traders seeking quick gains

## 📈 Technical Indicators

### Price-Based Indicators
- **RSI (14)**: Relative Strength Index with Wilder's smoothing
- **50/200 DMA**: Moving average trend analysis
- **ATR**: Average True Range for volatility
- **Drawdowns**: Maximum and current drawdown from peak

### Volume Indicators
- **Volume Z-Score**: Current volume vs 20-day average
- **Volume Ratio**: Volume confirmation of price moves
- **Volume Stability**: Coefficient of variation

### Risk Metrics
- **Realized Volatility**: 20D and 50D annualized volatility
- **VaR (95%)**: Value at Risk calculation
- **Sharpe Ratio**: Risk-adjusted return measure
- **Downside Deviation**: Asymmetric risk measure

## 📰 News Analysis Features

### News Categories
- **Earnings**: Quarterly results, guidance, estimates
- **Mergers**: Acquisitions, takeovers, partnerships
- **Products**: New launches, chips, AI technologies
- **Financial**: Financing, debt, investments
- **Operations**: Manufacturing, supply chain
- **Legal**: Lawsuits, patents, regulations
- **Market**: Competition, pricing, trends

### Quality Assessment
- **High Quality**: Reuters, Bloomberg, WSJ, FT, AP (0.8-1.0)
- **Medium Quality**: Seeking Alpha, IBT, Motley Fool (0.6-0.8)
- **Base Quality**: Other sources (0.5)

### Impact Levels
- **High Impact**: Breakthrough, revolutionary, landmark
- **Medium Impact**: Significant, substantial, major
- **Low Impact**: Normal, routine news

## 🎯 Dual Scoring System

### Opportunity Clusters
1. **Technical Momentum** (35% weight)
   - Strong price momentum
   - RSI oversold conditions
   - Bullish trend confirmation
   - Volume confirmation

2. **Value/Reversal** (25% weight)
   - Deep drawdown recovery
   - Low volatility entry
   - Support level proximity
   - Positive news sentiment

3. **Breakout Potential** (20% weight)
   - Near resistance breakout
   - Volume surge confirmation
   - Volatility expansion
   - Momentum acceleration

### Sell-Risk Clusters
1. **Technical Overheating** (35% weight)
   - RSI overbought (>70)
   - RSI divergence patterns
   - Extended gains
   - High volatility with gains

2. **Trend Deterioration** (30% weight)
   - Below 50DMA
   - 50DMA flattening
   - Bearish trend
   - Moving average cross threat

3. **Distribution Behavior** (25% weight)
   - High volume down days
   - Failed breakouts
   - Intraday weakness
   - Gap down frequency

4. **Volatility Regime Shift** (20% weight)
   - ATR rising with flat returns
   - High volatility regime
   - Rapid volatility expansion
   - High downside deviation

## 📊 Report Examples

### HTML Reports
- **Responsive Design**: Mobile and desktop compatible
- **Interactive Elements**: Expandable sections, hover effects
- **Professional Styling**: Corporate-quality presentation
- **Chart Placeholders**: Ready for chart library integration

### Markdown Reports
- **Structured Format**: Headers, tables, bullet points
- **GitHub Compatible**: Perfect for documentation
- **Easy Integration**: Works with documentation systems
- **Clean Output**: Minimal formatting, maximum readability

## 🔧 Advanced Configuration

### Custom Keywords
```python
DEFAULT_KEYWORDS = [
    "AI", "HBM", "DRAM", "NAND", "chipsets", 
    "semiconductor", "datacenter", "cloud"
]
```

### Strategy Customization
```python
custom_strategy = TradingStrategy(
    name="Custom Momentum",
    timeframes={"trend": 126, "cycle": 42},
    risk_tolerance=0.8,
    stop_loss_pct=0.06,
    take_profit_pct=0.18
)
```

### News Source Quality
```python
HIGH_QUALITY_SOURCES = {
    "reuters", "bloomberg", "wall street journal",
    "financial times", "associated press"
}
```

## 🚀 Performance & Scaling

### Data Processing
- **Efficient Computing**: Vectorized pandas operations
- **Memory Management**: Optimized data structures
- **Caching**: Reduces redundant API calls
- **Error Handling**: Robust failure recovery

### API Rate Limits
- **Yahoo Finance**: Built-in rate limiting
- **Google News RSS**: Respectful crawling
- **Batch Processing**: Multiple tickers efficiently
- **Retry Logic**: Automatic retry on failures

## 🧪 Testing & Validation

### Test Coverage
- **Market Data Processing**: 50+ indicators validation
- **News Analysis**: Categorization and sentiment accuracy
- **Dual Scoring**: Cluster triggering logic
- **Trading Strategies**: Recommendation accuracy

### Validation Methods
- **Historical Backtesting**: Strategy performance validation
- **Cross-Validation**: Signal reliability testing
- **Edge Case Handling**: Market condition extremes
- **Integration Testing**: End-to-end workflow validation

## 🔒 Security & Privacy

### Data Handling
- **Local Processing**: No external data sharing
- **Secure Storage**: Encrypted configuration files
- **Privacy Focused**: No personal data collection
- **Open Source**: Full code transparency

### API Security
- **Rate Limiting**: Respectful API usage
- **Error Handling**: No credential exposure
- **Session Management**: Secure connection handling
- **Input Validation**: Sanitized user inputs

## 🤝 Contributing

### Development Setup
```bash
git clone <repository>
cd stock-analysis-system
pip install -r requirements.txt
python -m pytest tests/
```

### Code Standards
- **PEP 8 Compliance**: Consistent formatting
- **Type Hints**: Full type annotation
- **Documentation**: Comprehensive docstrings
- **Testing**: Unit and integration tests

### Feature Requests
- **GitHub Issues**: Track feature requests
- **Pull Requests**: Welcome contributions
- **Discussions**: Community feedback
- **Roadmap**: Planned enhancements

## 📞 Support

### Documentation
- **README.md**: This overview
- **TRADING_GUIDE.md**: Detailed usage instructions
- **MARKET_DATA_SUMMARY.md**: Technical indicator documentation
- **DUAL_SCORING_SUMMARY.md**: Scoring system details

### Troubleshooting
- **Common Issues**: FAQ section
- **Error Messages**: Detailed explanations
- **Configuration Help**: Setup guidance
- **Performance Tips**: Optimization advice

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **yfinance**: Yahoo Finance API integration
- **feedparser**: RSS feed processing
- **pandas/numpy**: Data analysis foundation
- **requests**: HTTP client functionality

---

## 🎯 Quick Summary

This system provides **institutional-quality stock analysis** with:

✅ **50+ Technical Indicators** - Comprehensive market data processing  
✅ **Enhanced News Analysis** - 7 categories with quality scoring  
✅ **Dual Scoring System** - Opportunity vs sell-risk signal clustering  
✅ **Personalized Strategies** - 4 trading styles with risk management  
✅ **Professional Reports** - HTML/Markdown/PDF output  
✅ **Portfolio Integration** - Cost basis aware recommendations  

**Perfect for**: Individual investors, traders, portfolio managers, and financial analysts seeking sophisticated market analysis tools.

---

*Built with ❤️ for the investment community*
