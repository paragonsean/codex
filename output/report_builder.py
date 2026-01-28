from __future__ import annotations

from typing import Dict, List, Optional

from domain.models import FeatureVector, NewsEvent, Recommendation, ReactionRecord, SignalScore
from features.semiconductor_indicators import SemiconductorIndicators
try:
    from features.mining_stock_indicators import MiningStockIndicators, MINING_UNIVERSE
except Exception:
    MiningStockIndicators = None
    MINING_UNIVERSE = {}


class ReportBuilder:
    def build_analysis_report(
        self,
        ticker: str,
        features: FeatureVector,
        signal: SignalScore,
        recommendation: Recommendation,
        price_df: Optional[any] = None,
        news_events: Optional[List[NewsEvent]] = None,
    ) -> Dict[str, any]:
        semiconductor_analysis = None
        mining_stock_analysis = None
        
        if price_df is not None and not price_df.empty:
            current_price = float(price_df['Close'].iloc[-1]) if 'Close' in price_df.columns else 0.0
            semiconductor_analysis = SemiconductorIndicators.analyze_semiconductor_cycle_risk(
                ticker, price_df, current_price
            )
            
            # Check if this is a mining stock and add mining analysis
            mining_stock_analysis = self._build_mining_stock_analysis(ticker, price_df)
        else:
            current_price = None
        
        return {
            "ticker": ticker,
            "timestamp": features.asof.isoformat(),
            "regime": features.regime.value,
            "technical_summary": self._build_technical_summary(features),
            "news_summary": self._build_news_summary(features),
            "news_events": self._build_news_events(news_events, price_df),
            "news_weekly_metrics": self._build_weekly_news_metrics(news_events, price_df, features),
            "reaction_summary": self._build_reaction_summary(features),
            "semiconductor_analysis": semiconductor_analysis,
            "mining_stock_analysis": mining_stock_analysis,
            "signal_scores": {
                "opportunity": signal.opportunity,
                "sell_risk": signal.sell_risk,
                "bias": signal.bias,
                "confidence": signal.confidence.value,
            },
            "recommendation": {
                "action": recommendation.action.value,
                "confidence": recommendation.confidence,
                "reasons": recommendation.reasons,
                "tier": recommendation.tier,
                "urgency": recommendation.urgency,
                "key_levels": recommendation.key_levels,
                "position_sizing": recommendation.position_sizing,
                "hedge_suggestions": recommendation.hedge_suggestions,
            },
        }

    def _build_technical_summary(self, features: FeatureVector) -> Dict[str, any]:
        if not features.technical:
            return {}
        
        tech = features.technical
        summary = {
            "rsi_14": tech.get("rsi_14", 0.0),
            "rsi_trend": tech.get("rsi_trend", "neutral"),
            "rsi_weekly_values": tech.get("rsi_weekly_values", []),
            "price_vs_sma_50": tech.get("price_vs_sma_50", 0.0),
            "price_vs_sma_200": tech.get("price_vs_sma_200", 0.0),
            "volatility_20d": tech.get("volatility_20d", 0.0),
            "max_drawdown": tech.get("max_drawdown", 0.0),
            "current_drawdown": tech.get("current_drawdown", 0.0),
            "volume_z_score": tech.get("volume_z_score", 0.0),
        }
        
        return summary

    def _build_news_summary(self, features: FeatureVector) -> Dict[str, any]:
        if not features.news:
            return {}
        
        return {
            "total_count": features.news.get("total_count", 0),
            "avg_sentiment": features.news.get("avg_sentiment", 0.0),
            "avg_quality": features.news.get("avg_quality", 0.0),
            "positive_count": features.news.get("positive_count", 0),
            "negative_count": features.news.get("negative_count", 0),
            "neutral_count": features.news.get("neutral_count", 0),
        }
    
    def _build_news_events(self, news_events: Optional[List[NewsEvent]], price_df: Optional[any] = None) -> List[Dict[str, any]]:
        """Extract all news events with full details for display in reports."""
        if not news_events:
            return []
        
        from datetime import datetime, timedelta, timezone
        import pandas as pd
        
        # Get current time and price
        now = datetime.now(timezone.utc)
        current_price = None
        if price_df is not None and not price_df.empty and 'Close' in price_df.columns:
            current_price = float(price_df['Close'].iloc[-1])
        
        # Get all news events
        events = []
        for event in news_events:
            # Classify sentiment as Positive/Negative/Neutral
            if event.sentiment > 0.1:
                sentiment_label = "Positive"
            elif event.sentiment < -0.1:
                sentiment_label = "Negative"
            else:
                sentiment_label = "Neutral"
            
            # Calculate price change since publication (for articles > 1 day old)
            price_change = None
            days_ago = None
            if event.published_ts and price_df is not None and not price_df.empty:
                # Make published_ts timezone-aware if needed
                pub_ts = event.published_ts
                if pub_ts.tzinfo is None:
                    pub_ts = pub_ts.replace(tzinfo=timezone.utc)
                
                time_since_pub = now - pub_ts
                days_ago = time_since_pub.total_seconds() / 86400  # Convert to days
                
                # Only calculate price change if article is more than 1 day old
                if days_ago > 1 and current_price is not None:
                    # Find the price on the day the article was published
                    try:
                        # Convert published timestamp to pandas Timestamp for comparison
                        pub_date = pd.Timestamp(pub_ts)
                        
                        # Ensure price_df index is timezone-aware for comparison
                        if price_df.index.tz is None:
                            price_df_tz = price_df.copy()
                            price_df_tz.index = price_df_tz.index.tz_localize(timezone.utc)
                        else:
                            price_df_tz = price_df
                        
                        # Find the closest price on or before publication date
                        prices_before = price_df_tz[price_df_tz.index <= pub_date]
                        if not prices_before.empty and 'Close' in prices_before.columns:
                            pub_price = float(prices_before['Close'].iloc[-1])
                            price_change = ((current_price - pub_price) / pub_price) * 100
                    except Exception:
                        # If we can't calculate price change, leave it as None
                        pass
            
            events.append({
                "title": event.title,
                "published_ts": event.published_ts.strftime("%Y-%m-%d %H:%M") if event.published_ts else "Unknown",
                "source": event.source or "Unknown",
                "sentiment": sentiment_label,
                "sentiment_score": event.sentiment,  # Keep numeric score for reference
                "quality": event.quality,
                "url": event.url,
                "price_change": price_change,
                "days_ago": days_ago,
            })
        
        return events
    
    def _build_weekly_news_metrics(self, news_events: Optional[List[NewsEvent]], price_df: Optional[any] = None, features: Optional[any] = None) -> Dict[str, any]:
        """Calculate comprehensive weekly news metrics for last 4 weeks."""
        if not news_events:
            return {"weeks": []}
        
        from datetime import datetime, timedelta, timezone
        import pandas as pd
        
        # Get current time
        now = datetime.now(timezone.utc)
        
        # Initialize 4 weeks of data
        weeks = []
        for week_num in range(4):
            week_start = now - timedelta(days=(week_num + 1) * 7)
            week_end = now - timedelta(days=week_num * 7)
            
            # Filter events for this week
            week_events = []
            for event in news_events:
                pub_ts = event.published_ts
                if pub_ts:
                    if pub_ts.tzinfo is None:
                        pub_ts = pub_ts.replace(tzinfo=timezone.utc)
                    if week_start <= pub_ts < week_end:
                        week_events.append(event)
            
            # Calculate metrics for this week
            total_count = len(week_events)
            positive_count = sum(1 for e in week_events if e.sentiment > 0.1)
            negative_count = sum(1 for e in week_events if e.sentiment < -0.1)
            neutral_count = total_count - positive_count - negative_count
            
            avg_sentiment = sum(e.sentiment for e in week_events) / total_count if total_count > 0 else 0.0
            avg_quality = sum(e.quality for e in week_events) / total_count if total_count > 0 else 0.0
            
            # Calculate sentiment trend (positive - negative)
            sentiment_balance = positive_count - negative_count
            
            # High quality news count (quality > 0.7)
            high_quality_count = sum(1 for e in week_events if e.quality > 0.7)
            
            # Calculate price change for this week
            price_change = None
            week_rsi = None
            if price_df is not None and not price_df.empty:
                # Get price data for this week
                week_start_date = pd.Timestamp(week_start).tz_localize(None) if pd.Timestamp(week_start).tz is None else pd.Timestamp(week_start).tz_convert(None)
                week_end_date = pd.Timestamp(week_end).tz_localize(None) if pd.Timestamp(week_end).tz is None else pd.Timestamp(week_end).tz_convert(None)
                
                # Ensure price_df index is timezone-naive for comparison
                price_df_copy = price_df.copy()
                if hasattr(price_df_copy.index, 'tz') and price_df_copy.index.tz is not None:
                    price_df_copy.index = price_df_copy.index.tz_localize(None)
                
                week_data = price_df_copy[(price_df_copy.index >= week_start_date) & (price_df_copy.index < week_end_date)]
                
                if not week_data.empty and 'Close' in week_data.columns:
                    start_price = float(week_data['Close'].iloc[0])
                    end_price = float(week_data['Close'].iloc[-1])
                    price_change = ((end_price - start_price) / start_price) * 100 if start_price > 0 else 0.0
                    
                    # Calculate RSI using the full price dataset up to the end of this week
                    try:
                        # Get all data up to the end of this week
                        data_up_to_week_end = price_df_copy[price_df_copy.index < week_end_date]
                        
                        if len(data_up_to_week_end) >= 14 and 'Close' in data_up_to_week_end.columns:
                            # Calculate RSI(14) for the full dataset
                            delta = data_up_to_week_end['Close'].diff()
                            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                            rs = gain / loss
                            rsi_series = 100 - (100 / (1 + rs))
                            # Get the RSI value at the end of the week
                            if not rsi_series.empty and not pd.isna(rsi_series.iloc[-1]):
                                week_rsi = float(rsi_series.iloc[-1])
                    except:
                        week_rsi = None
            
            weeks.append({
                "week_num": week_num + 1,  # Week 1 is most recent
                "week_label": f"Week {week_num + 1}",
                "week_start": week_start.strftime("%Y-%m-%d"),
                "week_end": week_end.strftime("%Y-%m-%d"),
                "total_count": total_count,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count,
                "avg_sentiment": avg_sentiment,
                "avg_quality": avg_quality,
                "sentiment_balance": sentiment_balance,
                "high_quality_count": high_quality_count,
                "price_change": price_change,
                "rsi": week_rsi,
            })
        
        # Reverse to show oldest to newest
        weeks.reverse()
        
        # Calculate trends
        total_counts = [w["total_count"] for w in weeks]
        positive_counts = [w["positive_count"] for w in weeks]
        negative_counts = [w["negative_count"] for w in weeks]
        sentiment_balances = [w["sentiment_balance"] for w in weeks]
        
        # Calculate week-over-week changes (most recent vs previous)
        if len(weeks) >= 2:
            recent_week = weeks[-1]
            prev_week = weeks[-2]
            
            total_change = recent_week["total_count"] - prev_week["total_count"]
            positive_change = recent_week["positive_count"] - prev_week["positive_count"]
            negative_change = recent_week["negative_count"] - prev_week["negative_count"]
            sentiment_change = recent_week["avg_sentiment"] - prev_week["avg_sentiment"]
        else:
            total_change = 0
            positive_change = 0
            negative_change = 0
            sentiment_change = 0.0
        
        return {
            "weeks": weeks,
            "total_counts": total_counts,
            "positive_counts": positive_counts,
            "negative_counts": negative_counts,
            "sentiment_balances": sentiment_balances,
            "week_over_week": {
                "total_change": total_change,
                "positive_change": positive_change,
                "negative_change": negative_change,
                "sentiment_change": sentiment_change,
            },
        }

    def _build_reaction_summary(self, features: FeatureVector) -> Dict[str, any]:
        if not features.reactions:
            return {"count": 0}
        
        worked = sum(1 for r in features.reactions if r.verdict == "Worked")
        failed = sum(1 for r in features.reactions if r.verdict == "Failed")
        absorbed = sum(1 for r in features.reactions if r.verdict == "Absorbed")
        
        return {
            "count": len(features.reactions),
            "worked": worked,
            "failed": failed,
            "absorbed": absorbed,
            "effectiveness": worked / (worked + failed) if (worked + failed) > 0 else 0.0,
        }

    def _build_mining_stock_analysis(self, ticker: str, price_df) -> Optional[Dict[str, any]]:
        """Build mining stock analysis if ticker is in the mining universe."""
        if MiningStockIndicators is None:
            return None
        # Check if ticker is a mining stock (handle .AX suffix for ASX stocks)
        ticker_key = ticker.replace(".AX", "")
        
        if ticker_key not in MINING_UNIVERSE:
            return None
        
        stock = MINING_UNIVERSE[ticker_key]
        
        # Calculate indicators
        momentum = MiningStockIndicators.calculate_price_momentum(price_df, ticker)
        
        # Calculate semi demand score (use default cycle phase MID)
        semi_demand = MiningStockIndicators.calculate_semi_demand_score(
            ticker=ticker,
            semi_cycle_phase="MID",
            ev_growth_yoy=20.0,  # Default assumption
            ai_capex_growth_yoy=30.0,  # Default assumption
        )
        
        # Build composite from available indicators
        indicators = [momentum, semi_demand]
        composite = MiningStockIndicators.calculate_composite_signal(indicators)
        
        return {
            "is_mining_stock": True,
            "stock_info": {
                "ticker": ticker,
                "name": stock.name,
                "mineral": stock.mineral.value,
                "semi_sensitivity": stock.semi_sensitivity.value,
                "primary_exposure": stock.primary_exposure,
                "key_assets": stock.key_assets,
                "description": stock.description,
            },
            "momentum": {
                "current_price": momentum.evidence.get("current_price", 0),
                "rsi": momentum.evidence.get("rsi", 50),
                "trend": momentum.evidence.get("trend", "neutral"),
                "vs_ma20_pct": momentum.evidence.get("vs_ma20_pct", 0),
                "vs_ma50_pct": momentum.evidence.get("vs_ma50_pct", 0),
                "vs_ma200_pct": momentum.evidence.get("vs_ma200_pct", 0),
                "pct_off_high": momentum.evidence.get("pct_off_high", 0),
                "pct_off_low": momentum.evidence.get("pct_off_low", 0),
                "direction": momentum.direction.value,
                "alert": momentum.alert,
            },
            "semi_demand": {
                "score": semi_demand.evidence.get("total_score", 0),
                "sensitivity_weight": semi_demand.evidence.get("sensitivity_weight", 0),
                "direction": semi_demand.direction.value,
                "alert": semi_demand.alert,
            },
            "composite": composite,
        }
