from __future__ import annotations

from typing import List, Tuple

from domain.models import FeatureVector
from scoring.scorer import ScoreComponent


class DistributionComponent(ScoreComponent):
    def compute(self, features: FeatureVector) -> Tuple[float, List[str]]:
        if not features.technical:
            return 0.0, ["No technical data available"]
        
        score = 0.0
        reasons = []
        
        volume_z = features.technical.get("volume_z_score", 0.0)
        ret_5d = features.technical.get("return_5d", 0.0)
        
        if volume_z > 2.0 and ret_5d < -0.03:
            score -= 0.4
            reasons.append(f"Distribution signal: high volume ({volume_z:.1f}σ) + down {ret_5d:.1%}")
        elif volume_z > 2.0 and ret_5d > 0.03:
            score += 0.3
            reasons.append(f"Accumulation signal: high volume ({volume_z:.1f}σ) + up {ret_5d:.1%}")
        
        max_dd = features.technical.get("max_drawdown", 0.0)
        if max_dd < -0.30:
            score -= 0.2
            reasons.append(f"Severe max drawdown: {max_dd:.1%}")
        
        return max(-1.0, min(1.0, score)), reasons
