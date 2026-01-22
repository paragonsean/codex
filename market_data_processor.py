#!/usr/bin/env python3
"""
market_data_processor.py

Comprehensive market data processing with standard technical indicators.
Normalizes data from multiple sources and computes key trading indicators.

Features:
- Daily OHLCV data with normalization
- Standard technical indicators (RSI, DMA, ATR, etc.)
- Risk metrics (volatility, drawdown, volume analysis)
- "Good news not working" proxy indicators
- Clean, normalized data output for analysis

Usage:
    from market_data_processor import MarketDataProcessor
    
    processor = MarketDataProcessor()
    data = processor.fetch_and_process("AAPL", days=252)
"""

import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
try:
    from pandas.errors import Pandas4Warning
    warnings.filterwarnings("ignore", category=Pandas4Warning)
except Exception:
    pass


@dataclass
class MarketData:
    """Normalized market data with comprehensive indicators."""
    ticker: str
    data: pd.DataFrame  # All OHLCV data with indicators
    current_price: float
    indicators: Dict[str, float]  # Latest indicator values
    risk_metrics: Dict[str, float]  # Risk assessment metrics
    news_effectiveness: Dict[str, float]  # "Good news not working" proxies
    metadata: Dict[str, any]  # Data quality and metadata


class MarketDataProcessor:
    """Comprehensive market data processing with standard indicators."""
    
    def __init__(self):
        self.data_cache = {}
    
    def fetch_and_process(self, ticker: str, days: int = 252) -> MarketData:
        """Fetch and process market data with all indicators."""
        print(f"Processing market data for {ticker} ({days} days)...")
        
        # Fetch raw data
        raw_data = self._fetch_price_data(ticker, days)
        
        if raw_data.empty:
            raise ValueError(f"No data found for ticker {ticker}")
        
        # Process and normalize data
        processed_data = self._process_data(raw_data)
        
        # Calculate all indicators
        indicators = self._calculate_indicators(processed_data)
        
        # Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(processed_data)
        
        # Calculate news effectiveness proxies
        news_effectiveness = self._calculate_news_effectiveness(processed_data, indicators)
        
        # Extract current values
        current_price = float(processed_data['Close'].iloc[-1])
        
        # Metadata
        metadata = {
            "data_points": len(processed_data),
            "start_date": processed_data.index[0].strftime('%Y-%m-%d'),
            "end_date": processed_data.index[-1].strftime('%Y-%m-%d'),
            "missing_days": self._check_data_quality(processed_data),
            "data_quality": "good" if len(processed_data) >= days * 0.95 else "limited"
        }
        
        return MarketData(
            ticker=ticker,
            data=processed_data,
            current_price=current_price,
            indicators=indicators,
            risk_metrics=risk_metrics,
            news_effectiveness=news_effectiveness,
            metadata=metadata
        )
    
    def _fetch_price_data(self, ticker: str, days: int) -> pd.DataFrame:
        """Fetch raw OHLCV data from Yahoo Finance."""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days + 30)  # Buffer for weekends/holidays
        
        try:
            # Use the same approach as news.py that works
            data = yf.download(
                tickers=ticker,
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"),
                interval="1d",
                auto_adjust=False,
                progress=False,
                threads=False,
            )
            
            if data is None or data.empty:
                return pd.DataFrame()
            
            # Handle multi-index columns (yfinance can return MultiIndex columns)
            if isinstance(data.columns, pd.MultiIndex):
                # Extract the ticker data from multi-index
                try:
                    level_values = data.columns.get_level_values(1)
                    if ticker in level_values.tolist():
                        # Filter columns for our ticker
                        ticker_data = data.xs(ticker, axis=1, level=1)
                        ticker_data.columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
                        data = ticker_data
                    else:
                        # Fallback: take first level
                        data.columns = data.columns.get_level_values(0)
                except (IndexError, KeyError, AttributeError) as e:
                    print(f"MultiIndex handling failed for {ticker}: {e}")
                    # Fallback: take first level
                    data.columns = data.columns.get_level_values(0)
            
            return data.dropna()
            
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return pd.DataFrame()
    
    def _process_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Process and normalize raw OHLCV data."""
        data = raw_data.copy()
        
        # Ensure we have the required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Data normalization and cleaning
        # Remove any zero or negative prices (data errors)
        for col in ['Open', 'High', 'Low', 'Close']:
            data = data[data[col] > 0]
        
        # Remove zero volumes
        data = data[data['Volume'] > 0]
        
        # Sort by date
        data = data.sort_index()
        
        # Forward fill any missing values (shouldn't be many after cleaning)
        try:
            data = data.fillna(method='ffill')
        except TypeError:
            # Handle newer pandas versions
            data = data.ffill()
        
        # Add basic derived columns
        data['Return'] = data['Close'].pct_change()
        data['LogReturn'] = np.log(data['Close'] / data['Close'].shift(1))
        data['Range'] = (data['High'] - data['Low']) / data['Open']
        data['Body'] = abs(data['Close'] - data['Open']) / data['Open']
        
        return data
    
    def _calculate_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate all standard technical indicators."""
        indicators = {}
        
        # RSI (14)
        indicators['rsi_14'] = self._calculate_rsi(data['Close'], 14)
        
        # Moving averages and trend
        indicators['sma_50'] = data['Close'].rolling(50).mean().iloc[-1]
        indicators['sma_200'] = data['Close'].rolling(200).mean().iloc[-1]
        indicators['ema_20'] = data['Close'].ewm(span=20).mean().iloc[-1]
        indicators['ema_50'] = data['Close'].ewm(span=50).mean().iloc[-1]
        
        # Trend analysis
        current_price = data['Close'].iloc[-1]
        indicators['trend_50_200'] = self._analyze_trend(current_price, indicators['sma_50'], indicators['sma_200'])
        indicators['price_vs_sma_50'] = (current_price - indicators['sma_50']) / indicators['sma_50']
        indicators['price_vs_sma_200'] = (current_price - indicators['sma_200']) / indicators['sma_200']
        
        # High/Low analysis
        indicators['high_20d'] = data['High'].rolling(20).max().iloc[-1]
        indicators['low_20d'] = data['Low'].rolling(20).min().iloc[-1]
        indicators['high_50d'] = data['High'].rolling(50).max().iloc[-1]
        indicators['low_50d'] = data['Low'].rolling(50).min().iloc[-1]
        
        # Position within ranges
        indicators['position_20d_high'] = (current_price - indicators['low_20d']) / (indicators['high_20d'] - indicators['low_20d'])
        indicators['position_50d_high'] = (current_price - indicators['low_50d']) / (indicators['high_50d'] - indicators['low_50d'])
        
        # ATR (Average True Range) - volatility measure
        indicators['atr_14'] = self._calculate_atr(data, 14)
        indicators['atr_pct'] = indicators['atr_14'] / current_price
        
        # Volume indicators
        indicators['volume_sma_20'] = data['Volume'].rolling(20).mean().iloc[-1]
        indicators['volume_ratio'] = data['Volume'].iloc[-1] / indicators['volume_sma_20']
        indicators['volume_z_score'] = self._calculate_volume_zscore(data)
        
        # Price momentum
        for period in [5, 10, 21, 63]:
            indicators[f'return_{period}d'] = self._calculate_return(data['Close'], period)
        
        # Volatility metrics
        indicators['volatility_20d'] = data['Return'].rolling(20).std() * np.sqrt(252)
        indicators['volatility_50d'] = data['Return'].rolling(50).std() * np.sqrt(252)
        
        # Additional momentum indicators
        indicators['momentum_5d'] = self._calculate_momentum(data['Close'], 5)
        indicators['momentum_21d'] = self._calculate_momentum(data['Close'], 21)
        
        # Rate of Change
        indicators['roc_5d'] = self._calculate_roc(data['Close'], 5)
        indicators['roc_21d'] = self._calculate_roc(data['Close'], 21)
        
        return indicators
    
    def _calculate_risk_metrics(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate comprehensive risk metrics."""
        risk_metrics = {}
        
        current_price = data['Close'].iloc[-1]
        
        # Drawdown metrics
        risk_metrics['max_drawdown'] = self._calculate_max_drawdown(data['Close'])
        risk_metrics['current_drawdown'] = self._calculate_current_drawdown(data['Close'])
        risk_metrics['avg_drawdown'] = self._calculate_average_drawdown(data['Close'])
        
        # Volatility metrics
        returns = data['Return'].dropna()
        risk_metrics['realized_vol_20d'] = returns.tail(20).std() * np.sqrt(252)
        risk_metrics['realized_vol_50d'] = returns.tail(50).std() * np.sqrt(252)
        risk_metrics['volatility_regime'] = self._classify_volatility_regime(risk_metrics['realized_vol_20d'])
        
        # Downside risk metrics
        risk_metrics['downside_deviation'] = self._calculate_downside_deviation(returns)
        risk_metrics['var_95'] = returns.quantile(0.05)  # 5% VaR
        risk_metrics['cvar_95'] = returns[returns <= risk_metrics['var_95']].mean()  # 5% CVaR
        
        # Tail risk
        risk_metrics['skewness'] = returns.skew()
        risk_metrics['kurtosis'] = returns.kurtosis()
        risk_metrics['tail_ratio'] = self._calculate_tail_ratio(returns)
        
        # Liquidity risk (volume-based)
        risk_metrics['volume_stability'] = self._calculate_volume_stability(data['Volume'])
        risk_metrics['price_impact'] = self._estimate_price_impact(data)
        
        # Correlation risk (if we have benchmark data)
        risk_metrics['beta_estimate'] = self._estimate_beta(data['Close'])
        
        # Risk-adjusted returns
        risk_metrics['sharpe_ratio_20d'] = self._calculate_sharpe_ratio(returns.tail(20))
        risk_metrics['sortino_ratio_20d'] = self._calculate_sortino_ratio(returns.tail(20))
        
        return risk_metrics
    
    def _calculate_news_effectiveness(self, data: pd.DataFrame, indicators: Dict[str, float]) -> Dict[str, float]:
        """Calculate 'good news not working' proxy indicators."""
        proxies = {}
        
        returns = data['Return'].dropna()
        
        # 1. High volatility on up days (struggle to rise)
        up_days = returns[returns > 0]
        if len(up_days) > 0:
            proxies['up_day_volatility'] = up_days.std()
            proxies['up_day_vol_ratio'] = up_days.std() / returns.std()
        else:
            proxies['up_day_volatility'] = 0
            proxies['up_day_vol_ratio'] = 0
        
        # 2. Low return on high volume days (distribution)
        high_volume_threshold = data['Volume'].quantile(0.8)
        high_volume_days = data[data['Volume'] >= high_volume_threshold]
        if len(high_volume_days) > 0:
            proxies['high_volume_return'] = high_volume_days['Return'].mean()
            proxies['high_volume_win_rate'] = (high_volume_days['Return'] > 0).mean()
        else:
            proxies['high_volume_return'] = 0
            proxies['high_volume_win_rate'] = 0.5
        
        # 3. Weak close relative to high (intraday weakness)
        intraday_weakness = (data['Close'] - data['High']) / (data['High'] - data['Low'])
        proxies['avg_intraday_weakness'] = intraday_weakness.mean()
        proxies['intraday_weakness_trend'] = intraday_weakness.tail(20).mean()
        
        # 4. Gap down frequency (negative overnight sentiment)
        gaps = (data['Open'] - data['Close'].shift(1)) / data['Close'].shift(1)
        proxies['gap_down_frequency'] = (gaps < -0.01).mean()  # Gaps down >1%
        proxies['avg_gap'] = gaps.mean()
        
        # 5. Reversal patterns (failed breakouts)
        proxies['failed_breakout_frequency'] = self._calculate_failed_breakouts(data)
        
        # 6. Volume-price divergence
        price_trend = data['Close'].pct_change().rolling(10).sum()
        volume_trend = (data['Volume'].pct_change().rolling(10).sum())
        correlation = price_trend.corr(volume_trend)
        proxies['volume_price_divergence'] = -correlation if not np.isnan(correlation) else 0
        
        # 7. Resistance level strength
        proxies['resistance_strength'] = self._calculate_resistance_strength(data)
        
        # 8. News effectiveness score (composite)
        proxies['news_effectiveness_score'] = self._calculate_news_effectiveness_score(proxies)
        
        return proxies
    
    # === Technical Indicator Calculation Methods ===
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI using Wilder's smoothing."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range."""
        high_low = data['High'] - data['Low']
        high_close = abs(data['High'] - data['Close'].shift())
        low_close = abs(data['Low'] - data['Close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(period).mean()
        return atr.iloc[-1]
    
    def _analyze_trend(self, current_price: float, sma_50: float, sma_200: float) -> str:
        """Analyze trend based on moving averages."""
        if pd.isna(sma_50) or pd.isna(sma_200):
            return "unknown"
        
        if current_price > sma_50 > sma_200:
            return "strong_bullish"
        elif current_price > sma_50 and sma_50 < sma_200:
            return "bullish_transition"
        elif current_price < sma_50 < sma_200:
            return "strong_bearish"
        elif current_price < sma_50 and sma_50 > sma_200:
            return "bearish_transition"
        else:
            return "neutral"
    
    def _calculate_volume_zscore(self, data: pd.DataFrame, period: int = 20) -> float:
        """Calculate volume z-score."""
        volume = data['Volume']
        rolling_mean = volume.rolling(period).mean()
        rolling_std = volume.rolling(period).std()
        
        z_score = (volume.iloc[-1] - rolling_mean.iloc[-1]) / rolling_std.iloc[-1]
        return z_score if not np.isnan(z_score) else 0
    
    def _calculate_return(self, prices: pd.Series, period: int) -> float:
        """Calculate return over specified period."""
        if len(prices) <= period:
            return 0.0
        return (prices.iloc[-1] / prices.iloc[-period-1]) - 1
    
    def _calculate_momentum(self, prices: pd.Series, period: int) -> float:
        """Calculate momentum (price change over period)."""
        if len(prices) <= period:
            return 0.0
        return prices.iloc[-1] - prices.iloc[-period-1]
    
    def _calculate_roc(self, prices: pd.Series, period: int) -> float:
        """Calculate Rate of Change."""
        if len(prices) <= period:
            return 0.0
        return ((prices.iloc[-1] - prices.iloc[-period-1]) / prices.iloc[-period-1]) * 100
    
    # === Risk Metric Calculation Methods ===
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """Calculate maximum drawdown."""
        peak = prices.expanding().max()
        drawdown = (prices - peak) / peak
        return drawdown.min()
    
    def _calculate_current_drawdown(self, prices: pd.Series) -> float:
        """Calculate current drawdown from peak."""
        peak = prices.expanding().max()
        current_dd = (prices.iloc[-1] - peak.iloc[-1]) / peak.iloc[-1]
        return current_dd
    
    def _calculate_average_drawdown(self, prices: pd.Series) -> float:
        """Calculate average drawdown."""
        peak = prices.expanding().max()
        drawdown = (prices - peak) / peak
        return drawdown[drawdown < 0].mean()
    
    def _classify_volatility_regime(self, volatility: float) -> str:
        """Classify volatility regime."""
        if volatility < 0.15:
            return "low"
        elif volatility < 0.25:
            return "normal"
        elif volatility < 0.35:
            return "elevated"
        else:
            return "high"
    
    def _calculate_downside_deviation(self, returns: pd.Series, threshold: float = 0) -> float:
        """Calculate downside deviation."""
        downside_returns = returns[returns < threshold]
        if len(downside_returns) == 0:
            return 0
        return downside_returns.std()
    
    def _calculate_tail_ratio(self, returns: pd.Series) -> float:
        """Calculate tail ratio (95th percentile / 5th percentile)."""
        if len(returns) < 20:
            return 1.0
        return abs(returns.quantile(0.95)) / abs(returns.quantile(0.05))
    
    def _calculate_volume_stability(self, volume: pd.Series) -> float:
        """Calculate volume stability (coefficient of variation)."""
        if len(volume) < 20:
            return 1.0
        recent_volume = volume.tail(20)
        return recent_volume.std() / recent_volume.mean()
    
    def _estimate_price_impact(self, data: pd.DataFrame) -> float:
        """Estimate price impact based on volume and price changes."""
        if len(data) < 20:
            return 0.0
        
        recent_data = data.tail(20)
        volume_change = recent_data['Volume'].pct_change()
        price_change = recent_data['Close'].pct_change()
        
        # Simple correlation as proxy for price impact
        correlation = abs(volume_change.corr(price_change))
        return correlation if not np.isnan(correlation) else 0
    
    def _estimate_beta(self, prices: pd.Series, benchmark_ticker: str = 'SPY') -> float:
        """Estimate beta relative to market (simplified)."""
        # This is a simplified beta estimation
        # In practice, you'd fetch benchmark data and calculate properly
        returns = prices.pct_change().dropna()
        if len(returns) < 30:
            return 1.0
        
        # Use volatility as a simple proxy for beta
        volatility = returns.std() * np.sqrt(252)
        # Rough scaling: high volatility stocks tend to have higher beta
        return min(max(volatility / 0.2, 0.5), 2.0)  # Clamp between 0.5 and 2.0
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio."""
        if len(returns) < 2:
            return 0.0
        
        excess_return = returns.mean() * 252 - risk_free_rate
        volatility = returns.std() * np.sqrt(252)
        
        return excess_return / volatility if volatility > 0 else 0
    
    def _calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio (downside deviation)."""
        if len(returns) < 2:
            return 0.0
        
        excess_return = returns.mean() * 252 - risk_free_rate
        downside_dev = self._calculate_downside_deviation(returns) * np.sqrt(252)
        
        return excess_return / downside_dev if downside_dev > 0 else 0
    
    # === News Effectiveness Calculation Methods ===
    
    def _calculate_failed_breakouts(self, data: pd.DataFrame) -> float:
        """Calculate frequency of failed breakouts."""
        if len(data) < 50:
            return 0.0
        
        # Simple proxy: days that close below previous day's low after high volume
        failed_signals = 0
        total_signals = 0
        
        for i in range(20, len(data)):
            # Check for potential breakout (high > previous high)
            if data['High'].iloc[i] > data['High'].iloc[i-1]:
                total_signals += 1
                # Check if it failed (close below previous low)
                if data['Close'].iloc[i] < data['Low'].iloc[i-1]:
                    failed_signals += 1
        
        return failed_signals / total_signals if total_signals > 0 else 0
    
    def _calculate_resistance_strength(self, data: pd.DataFrame) -> float:
        """Calculate resistance level strength."""
        if len(data) < 20:
            return 0.0
        
        # Look at recent highs and how often they're rejected
        recent_data = data.tail(20)
        current_price = recent_data['Close'].iloc[-1]
        
        # Find recent highs
        highs = recent_data['High'].sort_values(ascending=False).head(5)
        
        # Calculate how often price fails to break through highs
        rejections = 0
        for high in highs:
            if current_price < high:
                rejections += 1
        
        return rejections / len(highs)
    
    def _calculate_news_effectiveness_score(self, proxies: Dict[str, float]) -> float:
        """Calculate composite news effectiveness score."""
        # Higher score = "good news not working" (bad for stock)
        score = 0
        
        # Weight different factors
        score += proxies.get('up_day_vol_ratio', 0) * 0.2
        score += (1 - proxies.get('high_volume_win_rate', 0.5)) * 0.15
        score += abs(proxies.get('avg_intraday_weakness', 0)) * 0.15
        score += proxies.get('gap_down_frequency', 0) * 0.1
        score += proxies.get('failed_breakout_frequency', 0) * 0.1
        score += proxies.get('volume_price_divergence', 0) * 0.15
        score += proxies.get('resistance_strength', 0) * 0.15
        
        return min(max(score, 0), 1)  # Clamp between 0 and 1
    
    def _check_data_quality(self, data: pd.DataFrame) -> int:
        """Check for missing trading days."""
        if len(data) < 2:
            return 0
        
        # Count expected trading days (rough estimate)
        date_range = (data.index[-1] - data.index[0]).days
        expected_trading_days = date_range * 5 / 7  # Weekdays only
        
        missing_days = max(0, int(expected_trading_days - len(data)))
        return missing_days


def print_market_data_summary(market_data: MarketData):
    """Print a comprehensive summary of market data."""
    print(f"\n{'='*80}")
    print(f"📊 MARKET DATA SUMMARY - {market_data.ticker}")
    print(f"{'='*80}")
    
    print(f"\n📋 Data Overview:")
    print(f"  Period: {market_data.metadata['start_date']} to {market_data.metadata['end_date']}")
    print(f"  Data Points: {market_data.metadata['data_points']}")
    print(f"  Data Quality: {market_data.metadata['data_quality']}")
    print(f"  Missing Days: {market_data.metadata['missing_days']}")
    
    print(f"\n💰 Current Price: ${market_data.current_price:.2f}")
    
    print(f"\n📈 Technical Indicators:")
    indicators = market_data.indicators
    print(f"  RSI(14): {indicators.get('rsi_14', 0):.1f}")
    print(f"  50/200 DMA Trend: {indicators.get('trend_50_200', 'unknown')}")
    print(f"  Price vs 50DMA: {indicators.get('price_vs_sma_50', 0):+.1%}")
    print(f"  Price vs 200DMA: {indicators.get('price_vs_sma_200', 0):+.1%}")
    print(f"  20D High: ${indicators.get('high_20d', 0):.2f}")
    print(f"  20D Low: ${indicators.get('low_20d', 0):.2f}")
    print(f"  Position in 20D Range: {indicators.get('position_20d_high', 0):.1%}")
    print(f"  ATR(14): ${indicators.get('atr_14', 0):.2f} ({indicators.get('atr_pct', 0):.1%})")
    print(f"  Volume Z-Score: {indicators.get('volume_z_score', 0):.2f}")
    
    print(f"\n📊 Returns:")
    for period in [5, 10, 21, 63]:
        ret = indicators.get(f'return_{period}d', 0)
        print(f"  {period}D: {ret:+.1%}")
    
    print(f"\n⚠️ Risk Metrics:")
    risk = market_data.risk_metrics
    print(f"  Max Drawdown: {risk.get('max_drawdown', 0):.1%}")
    print(f"  Current Drawdown: {risk.get('current_drawdown', 0):.1%}")
    print(f"  Volatility (20D): {risk.get('realized_vol_20d', 0):.1%}")
    print(f"  Volatility Regime: {risk.get('volatility_regime', 'unknown')}")
    print(f"  Downside Deviation: {risk.get('downside_deviation', 0):.3f}")
    print(f"  VaR (95%): {risk.get('var_95', 0):.2%}")
    print(f"  Sharpe Ratio (20D): {risk.get('sharpe_ratio_20d', 0):.2f}")
    print(f"  Beta Estimate: {risk.get('beta_estimate', 0):.2f}")
    
    print(f"\n📰 News Effectiveness ('Good News Not Working'):")
    news_eff = market_data.news_effectiveness
    print(f"  Composite Score: {news_eff.get('news_effectiveness_score', 0):.2f}")
    print(f"  Up-Day Volatility Ratio: {news_eff.get('up_day_vol_ratio', 0):.2f}")
    print(f"  High Volume Win Rate: {news_eff.get('high_volume_win_rate', 0):.1%}")
    print(f"  Intraday Weakness: {news_eff.get('avg_intraday_weakness', 0):.3f}")
    print(f"  Gap Down Frequency: {news_eff.get('gap_down_frequency', 0):.1%}")
    print(f"  Failed Breakout Freq: {news_eff.get('failed_breakout_frequency', 0):.1%}")
    print(f"  Volume-Price Divergence: {news_eff.get('volume_price_divergence', 0):.2f}")
    print(f"  Resistance Strength: {news_eff.get('resistance_strength', 0):.2f}")


def main():
    """Demonstrate the market data processor."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive market data processing")
    parser.add_argument("tickers", nargs="+", help="Tickers to process")
    parser.add_argument("--days", type=int, default=252, help="Number of days to analyze")
    parser.add_argument("--save", action="store_true", help="Save data to CSV")
    
    args = parser.parse_args()
    
    processor = MarketDataProcessor()
    
    for ticker in args.tickers:
        try:
            market_data = processor.fetch_and_process(ticker, args.days)
            print_market_data_summary(market_data)
            
            if args.save:
                filename = f"{ticker}_market_data_{args.days}d.csv"
                market_data.data.to_csv(filename)
                print(f"\n💾 Data saved to: {filename}")
                
        except Exception as e:
            print(f"❌ Error processing {ticker}: {e}")


if __name__ == "__main__":
    main()
