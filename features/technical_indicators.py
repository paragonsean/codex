from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
import pandas as pd


class TechnicalIndicators:
    @staticmethod
    def calculate_rsi(series: pd.Series, period: int = 14) -> float:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0

    @staticmethod
    def calculate_sma(series: pd.Series, period: int) -> float:
        sma = series.rolling(period).mean().iloc[-1]
        return float(sma) if not pd.isna(sma) else 0.0

    @staticmethod
    def calculate_ema(series: pd.Series, period: int) -> float:
        ema = series.ewm(span=period).mean().iloc[-1]
        return float(ema) if not pd.isna(ema) else 0.0

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean().iloc[-1]
        
        return float(atr) if not pd.isna(atr) else 0.0

    @staticmethod
    def calculate_max_drawdown(series: pd.Series) -> float:
        cummax = series.cummax()
        drawdown = (series - cummax) / cummax
        return float(drawdown.min()) if len(drawdown) > 0 else 0.0

    @staticmethod
    def calculate_current_drawdown(series: pd.Series) -> float:
        cummax = series.cummax()
        current_dd = (series.iloc[-1] - cummax.iloc[-1]) / cummax.iloc[-1]
        return float(current_dd)

    @staticmethod
    def calculate_volume_zscore(df: pd.DataFrame, window: int = 20) -> float:
        volume = df['Volume']
        mean = volume.rolling(window).mean()
        std = volume.rolling(window).std()
        
        if std.iloc[-1] == 0:
            return 0.0
        
        zscore = (volume.iloc[-1] - mean.iloc[-1]) / std.iloc[-1]
        return float(zscore) if not pd.isna(zscore) else 0.0

    @staticmethod
    def calculate_volatility(returns: pd.Series, window: int = 20) -> float:
        vol = returns.rolling(window).std() * np.sqrt(252)
        return float(vol.iloc[-1]) if not pd.isna(vol.iloc[-1]) else 0.0

    @staticmethod
    def calculate_momentum(series: pd.Series, period: int) -> float:
        if len(series) < period + 1:
            return 0.0
        momentum = series.iloc[-1] - series.iloc[-period - 1]
        return float(momentum)

    @staticmethod
    def calculate_rsi_history(series: pd.Series, period: int = 14, weeks: int = 8) -> Dict[str, any]:
        """Calculate RSI with weekly history for trend analysis."""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
        
        weekly_rsi = []
        days_per_week = 5
        total_days = weeks * days_per_week
        
        if len(rsi) >= total_days:
            for i in range(weeks):
                week_start = -(total_days - i * days_per_week)
                week_end = week_start + days_per_week
                if week_end == 0:
                    week_end = None
                week_data = rsi.iloc[week_start:week_end]
                if len(week_data) > 0:
                    weekly_avg = float(week_data.mean())
                    weekly_rsi.append(weekly_avg)
        
        return {
            "current": current_rsi,
            "weekly_values": weekly_rsi,
            "trend": TechnicalIndicators._determine_trend(weekly_rsi),
        }
    
    @staticmethod
    def _determine_trend(values: List[float]) -> str:
        """Determine if values are rising, falling, or neutral."""
        if len(values) < 3:
            return "neutral"
        
        recent_3 = values[-3:]
        if recent_3[2] > recent_3[1] > recent_3[0]:
            return "rising"
        elif recent_3[2] < recent_3[1] < recent_3[0]:
            return "falling"
        elif recent_3[2] > recent_3[0]:
            return "rising"
        elif recent_3[2] < recent_3[0]:
            return "falling"
        else:
            return "neutral"

    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> Dict[str, float]:
        indicators = {}
        
        close = df['Close']
        current_price = float(close.iloc[-1])
        
        indicators['rsi_14'] = TechnicalIndicators.calculate_rsi(close, 14)
        
        rsi_history = TechnicalIndicators.calculate_rsi_history(close, 14, 8)
        indicators['rsi_weekly_values'] = rsi_history['weekly_values']
        indicators['rsi_trend'] = rsi_history['trend']
        
        indicators['sma_50'] = TechnicalIndicators.calculate_sma(close, 50)
        indicators['sma_200'] = TechnicalIndicators.calculate_sma(close, 200)
        indicators['ema_20'] = TechnicalIndicators.calculate_ema(close, 20)
        indicators['ema_50'] = TechnicalIndicators.calculate_ema(close, 50)
        
        indicators['price_vs_sma_50'] = (
            (current_price - indicators['sma_50']) / indicators['sma_50']
            if indicators['sma_50'] > 0 else 0.0
        )
        indicators['price_vs_sma_200'] = (
            (current_price - indicators['sma_200']) / indicators['sma_200']
            if indicators['sma_200'] > 0 else 0.0
        )
        
        indicators['atr_14'] = TechnicalIndicators.calculate_atr(df, 14)
        indicators['atr_pct'] = (
            indicators['atr_14'] / current_price if current_price > 0 else 0.0
        )

        # Key levels used by SemiconductorPolicy
        if len(df) >= 1:
            if 'High' in df.columns:
                indicators['high_20d'] = float(df['High'].rolling(20).max().iloc[-1]) if len(df) >= 20 else float(df['High'].max())
            else:
                indicators['high_20d'] = float(close.rolling(20).max().iloc[-1]) if len(close) >= 20 else float(close.max())

            if 'Low' in df.columns:
                indicators['low_20d'] = float(df['Low'].rolling(20).min().iloc[-1]) if len(df) >= 20 else float(df['Low'].min())
            else:
                indicators['low_20d'] = float(close.rolling(20).min().iloc[-1]) if len(close) >= 20 else float(close.min())
        
        indicators['volume_z_score'] = TechnicalIndicators.calculate_volume_zscore(df, 20)
        
        # Volatility: compute from close-to-close returns (don't require a precomputed Return column)
        returns = close.pct_change().dropna()
        indicators['volatility_20d'] = TechnicalIndicators.calculate_volatility(returns, 20)
        indicators['volatility_50d'] = TechnicalIndicators.calculate_volatility(returns, 50)
        
        indicators['max_drawdown'] = TechnicalIndicators.calculate_max_drawdown(close)
        indicators['current_drawdown'] = TechnicalIndicators.calculate_current_drawdown(close)
        
        for period in [5, 10, 21, 63]:
            if len(close) >= period + 1:
                ret = (close.iloc[-1] - close.iloc[-period - 1]) / close.iloc[-period - 1]
                indicators[f'return_{period}d'] = float(ret)
        
        indicators['momentum_5d'] = TechnicalIndicators.calculate_momentum(close, 5)
        indicators['momentum_21d'] = TechnicalIndicators.calculate_momentum(close, 21)
        
        return indicators
    
    @staticmethod
    def get_rsi_weekly_summary(df: pd.DataFrame, weeks: int = 8) -> str:
        """Generate human-readable RSI weekly summary."""
        rsi_history = TechnicalIndicators.calculate_rsi_history(df['Close'], 14, weeks)
        
        current = rsi_history['current']
        weekly = rsi_history['weekly_values']
        trend = rsi_history['trend']
        
        summary = f"Current RSI: {current:.1f} ({trend})\n"
        summary += "Past {weeks} weeks: "
        summary += ", ".join([f"{val:.1f}" for val in weekly[-weeks:]])
        
        return summary
