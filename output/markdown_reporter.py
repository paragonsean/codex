from __future__ import annotations

from typing import Any, Dict, List, Optional

from domain.models import ReactionRecord


class MarkdownReporter:
    def render_analysis_report(self, report_data: Dict[str, any]) -> str:
        md = f"""# 🎯 {report_data['ticker']} Advanced Stock Analysis Report

**Generated:** {report_data['timestamp']}  
**Regime:** {report_data['regime'].upper()}

---

## 📊 Signal Scores

| Metric | Value |
|--------|-------|
| **Opportunity Score** | {report_data['signal_scores']['opportunity']:.1f}/100 |
| **Sell-Risk Score** | {report_data['signal_scores']['sell_risk']:.1f}/100 |
| **Overall Bias** | {report_data['signal_scores']['bias'].upper()} |
| **Confidence** | {report_data['signal_scores']['confidence'].upper()} |

---

## 🎯 Recommendation

### **{report_data['recommendation']['action'].upper()}**

- **Confidence:** {report_data['recommendation']['confidence']:.1%}
- **Urgency:** {report_data['recommendation'].get('urgency', 'normal').upper()}
"""
        
        if report_data['recommendation'].get('tier'):
            md += f"- **Tier:** {report_data['recommendation']['tier'].replace('_', ' ').upper()}\n"
        
        md += "\n### 💡 Key Reasons:\n\n"
        
        for i, reason in enumerate(report_data['recommendation']['reasons'][:5], 1):
            md += f"{i}. {reason}\n"
        
        if report_data['recommendation'].get('key_levels'):
            md += "\n---\n\n## 📍 Key Levels\n\n"
            for level_type, level_value in report_data['recommendation']['key_levels'].items():
                if level_value and level_value != 0.0:
                    md += f"- **{level_type.replace('_', ' ').title()}:** ${level_value:.2f}\n"
        
        md += "\n---\n\n## 📈 Technical Summary\n\n| Indicator | Value |\n|-----------|-------|\n"
        
        for key, value in report_data.get('technical_summary', {}).items():
            if isinstance(value, float):
                md += f"| **{key.replace('_', ' ').title()}** | {value:.4f} |\n"
            else:
                md += f"| **{key.replace('_', ' ').title()}** | {value} |\n"
        
        md += "\n---\n\n## 📰 News Summary\n\n| Metric | Value |\n|--------|-------|\n"
        
        for key, value in report_data.get('news_summary', {}).items():
            if isinstance(value, float):
                md += f"| **{key.replace('_', ' ').title()}** | {value:.4f} |\n"
            else:
                md += f"| **{key.replace('_', ' ').title()}** | {value} |\n"
        
        # Add news articles section
        if report_data.get('news_events'):
            num_articles = len(report_data['news_events'])
            md += f"\n---\n\n## 📰 Recent News Articles ({num_articles} articles)\n\n"
            md += "| # | Headline | Published | Source | Sentiment | Price Change | Quality |\n"
            md += "|---|----------|-----------|--------|-----------|--------------|---------|\n"
            
            for idx, event in enumerate(report_data['news_events'], 1):
                sentiment_label = event['sentiment']
                sentiment_emoji = '📈' if sentiment_label == 'Positive' else '📉' if sentiment_label == 'Negative' else '➡️'
                sentiment_str = f"{sentiment_emoji} {sentiment_label}"
                quality_emoji = '🟢' if event['quality'] > 0.7 else '🟡' if event['quality'] > 0.4 else '⚪'
                quality_str = f"{quality_emoji} {event['quality']:.2f}"
                
                # Format price change if available (for articles > 1 day old)
                price_change_str = "-"
                if event.get('price_change') is not None:
                    price_change = event['price_change']
                    change_emoji = '🟢' if price_change > 0 else '🔴' if price_change < 0 else '⚪'
                    price_change_str = f"{change_emoji} {price_change:+.2f}%"
                
                # Truncate long titles
                title = event['title']
                if len(title) > 70:
                    title = title[:67] + "..."
                
                md += f"| {idx} | [{title}]({event['url']}) | {event['published_ts']} | {event['source']} | {sentiment_str} | {price_change_str} | {quality_str} |\n"
            
            md += "\n*Price change shown for articles published more than 1 day ago*\n"
        
        # Add weekly news metrics section
        if report_data.get('news_weekly_metrics') and report_data['news_weekly_metrics'].get('weeks'):
            weekly_metrics = report_data['news_weekly_metrics']
            md += "\n---\n\n## 📈 Weekly News Trends (Last 4 Weeks)\n\n"
            md += "| Week | Period | Total | Positive | Negative | Neutral | Balance | Avg Quality | Price Change | RSI |\n"
            md += "|------|--------|-------|----------|----------|---------|---------|-------------|--------------|-----|\n"
            
            for week in weekly_metrics['weeks']:
                balance = week['sentiment_balance']
                balance_emoji = '📈' if balance > 0 else '📉' if balance < 0 else '➡️'
                quality_emoji = '🟢' if week['avg_quality'] > 0.7 else '🟡' if week['avg_quality'] > 0.4 else '⚪'
                
                # Format price change
                price_change_str = "-"
                if week.get('price_change') is not None:
                    pc = week['price_change']
                    price_change_emoji = '📈' if pc > 0 else '📉' if pc < 0 else '➡️'
                    price_change_str = f"{price_change_emoji} {pc:+.2f}%"
                
                # Format RSI
                rsi_str = "-"
                if week.get('rsi') is not None:
                    rsi = week['rsi']
                    rsi_str = f"{rsi:.1f}"
                
                md += f"| {week['week_label']} | {week['week_start']} to {week['week_end']} | "
                md += f"**{week['total_count']}** | {week['positive_count']} | {week['negative_count']} | {week['neutral_count']} | "
                md += f"{balance_emoji} {balance:+d} | {quality_emoji} {week['avg_quality']:.2f} | {price_change_str} | {rsi_str} |\n"
            
            # Add week-over-week changes
            wow = weekly_metrics['week_over_week']
            md += "\n### Week-over-Week Changes\n\n"
            md += "| Metric | Change |\n"
            md += "|--------|--------|\n"
            
            total_change = wow['total_change']
            positive_change = wow['positive_change']
            negative_change = wow['negative_change']
            sentiment_change = wow['sentiment_change']
            
            total_emoji = '📈' if total_change > 0 else '📉' if total_change < 0 else '➡️'
            pos_emoji = '📈' if positive_change > 0 else '📉' if positive_change < 0 else '➡️'
            neg_emoji = '📉' if negative_change > 0 else '📈' if negative_change < 0 else '➡️'
            sent_emoji = '📈' if sentiment_change > 0 else '📉' if sentiment_change < 0 else '➡️'
            
            md += f"| **Total Articles** | {total_emoji} {total_change:+d} |\n"
            md += f"| **Positive Articles** | {pos_emoji} {positive_change:+d} |\n"
            md += f"| **Negative Articles** | {neg_emoji} {negative_change:+d} |\n"
            md += f"| **Avg Sentiment** | {sent_emoji} {sentiment_change:+.3f} |\n"
        
        if report_data.get('semiconductor_analysis'):
            semi = report_data['semiconductor_analysis']
            rsi_data = semi['rsi_analysis']
            
            md += f"""
---

## 🔴 Semiconductor Cycle Risk Analysis

| Metric | Value |
|--------|-------|
| **Stock Type** | {'Memory Stock' if semi['is_memory_stock'] else 'Non-Memory Semiconductor'} |
| **Cycle Risk Score** | {semi['cycle_risk_score']} ({semi['risk_level'].upper()}) |
| **Total Risk Points** | {semi['total_risk_points']:.0f} |
| **Total Opportunity Points** | {semi['total_opportunity_points']:.0f} |

### 📊 Key Risk Drivers & Opportunities

{semi.get('driver_summary', 'No significant drivers detected.')}

### 📊 RSI Trend Analysis (Past 8 Weeks)

| Metric | Value |
|--------|-------|
| **Current RSI** | {rsi_data.evidence.get('current_rsi', 50):.1f} |
| **RSI Trend** | {rsi_data.evidence.get('trend_direction', 'neutral').upper()} |
| **Weeks Above 75** | {rsi_data.evidence.get('weeks_above_75', 0)} |
| **Risk Points** | {rsi_data.risk_points} |

### 📊 Position vs 20-Day High (Exhaustion Signal)

| Metric | Value |
|--------|-------|
| **Current Position** | {semi['exhaustion_analysis'].evidence.get('position_vs_20d_high', 0):.1%} |
| **Days Above 98%** | {semi['exhaustion_analysis'].evidence.get('days_above_threshold', 0)} |
| **Exhaustion Status** | {'EXHAUSTED' if semi['exhaustion_analysis'].evidence.get('is_exhausted', False) else 'NORMAL'} |
| **Exhaustion Risk Points** | {semi['exhaustion_analysis'].risk_points} |
"""
            
            if semi['exhaustion_analysis'].alert:
                md += f"\n> {semi['exhaustion_analysis'].alert}\n"
            
            md += f"""\n### 📉 RSI Divergence (Early Momentum Decay)\n\n| Metric | Value |\n|--------|-------|\n| **Divergence Type** | {semi['divergence_analysis'].evidence.get('divergence_type', 'none').upper() if semi['divergence_analysis'].evidence.get('divergence_type') != 'none' else 'NONE DETECTED'} |\n| **Divergence Risk Points** | {semi['divergence_analysis'].risk_points} |\n"""
            
            if semi['divergence_analysis'].alert:
                md += f"\n> {semi['divergence_analysis'].alert}\n"
            
            md += f"""\n### 📉 ROC Compression (Cycle Aging)\n\n| Metric | Value |\n|--------|-------|\n| **Compression Status** | {semi['roc_compression_analysis'].evidence.get('severity', 'none').upper()} |\n| **ROC Risk Points** | {semi['roc_compression_analysis'].risk_points} |\n"""
            
            if semi['roc_compression_analysis'].evidence.get('current_roc'):
                md += "\n#### Current ROC vs Baseline:\n\n"
                for period_key, current_val in semi['roc_compression_analysis'].evidence.get('current_roc', {}).items():
                    period_label = period_key.replace('roc_', '').replace('d', 'D')
                    early_val = semi['roc_compression_analysis'].evidence.get('baseline_roc', {}).get(period_key, 0)
                    ratio = semi['roc_compression_analysis'].evidence.get('compression_ratio', {}).get(period_key, 0)
                    
                    indicator = "🔴" if ratio < 0.5 else "🟡" if ratio < 0.8 else "🟢"
                    md += f"- **{period_label}**: Current {current_val:.2f}% | Baseline {early_val:.2f}% | Ratio **{ratio:.2f}** {indicator}\n"
            
            if semi['roc_compression_analysis'].alert:
                md += f"\n> {semi['roc_compression_analysis'].alert}\n"
            
            md += f"""\n### 💚 RSI 55-70 Zone (Institutional Accumulation Band)\n\n| Metric | Value |\n|--------|-------|\n| **Trend Health** | {semi['accumulation_zone_analysis'].evidence.get('trend_health', 'unknown').upper()} |\n| **Current RSI** | {semi['accumulation_zone_analysis'].evidence.get('current_rsi', 50):.1f} |\n| **Zone Visits (Last 20D)** | {semi['accumulation_zone_analysis'].evidence.get('zone_visits_last_20d', 0)} |\n| **Days Since Zone** | {semi['accumulation_zone_analysis'].evidence.get('days_since_zone', 0)} |\n| **Zone Risk Points** | {semi['accumulation_zone_analysis'].risk_points} |\n"""
            
            if semi['accumulation_zone_analysis'].alert:
                md += f"\n> {semi['accumulation_zone_analysis'].alert}\n"
            
            md += f"""\n### 📊 Trend Persistence (% Time Above 50DMA)\n\n| Metric | Value |\n|--------|-------|\n| **Trend Strength** | {semi['trend_persistence_analysis'].evidence.get('trend_strength', 'unknown').upper()} |\n| **Persistence Declining** | {'YES - Internal Erosion' if semi['trend_persistence_analysis'].evidence.get('persistence_declining', False) else 'NO'} |\n| **Persistence Risk Points** | {semi['trend_persistence_analysis'].risk_points} |\n"""
            
            if semi['trend_persistence_analysis'].evidence.get('pct_above_50dma'):
                md += "\n#### % Time Above 50DMA:\n\n"
                for period_key, pct_val in semi['trend_persistence_analysis'].evidence.get('pct_above_50dma', {}).items():
                    period_label = period_key.replace('d', 'D')
                    indicator = "🟢" if pct_val >= 80 else "🟡" if pct_val >= 60 else "🔴"
                    md += f"- **{period_label}**: {pct_val:.1f}% {indicator}\n"
            
            if semi['trend_persistence_analysis'].alert:
                md += f"\n> {semi['trend_persistence_analysis'].alert}\n"
            
            # DMA Failure section
            md += "\n### 🔴 First 50DMA Failure (Cycle Turn Trigger)\n\n"
            md += "| Metric | Value |\n|--------|-------|\n"
            md += f"| **Currently Below 50DMA** | {'YES' if semi['dma_failure_analysis'].evidence.get('currently_below_50dma', False) else 'NO'} |\n"
            md += f"| **First Failure After Long Uptrend** | {'YES - Cycle Turn' if semi['dma_failure_analysis'].evidence.get('is_first_failure', False) else 'NO'} |\n"
            md += f"| **Previous Uptrend Days** | {semi['dma_failure_analysis'].evidence.get('previous_uptrend_days', 0)} |\n"
            md += f"| **Days in Current Streak** | {semi['dma_failure_analysis'].evidence.get('days_in_current_streak', 0)} |\n"
            md += f"| **Failure Severity** | {semi['dma_failure_analysis'].evidence.get('failure_severity', 'none').upper()} |\n"
            md += f"| **50DMA Failure Risk Points** | {semi['dma_failure_analysis'].risk_points} |\n"
            
            if semi['dma_failure_analysis'].alert:
                md += f"\n> {semi['dma_failure_analysis'].alert}\n"
            
            # ATR Expansion section
            md += "\n### 📊 ATR Expansion (Distribution Signature)\n\n"
            md += "| Metric | Value |\n|--------|-------|\n"
            md += f"| **ATR (14-day)** | ${semi['atr_expansion_analysis'].evidence.get('atr_14', 0):.2f} |\n"
            md += f"| **ATR % of Price** | {semi['atr_expansion_analysis'].evidence.get('atr_pct_price', 0):.2f}% |\n"
            md += f"| **ATR Z-Score** | {semi['atr_expansion_analysis'].evidence.get('atr_zscore_60d', 0):.2f} |\n"
            md += f"| **Position vs 20D High** | {semi['atr_expansion_analysis'].evidence.get('near_highs', 0):.1%} |\n"
            md += f"| **ATR Risk Points** | {semi['atr_expansion_analysis'].risk_points} |\n"
            
            if semi['atr_expansion_analysis'].alert:
                md += f"\n> {semi['atr_expansion_analysis'].alert}\n"
            
            md += f"""\n### 📏 MA Extension (Rubber-Band Risk)\n\n| Metric | Value |\n|--------|-------|\n| **Extension Level** | {semi['ma_extension_analysis'].evidence.get('extension_level', 'unknown').upper()} |\n| **% Above 21DMA** | {f"{semi['ma_extension_analysis'].evidence.get('pct_above_21dma'):.1f}%" if semi['ma_extension_analysis'].evidence.get('pct_above_21dma') is not None else 'N/A'} |\n| **% Above 50DMA** | {f"{semi['ma_extension_analysis'].evidence.get('pct_above_50dma'):.1f}%" if semi['ma_extension_analysis'].evidence.get('pct_above_50dma') is not None else 'N/A'} |\n| **% Above 200DMA** | {f"{semi['ma_extension_analysis'].evidence.get('pct_above_200dma'):.1f}%" if semi['ma_extension_analysis'].evidence.get('pct_above_200dma') is not None else 'N/A'} |\n| **Extension Risk Points** | {semi['ma_extension_analysis'].risk_points} |\n"""
            
            if semi['ma_extension_analysis'].alert:
                md += f"\n> {semi['ma_extension_analysis'].alert}\n"
            
            md += f"""\n### 📈 Volatility Regime (Two-Way Trade Detector)\n\n| Metric | Value |\n|--------|-------|\n| **Vol Regime** | {semi['vol_regime_analysis'].evidence.get('regime', 'unknown').upper()} |\n| **20D Annualized Vol** | {semi['vol_regime_analysis'].evidence.get('vol_20_ann', 0):.1f}% |\n| **Baseline Vol** | {semi['vol_regime_analysis'].evidence.get('vol_baseline_120', 0):.1f}% |\n| **Vol Ratio** | {semi['vol_regime_analysis'].evidence.get('vol_ratio', 0):.2f}x |\n| **Vol Risk Points** | {semi['vol_regime_analysis'].risk_points} |\n"""
            
            if semi['vol_regime_analysis'].alert:
                md += f"\n> {semi['vol_regime_analysis'].alert}\n"
            
            md += "\n"
            
            if rsi_data.evidence.get('weekly_rsi'):
                md += "\n#### Weekly RSI Values:\n\n"
                for i, val in enumerate(rsi_data.evidence.get('weekly_rsi', []), 1):
                    indicator = "🔴" if val > 75 else "🟢" if val < 25 else "⚪"
                    md += f"- Week {i}: **{val:.1f}** {indicator}\n"
            
            if rsi_data.alert:
                md += f"\n#### ⚠️ Alert:\n\n> {rsi_data.alert}\n"
            
            if semi.get('recommendations'):
                md += "\n#### 💡 Cycle-Based Recommendations:\n\n"
                for i, rec in enumerate(semi['recommendations'], 1):
                    md += f"{i}. {rec}\n"
        
        if report_data.get('reaction_summary', {}).get('count', 0) > 0:
            md += f"""\n---\n\n## 📊 News Reaction Analysis\n\n| Metric | Value |\n|--------|-------|\n| **Total Reactions Analyzed** | {report_data['reaction_summary']['count']} |\n| **Worked** | {report_data['reaction_summary']['worked']} |\n| **Failed** | {report_data['reaction_summary']['failed']} |\n| **Absorbed** | {report_data['reaction_summary']['absorbed']} |\n| **Effectiveness** | {report_data['reaction_summary']['effectiveness']:.1%} |\n"""
        
        md += "\n---\n\n*Report generated by Advanced Trading System*\n"
        
        return md

    def render_reaction_table(self, reactions: list[ReactionRecord]) -> str:
        if not reactions:
            return "No reaction data available.\n"
        
        md = """
| Published (ET) | Headline | Sentiment | Session | 0→Close | 1D | 3D | 5D | Verdict |
|----------------|----------|-----------|---------|---------|----|----|----|---------|\n"""
        
        for reaction in reactions:
            published_et = reaction.event.published_ts.strftime("%Y-%m-%d %H:%M")
            headline = reaction.event.title[:50] + "..." if len(reaction.event.title) > 50 else reaction.event.title
            sentiment = f"{reaction.event.sentiment:.2f}"
            session = reaction.session
            
            ret_0 = self._format_return(reaction.forward_returns.get("0_close"))
            ret_1d = self._format_return(reaction.forward_returns.get("1d"))
            ret_3d = self._format_return(reaction.forward_returns.get("3d"))
            ret_5d = self._format_return(reaction.forward_returns.get("5d"))
            
            verdict = reaction.verdict or "N/A"
            
            md += f"| {published_et} | {headline} | {sentiment} | {session} | {ret_0} | {ret_1d} | {ret_3d} | {ret_5d} | {verdict} |\n"
        
        return md

    def _format_return(self, value: float | None) -> str:
        if value is None:
            return "N/A"
        
        pct = value * 100
        return f"{pct:+.2f}%"
