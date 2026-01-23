from __future__ import annotations

from typing import List, Optional

from domain.models import FeatureVector, SignalScore


class RotationEngine:
    def __init__(self, rotation_threshold: float = 60.0):
        self.rotation_threshold = rotation_threshold

    def suggest_rotation_targets(
        self,
        current_ticker: str,
        current_signal: SignalScore,
        candidate_signals: List[tuple[str, SignalScore]],
    ) -> List[str]:
        if current_signal.sell_risk < self.rotation_threshold:
            return []
        
        better_candidates = [
            ticker
            for ticker, signal in candidate_signals
            if signal.opportunity > current_signal.opportunity + 10
            and signal.sell_risk < current_signal.sell_risk - 10
        ]
        
        better_candidates.sort(
            key=lambda t: next(
                (s.opportunity - s.sell_risk for ticker, s in candidate_signals if ticker == t),
                0,
            ),
            reverse=True,
        )
        
        return better_candidates[:3]

    def compute_rotation_urgency(self, signal: SignalScore) -> str:
        if signal.sell_risk >= 80:
            return "high"
        elif signal.sell_risk >= 70:
            return "medium"
        else:
            return "low"

    def suggest_defensive_rotation(
        self, features: FeatureVector
    ) -> Optional[List[str]]:
        if features.regime.value in ("elevated", "high"):
            return ["QQQ", "SOXX", "Cash"]
        
        return None
