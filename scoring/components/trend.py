from __future__ import annotations

from typing import List, Tuple

from domain.models import FeatureVector
from scoring.scorer import ScoreComponent


class TrendComponent(ScoreComponent):
    def compute(self, features: FeatureVector) -> Tuple[float, List[str]]:
        if not features.technical:
            return 0.0, ["No technical data available"]
        
        score = 0.0
        reasons = []
        
        price_vs_sma_50 = features.technical.get("price_vs_sma_50", 0.0)
        price_vs_sma_200 = features.technical.get("price_vs_sma_200", 0.0)
        
        if price_vs_sma_50 > 0.05:
            score += 0.3
            reasons.append(f"Above SMA50 by {price_vs_sma_50:.1%}")
        elif price_vs_sma_50 < -0.05:
            score -= 0.3
            reasons.append(f"Below SMA50 by {abs(price_vs_sma_50):.1%}")
        
        if price_vs_sma_200 > 0.10:
            score += 0.4
            reasons.append(f"Above SMA200 by {price_vs_sma_200:.1%}")
        elif price_vs_sma_200 < -0.10:
            score -= 0.4
            reasons.append(f"Below SMA200 by {abs(price_vs_sma_200):.1%}")
        
        sma_50 = features.technical.get("sma_50", 0.0)
        sma_200 = features.technical.get("sma_200", 0.0)
        
        if sma_50 > 0 and sma_200 > 0:
            if sma_50 > sma_200 * 1.02:
                score += 0.2
                reasons.append("Golden cross: SMA50 > SMA200")
            elif sma_50 < sma_200 * 0.98:
                score -= 0.2
                reasons.append("Death cross: SMA50 < SMA200")
        
        return max(-1.0, min(1.0, score)), reasons
