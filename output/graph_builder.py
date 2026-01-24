"""
Graph Builder for Report Visualizations

Generates charts for stock analysis reports:
  - Price charts with moving averages
  - RSI charts with overbought/oversold zones
  - Volume charts
  - Semiconductor cycle indicators
  - Mining stock demand scores
"""

from __future__ import annotations

import base64
import io
from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for server use
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class GraphBuilder:
    """
    Builds charts for stock analysis reports.
    
    All charts are returned as base64-encoded PNG images for embedding in HTML.
    """
    
    # Color scheme
    COLORS = {
        'price': '#2196F3',
        'ma_20': '#FF9800',
        'ma_50': '#4CAF50',
        'ma_200': '#9C27B0',
        'volume_up': '#4CAF50',
        'volume_down': '#F44336',
        'rsi': '#2196F3',
        'overbought': '#F44336',
        'oversold': '#4CAF50',
        'neutral_zone': '#FFF9C4',
        'bullish': '#4CAF50',
        'bearish': '#F44336',
        'neutral': '#9E9E9E',
        'background': '#FAFAFA',
        'grid': '#E0E0E0',
    }
    
    # Default figure size
    DEFAULT_FIGSIZE = (10, 4)
    DEFAULT_DPI = 100
    
    def __init__(self, style: str = 'default'):
        """
        Initialize GraphBuilder.
        
        Args:
            style: matplotlib style to use
        """
        self.style = style
        
        if not MATPLOTLIB_AVAILABLE:
            print("Warning: matplotlib not available. Charts will not be generated.")
    
    @staticmethod
    def is_available() -> bool:
        """Check if matplotlib is available."""
        return MATPLOTLIB_AVAILABLE
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string."""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=self.DEFAULT_DPI, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close(fig)
        return img_base64
    
    def create_price_chart(
        self,
        df: pd.DataFrame,
        ticker: str,
        show_ma: bool = True,
        ma_periods: List[int] = [20, 50, 200],
        days: int = 90,
        figsize: Tuple[int, int] = None,
    ) -> Optional[str]:
        """
        Create price chart with optional moving averages.
        
        Args:
            df: DataFrame with OHLCV data
            ticker: Stock ticker symbol
            show_ma: Whether to show moving averages
            ma_periods: Moving average periods to show
            days: Number of days to display
            figsize: Figure size tuple
            
        Returns:
            Base64-encoded PNG image string, or None if unavailable
        """
        if not MATPLOTLIB_AVAILABLE or df.empty:
            return None
        
        figsize = figsize or self.DEFAULT_FIGSIZE
        fig, ax = plt.subplots(figsize=figsize)
        
        # Get recent data
        plot_df = df.tail(days).copy()
        
        # Plot price
        ax.plot(plot_df.index, plot_df['Close'], 
                color=self.COLORS['price'], linewidth=1.5, label='Price')
        
        # Plot moving averages
        if show_ma:
            ma_colors = {
                20: self.COLORS['ma_20'],
                50: self.COLORS['ma_50'],
                200: self.COLORS['ma_200'],
            }
            for period in ma_periods:
                if len(df) >= period:
                    ma = df['Close'].rolling(window=period).mean()
                    ma_plot = ma.tail(days)
                    color = ma_colors.get(period, '#666666')
                    ax.plot(ma_plot.index, ma_plot, 
                            color=color, linewidth=1, alpha=0.8,
                            label=f'MA{period}', linestyle='--')
        
        # Formatting
        ax.set_title(f'{ticker} Price Chart', fontsize=12, fontweight='bold')
        ax.set_xlabel('')
        ax.set_ylabel('Price ($)', fontsize=10)
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3, color=self.COLORS['grid'])
        ax.set_facecolor(self.COLORS['background'])
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        plt.xticks(rotation=45, ha='right', fontsize=8)
        
        # Add current price annotation
        current_price = float(plot_df['Close'].iloc[-1])
        ax.annotate(f'${current_price:.2f}', 
                    xy=(plot_df.index[-1], current_price),
                    xytext=(10, 0), textcoords='offset points',
                    fontsize=9, fontweight='bold',
                    color=self.COLORS['price'])
        
        fig.tight_layout()
        return self._fig_to_base64(fig)
    
    def create_rsi_chart(
        self,
        df: pd.DataFrame,
        ticker: str,
        period: int = 14,
        days: int = 90,
        figsize: Tuple[int, int] = None,
    ) -> Optional[str]:
        """
        Create RSI chart with overbought/oversold zones.
        
        Args:
            df: DataFrame with OHLCV data
            ticker: Stock ticker symbol
            period: RSI period
            days: Number of days to display
            figsize: Figure size tuple
            
        Returns:
            Base64-encoded PNG image string
        """
        if not MATPLOTLIB_AVAILABLE or df.empty:
            return None
        
        figsize = figsize or (self.DEFAULT_FIGSIZE[0], 3)
        fig, ax = plt.subplots(figsize=figsize)
        
        # Calculate RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        plot_rsi = rsi.tail(days)
        
        # Plot RSI line
        ax.plot(plot_rsi.index, plot_rsi, 
                color=self.COLORS['rsi'], linewidth=1.5)
        
        # Add overbought/oversold zones
        ax.axhline(y=70, color=self.COLORS['overbought'], linestyle='--', alpha=0.7, linewidth=1)
        ax.axhline(y=30, color=self.COLORS['oversold'], linestyle='--', alpha=0.7, linewidth=1)
        ax.axhline(y=50, color='#666666', linestyle=':', alpha=0.5, linewidth=1)
        
        # Fill overbought/oversold zones
        ax.fill_between(plot_rsi.index, 70, 100, alpha=0.1, color=self.COLORS['overbought'])
        ax.fill_between(plot_rsi.index, 0, 30, alpha=0.1, color=self.COLORS['oversold'])
        
        # Formatting
        ax.set_title(f'{ticker} RSI ({period})', fontsize=12, fontweight='bold')
        ax.set_ylabel('RSI', fontsize=10)
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3, color=self.COLORS['grid'])
        ax.set_facecolor(self.COLORS['background'])
        
        # Add labels
        ax.text(plot_rsi.index[0], 75, 'Overbought', fontsize=8, color=self.COLORS['overbought'])
        ax.text(plot_rsi.index[0], 25, 'Oversold', fontsize=8, color=self.COLORS['oversold'])
        
        # Current RSI value
        current_rsi = float(plot_rsi.iloc[-1])
        rsi_color = self.COLORS['overbought'] if current_rsi > 70 else self.COLORS['oversold'] if current_rsi < 30 else self.COLORS['rsi']
        ax.annotate(f'{current_rsi:.1f}', 
                    xy=(plot_rsi.index[-1], current_rsi),
                    xytext=(10, 0), textcoords='offset points',
                    fontsize=9, fontweight='bold',
                    color=rsi_color)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        plt.xticks(rotation=45, ha='right', fontsize=8)
        
        fig.tight_layout()
        return self._fig_to_base64(fig)
    
    def create_volume_chart(
        self,
        df: pd.DataFrame,
        ticker: str,
        days: int = 90,
        figsize: Tuple[int, int] = None,
    ) -> Optional[str]:
        """
        Create volume bar chart with color coding.
        
        Args:
            df: DataFrame with OHLCV data
            ticker: Stock ticker symbol
            days: Number of days to display
            figsize: Figure size tuple
            
        Returns:
            Base64-encoded PNG image string
        """
        if not MATPLOTLIB_AVAILABLE or df.empty or 'Volume' not in df.columns:
            return None
        
        figsize = figsize or (self.DEFAULT_FIGSIZE[0], 2.5)
        fig, ax = plt.subplots(figsize=figsize)
        
        plot_df = df.tail(days).copy()
        
        # Color based on price change
        colors = []
        for i in range(len(plot_df)):
            if i == 0:
                colors.append(self.COLORS['neutral'])
            elif plot_df['Close'].iloc[i] >= plot_df['Close'].iloc[i-1]:
                colors.append(self.COLORS['volume_up'])
            else:
                colors.append(self.COLORS['volume_down'])
        
        # Plot volume bars
        ax.bar(plot_df.index, plot_df['Volume'], color=colors, alpha=0.7, width=0.8)
        
        # Add volume MA
        vol_ma = plot_df['Volume'].rolling(20).mean()
        ax.plot(plot_df.index, vol_ma, color='#FF9800', linewidth=1.5, label='20-day Avg')
        
        # Formatting
        ax.set_title(f'{ticker} Volume', fontsize=12, fontweight='bold')
        ax.set_ylabel('Volume', fontsize=10)
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3, color=self.COLORS['grid'])
        ax.set_facecolor(self.COLORS['background'])
        
        # Format y-axis for large numbers
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        plt.xticks(rotation=45, ha='right', fontsize=8)
        
        fig.tight_layout()
        return self._fig_to_base64(fig)
    
    def create_combined_chart(
        self,
        df: pd.DataFrame,
        ticker: str,
        days: int = 90,
        figsize: Tuple[int, int] = None,
    ) -> Optional[str]:
        """
        Create combined price + RSI + volume chart.
        
        Args:
            df: DataFrame with OHLCV data
            ticker: Stock ticker symbol
            days: Number of days to display
            figsize: Figure size tuple
            
        Returns:
            Base64-encoded PNG image string
        """
        if not MATPLOTLIB_AVAILABLE or df.empty:
            return None
        
        figsize = figsize or (12, 8)
        fig, axes = plt.subplots(3, 1, figsize=figsize, 
                                  gridspec_kw={'height_ratios': [3, 1, 1]},
                                  sharex=True)
        
        plot_df = df.tail(days).copy()
        
        # ===== Price Chart (top) =====
        ax1 = axes[0]
        ax1.plot(plot_df.index, plot_df['Close'], 
                 color=self.COLORS['price'], linewidth=1.5, label='Price')
        
        # Moving averages
        for period, color in [(20, self.COLORS['ma_20']), (50, self.COLORS['ma_50'])]:
            if len(df) >= period:
                ma = df['Close'].rolling(window=period).mean().tail(days)
                ax1.plot(ma.index, ma, color=color, linewidth=1, 
                         alpha=0.8, label=f'MA{period}', linestyle='--')
        
        ax1.set_title(f'{ticker} Technical Analysis', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=10)
        ax1.legend(loc='upper left', fontsize=8)
        ax1.grid(True, alpha=0.3)
        
        # ===== RSI Chart (middle) =====
        ax2 = axes[1]
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        plot_rsi = rsi.tail(days)
        
        ax2.plot(plot_rsi.index, plot_rsi, color=self.COLORS['rsi'], linewidth=1.5)
        ax2.axhline(y=70, color=self.COLORS['overbought'], linestyle='--', alpha=0.7)
        ax2.axhline(y=30, color=self.COLORS['oversold'], linestyle='--', alpha=0.7)
        ax2.fill_between(plot_rsi.index, 70, 100, alpha=0.1, color=self.COLORS['overbought'])
        ax2.fill_between(plot_rsi.index, 0, 30, alpha=0.1, color=self.COLORS['oversold'])
        ax2.set_ylabel('RSI', fontsize=10)
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3)
        
        # ===== Volume Chart (bottom) =====
        ax3 = axes[2]
        colors = [self.COLORS['volume_up'] if plot_df['Close'].iloc[i] >= plot_df['Close'].iloc[max(0, i-1)] 
                  else self.COLORS['volume_down'] for i in range(len(plot_df))]
        ax3.bar(plot_df.index, plot_df['Volume'], color=colors, alpha=0.7)
        ax3.set_ylabel('Volume', fontsize=10)
        ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))
        ax3.grid(True, alpha=0.3)
        
        # Format x-axis
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        ax3.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        plt.xticks(rotation=45, ha='right', fontsize=8)
        
        fig.tight_layout()
        return self._fig_to_base64(fig)
    
    def create_gauge_chart(
        self,
        value: float,
        title: str,
        min_val: float = 0,
        max_val: float = 100,
        thresholds: List[Tuple[float, str]] = None,
        figsize: Tuple[int, int] = None,
    ) -> Optional[str]:
        """
        Create a gauge/dial chart for scores.
        
        Args:
            value: Current value to display
            title: Chart title
            min_val: Minimum value
            max_val: Maximum value
            thresholds: List of (value, color) tuples for zones
            figsize: Figure size tuple
            
        Returns:
            Base64-encoded PNG image string
        """
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        figsize = figsize or (4, 3)
        fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': 'polar'})
        
        # Default thresholds
        if thresholds is None:
            thresholds = [
                (33, self.COLORS['bearish']),
                (66, '#FFC107'),
                (100, self.COLORS['bullish']),
            ]
        
        # Create gauge background
        theta = np.linspace(np.pi, 0, 100)
        
        prev_thresh = 0
        for thresh, color in thresholds:
            mask = (np.linspace(min_val, max_val, 100) >= prev_thresh) & (np.linspace(min_val, max_val, 100) <= thresh)
            ax.fill_between(theta[mask], 0.5, 1.0, color=color, alpha=0.3)
            prev_thresh = thresh
        
        # Draw gauge needle
        value_normalized = (value - min_val) / (max_val - min_val)
        needle_angle = np.pi - value_normalized * np.pi
        ax.annotate('', xy=(needle_angle, 0.9), xytext=(needle_angle, 0.1),
                    arrowprops=dict(arrowstyle='->', color='#333', lw=2))
        
        # Add value text
        ax.text(np.pi/2, 0.3, f'{value:.0f}', ha='center', va='center',
                fontsize=20, fontweight='bold')
        ax.text(np.pi/2, 0.1, title, ha='center', va='center', fontsize=10)
        
        # Configure polar plot
        ax.set_ylim(0, 1)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_thetamin(0)
        ax.set_thetamax(180)
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.spines['polar'].set_visible(False)
        ax.grid(False)
        
        fig.tight_layout()
        return self._fig_to_base64(fig)
    
    def create_signal_bar_chart(
        self,
        risk_points: int,
        opportunity_points: int,
        title: str = "Signal Breakdown",
        figsize: Tuple[int, int] = None,
    ) -> Optional[str]:
        """
        Create horizontal bar chart for risk vs opportunity.
        
        Args:
            risk_points: Total risk points
            opportunity_points: Total opportunity points
            title: Chart title
            figsize: Figure size tuple
            
        Returns:
            Base64-encoded PNG image string
        """
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        figsize = figsize or (6, 2)
        fig, ax = plt.subplots(figsize=figsize)
        
        # Data
        categories = ['Opportunity', 'Risk']
        values = [opportunity_points, risk_points]
        colors = [self.COLORS['bullish'], self.COLORS['bearish']]
        
        # Create horizontal bars
        bars = ax.barh(categories, values, color=colors, height=0.5)
        
        # Add value labels
        for bar, val in zip(bars, values):
            ax.text(val + 1, bar.get_y() + bar.get_height()/2, 
                    f'{val}', va='center', fontweight='bold')
        
        # Net signal annotation
        net = opportunity_points - risk_points
        net_color = self.COLORS['bullish'] if net > 0 else self.COLORS['bearish'] if net < 0 else self.COLORS['neutral']
        ax.axvline(x=0, color='#333', linewidth=0.5)
        
        ax.set_title(f'{title} (Net: {net:+d})', fontsize=12, fontweight='bold')
        ax.set_xlabel('Points')
        ax.grid(True, alpha=0.3, axis='x')
        ax.set_facecolor(self.COLORS['background'])
        
        fig.tight_layout()
        return self._fig_to_base64(fig)
    
    def create_mining_demand_chart(
        self,
        stocks: List[Dict],
        title: str = "Mining Stock Demand Scores",
        figsize: Tuple[int, int] = None,
    ) -> Optional[str]:
        """
        Create bar chart comparing mining stock demand scores.
        
        Args:
            stocks: List of dicts with 'ticker', 'score', 'sensitivity'
            title: Chart title
            figsize: Figure size tuple
            
        Returns:
            Base64-encoded PNG image string
        """
        if not MATPLOTLIB_AVAILABLE or not stocks:
            return None
        
        figsize = figsize or (8, 4)
        fig, ax = plt.subplots(figsize=figsize)
        
        # Sort by score
        stocks = sorted(stocks, key=lambda x: x.get('score', 0), reverse=True)
        
        tickers = [s['ticker'] for s in stocks]
        scores = [s.get('score', 0) for s in stocks]
        
        # Color by sensitivity
        sensitivity_colors = {
            'Very High': '#FF5722',
            'High': '#FF9800',
            'Medium': '#FFC107',
            'Low': '#9E9E9E',
        }
        colors = [sensitivity_colors.get(s.get('sensitivity', 'Low'), '#9E9E9E') for s in stocks]
        
        # Create bars
        bars = ax.bar(tickers, scores, color=colors, edgecolor='white', linewidth=1)
        
        # Add score labels
        for bar, score in zip(bars, scores):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{score:.0f}', ha='center', va='bottom', fontweight='bold')
        
        # Reference lines
        ax.axhline(y=60, color=self.COLORS['bullish'], linestyle='--', alpha=0.5, label='Strong (60+)')
        ax.axhline(y=40, color='#FFC107', linestyle='--', alpha=0.5, label='Neutral (40-60)')
        
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_ylabel('Demand Score')
        ax.set_ylim(0, 100)
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_facecolor(self.COLORS['background'])
        
        plt.xticks(rotation=45, ha='right')
        fig.tight_layout()
        return self._fig_to_base64(fig)
    
    def embed_in_html(self, base64_img: str, alt_text: str = "Chart") -> str:
        """
        Create HTML img tag from base64 image.
        
        Args:
            base64_img: Base64-encoded image string
            alt_text: Alt text for image
            
        Returns:
            HTML img tag string
        """
        if not base64_img:
            return f'<p style="color: #999; font-style: italic;">{alt_text} not available</p>'
        
        return f'<img src="data:image/png;base64,{base64_img}" alt="{alt_text}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">'
