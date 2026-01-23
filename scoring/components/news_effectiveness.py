from __future__ import annotations

from typing import List, Tuple

from domain.models import FeatureVector
from scoring.scorer import ScoreComponent


class NewsEffectivenessComponent(ScoreComponent):
    def compute(self, features: FeatureVector) -> Tuple[float, List[str]]:
        if not features.reactions:
            return 0.0, ["No reaction data available"]
        
        score = 0.0
        reasons = []
        
        positive_reactions = [r for r in features.reactions if r.event.sentiment > 0.3]
        negative_reactions = [r for r in features.reactions if r.event.sentiment < -0.3]
        
        if positive_reactions:
            worked = sum(1 for r in positive_reactions if r.verdict == "Worked")
            failed = sum(1 for r in positive_reactions if r.verdict == "Failed")
            
            if worked + failed > 0:
                effectiveness = worked / (worked + failed)
                
                if effectiveness < 0.3:
                    score -= 0.5
                    reasons.append(f"Good news not working: {effectiveness:.1%} success rate")
                elif effectiveness > 0.7:
                    score += 0.3
                    reasons.append(f"Good news working well: {effectiveness:.1%} success rate")
        
        if negative_reactions:
            worked = sum(1 for r in negative_reactions if r.verdict == "Worked")
            failed = sum(1 for r in negative_reactions if r.verdict == "Failed")
            
            if worked + failed > 0:
                effectiveness = worked / (worked + failed)
                
                if effectiveness > 0.7:
                    score -= 0.3
                    reasons.append(f"Bad news working: {effectiveness:.1%} (bearish)")
        
        return max(-1.0, min(1.0, score)), reasons
