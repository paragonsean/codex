from __future__ import annotations

from typing import List, Tuple

from domain.models import FeatureVector
from scoring.scorer import ScoreComponent


class MomentumComponent(ScoreComponent):
    def compute(self, features: FeatureVector) -> Tuple[float, List[str]]:
        if not features.technical:
            return 0.0, ["No technical data available"]
        
        score = 0.0
        reasons = []
        
        ret_5d = features.technical.get("return_5d", 0.0)
        ret_21d = features.technical.get("return_21d", 0.0)
        
        if ret_5d > 0.05:
            score += 0.3
            reasons.append(f"Strong 5-day momentum: {ret_5d:.1%}")
        elif ret_5d < -0.05:
            score -= 0.3
            reasons.append(f"Weak 5-day momentum: {ret_5d:.1%}")
        
        if ret_21d > 0.10:
            score += 0.3
            reasons.append(f"Strong 21-day momentum: {ret_21d:.1%}")
        elif ret_21d < -0.10:
            score -= 0.3
            reasons.append(f"Weak 21-day momentum: {ret_21d:.1%}")
        
        momentum_5d = features.technical.get("momentum_5d", 0.0)
        if abs(momentum_5d) > 5.0:
            if momentum_5d > 0:
                score += 0.2
                reasons.append("Accelerating upward momentum")
            else:
                score -= 0.2
                reasons.append("Accelerating downward momentum")
        
        return max(-1.0, min(1.0, score)), reasons
