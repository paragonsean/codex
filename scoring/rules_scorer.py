from __future__ import annotations

from typing import List, Optional

from domain.enums import Confidence
from domain.models import FeatureVector, SignalScore
from scoring.components import (
    DistributionComponent,
    MomentumComponent,
    NewsEffectivenessComponent,
    NewsSentimentComponent,
    OverheatComponent,
    TrendComponent,
)
from scoring.scorer import ScoreComponent


class RulesScorer:
    def __init__(self, components: Optional[List[ScoreComponent]] = None):
        if components is None:
            self.components = [
                MomentumComponent(),
                TrendComponent(),
                OverheatComponent(),
                DistributionComponent(),
                NewsSentimentComponent(),
                NewsEffectivenessComponent(),
            ]
        else:
            self.components = components

    def score(self, features: FeatureVector) -> SignalScore:
        all_reasons = []
        opportunity_score = 0.0
        sell_risk_score = 0.0
        
        for component in self.components:
            comp_score, reasons = component.compute(features)
            all_reasons.extend(reasons)
            
            if comp_score > 0:
                opportunity_score += comp_score
            else:
                sell_risk_score += abs(comp_score)
        
        opportunity_score = max(0.0, min(100.0, opportunity_score * 20))
        sell_risk_score = max(0.0, min(100.0, sell_risk_score * 20))
        
        bias = self._determine_bias(opportunity_score, sell_risk_score)
        confidence = self._determine_confidence(opportunity_score, sell_risk_score)
        
        return SignalScore(
            ticker=features.ticker,
            opportunity=opportunity_score,
            sell_risk=sell_risk_score,
            bias=bias,
            confidence=confidence,
            contributors=all_reasons,
            metadata={
                "regime": features.regime.value,
                "component_count": len(self.components),
            },
        )

    def _determine_bias(self, opportunity: float, sell_risk: float) -> str:
        net = opportunity - sell_risk
        
        if net > 20:
            return "bullish"
        elif net < -20:
            return "bearish"
        else:
            return "neutral"

    def _determine_confidence(self, opportunity: float, sell_risk: float) -> Confidence:
        total_signal = opportunity + sell_risk
        
        if total_signal > 60:
            return Confidence.HIGH
        elif total_signal > 30:
            return Confidence.MEDIUM
        else:
            return Confidence.LOW
