from __future__ import annotations

from typing import List, Tuple

from domain.models import FeatureVector
from scoring.scorer import ScoreComponent


class OverheatComponent(ScoreComponent):
    def compute(self, features: FeatureVector) -> Tuple[float, List[str]]:
        if not features.technical:
            return 0.0, ["No technical data available"]
        
        score = 0.0
        reasons = []
        
        rsi_14 = features.technical.get("rsi_14", 50.0)
        
        if rsi_14 > 70:
            penalty = min(0.5, (rsi_14 - 70) / 30 * 0.5)
            score -= penalty
            reasons.append(f"Overbought: RSI={rsi_14:.1f}")
        elif rsi_14 < 30:
            bonus = min(0.5, (30 - rsi_14) / 30 * 0.5)
            score += bonus
            reasons.append(f"Oversold: RSI={rsi_14:.1f}")
        
        current_dd = features.technical.get("current_drawdown", 0.0)
        if current_dd < -0.20:
            score += 0.3
            reasons.append(f"Deep drawdown: {current_dd:.1%}")
        
        volatility_20d = features.technical.get("volatility_20d", 0.0)
        if volatility_20d > 0.5:
            score -= 0.2
            reasons.append(f"High volatility: {volatility_20d:.1%}")
        
        return max(-1.0, min(1.0, score)), reasons
