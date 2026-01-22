# Trading Strategy Analyzer - Usage Guide

## 🎯 Personalized Trading Analysis System

The Trading Strategy Analyzer provides **actionable recommendations** based on your actual trading style, positions, and risk tolerance.

## 📋 Trading Strategies Available

### 1. **Swing Trading** 🔄
- **Timeframe**: Weeks to months
- **Focus**: Momentum and trend reversals
- **Risk**: High (0.7)
- **Stop Loss**: 8%
- **Take Profit**: 20%
- **Best for**: Active traders who want to capture medium-term moves

### 2. **Position Trading** 📊
- **Timeframe**: Months to years  
- **Focus**: Fundamental analysis and major trends
- **Risk**: Medium (0.5)
- **Stop Loss**: 15%
- **Take Profit**: 50%
- **Best for**: Long-term investors building core positions

### 3. **Income/Covered Calls** 💰
- **Timeframe**: 3-6 months
- **Focus**: Dividend income and options writing
- **Risk**: Low (0.3)
- **Stop Loss**: 12%
- **Take Profit**: 15%
- **Best for**: Income-focused investors

### 4. **Momentum Trading** ⚡
- **Timeframe**: Days to weeks
- **Focus**: Strong trends and news catalysts
- **Risk**: Very High (0.9)
- **Stop Loss**: 5%
- **Take Profit**: 15%
- **Best for**: Active traders seeking quick gains

## 🚀 Quick Start Examples

### Analyze Your Portfolio
```bash
# Swing trading analysis of current positions
python trading_strategy_analyzer.py --portfolio portfolio.json --strategy swing

# Position trading with longer timeframe
python trading_strategy_analyzer.py --portfolio portfolio.json --strategy position --max-headlines 20
```

### Analyze Watchlist
```bash
# Momentum trading for quick entries
python trading_strategy_analyzer.py --watchlist AAPL TSLA NVDA --strategy momentum

# Income strategy for dividend stocks
python trading_strategy_analyzer.py --watchlist JPM KO XOM --strategy income
```

### Save Analysis Results
```bash
# Save detailed analysis to JSON
python trading_strategy_analyzer.py --portfolio portfolio.json --strategy swing --output analysis_2026_01.json
```

## 📁 Portfolio Configuration

Create a `portfolio.json` file:

```json
{
  "portfolio_name": "Tech Growth Portfolio",
  "created_date": "2026-01-22",
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
    },
    {
      "ticker": "AMD",
      "shares": 75,
      "cost_basis": 220.0,
      "notes": "AI chip momentum"
    }
  ],
  "cash": 25000.0,
  "total_value": 85000.0
}
```

## 📊 Understanding the Output

### Recommendation Types
- 🟢 **BUY**: New position recommendation
- 🔴 **SELL**: Exit current position
- 🟡 **HOLD**: Maintain current position
- 🟠 **TRIM**: Reduce position size (partial profit taking)
- 🔵 **ADD**: Increase position size
- ⚫ **CLOSE**: Close entire position

### Key Metrics
- **Confidence**: How certain the system is (0-100%)
- **Price Target**: Where the stock could go
- **Stop Loss**: Where to cut losses
- **Position Size**: Recommended position size (% of portfolio)
- **Risk/Reward**: Potential reward vs risk ratio

### Risk Assessment
- 🟢 **LOW**: Minimal risk factors
- 🟡 **MEDIUM**: Some concerning factors
- 🔴 **HIGH**: Multiple risk factors present

## 🎯 Sample Analysis Results

### Swing Trading Example
```
🎯 WDC
Position: 50 shares @ $180.00
Current: $241.90 📈 +34.4% ($+3095.00)

🟠 RECOMMENDATION: TRIM
Confidence: 80%
Stop Loss: $165.60
Position Size: 50%

📝 Reasoning:
  1. Take profit: +34.4% exceeds target of 20%

🟡 RISK ASSESSMENT: MEDIUM (Score: 0.45)
Factors:
  • High volatility
  • Moderate drawdown
```

### Position Trading Example
```
🎯 NVDA
🟢 RECOMMENDATION: BUY
Confidence: 70%
Price Target: $274.98
Stop Loss: $155.82
Position Size: 15%
Risk/Reward: 3.33

📝 Reasoning:
  1. Long-term uptrend with positive fundamentals

🟢 RISK ASSESSMENT: LOW (Score: 0.25)
```

## 🔄 Strategy-Specific Logic

### Swing Trading
- **Trim winners** at 20% profit
- **Cut losses** quickly at 8% loss
- **Add to positions** on strong news signals
- **Focus on** momentum and technical indicators

### Position Trading
- **Take partial profits** at 50% gains
- **Hold through** volatility if trend is intact
- **Add on dips** if fundamentals are strong
- **Focus on** long-term trends and fundamentals

### Income Strategy
- **Look for** covered call opportunities at 10%+ profit
- **Average down** on significant declines (15%+)
- **Focus on** low volatility and dividend yield
- **Less concerned** with short-term price swings

### Momentum Trading
- **Quick entries** on strong news signals
- **Tight stops** at 5% loss
- **Take profits** at 15% gains
- **Focus on** volume spikes and news catalysts

## 📈 Advanced Features

### Custom Timeframes
```bash
# Override default timeframes
python trading_strategy_analyzer.py --watchlist AAPL --strategy swing --timeframe 6m
```

### Risk Management
- **Position sizing** based on strategy risk tolerance
- **Stop losses** automatically calculated
- **Risk/reward ratios** provided for all trades
- **Portfolio-level** risk assessment

### News Integration
- **Real-time sentiment** analysis
- **News categorization** (earnings, products, M&A, etc.)
- **Quality scoring** of news sources
- **Impact assessment** (High/Medium/Low)

## 💡 Pro Tips

1. **Match Strategy to Your Style**: Don't use momentum trading if you're a long-term investor
2. **Watch Confidence Levels**: Focus on recommendations with 70%+ confidence
3. **Understand Risk Factors**: Pay attention to the risk assessment section
4. **Use Position Sizing**: Don't ignore the recommended position sizes
5. **Set Real Stops**: Always use the suggested stop-loss levels

## ⚠️ Important Notes

- **Not Investment Advice**: This is for analysis and educational purposes
- **Market Conditions**: Strategies perform differently in various market environments
- **Personal Risk**: Adjust position sizes based on your personal risk tolerance
- **Due Diligence**: Always do your own research before making trades

## 🔗 Integration with Other Tools

The analyzer works seamlessly with:
- **News Analyzer**: Enhanced sentiment and categorization
- **Report Generator**: Professional HTML/Markdown reports
- **Portfolio Trackers**: JSON format for easy integration

---

*Start with the strategy that best matches your trading style and adjust as needed!*
