from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from domain.models import FeatureVector, Recommendation, SignalScore
from domain.portfolio import PortfolioContext


class Policy(ABC):
    @abstractmethod
    def recommend(
        self,
        signal: SignalScore,
        features: FeatureVector,
        portfolio_ctx: Optional[PortfolioContext] = None,
    ) -> Recommendation:
        """
        Generate a trading recommendation based on signal scores and features.
        
        Args:
            signal: Computed signal scores (opportunity, sell_risk, etc.)
            features: Full feature vector with technical/news/reactions
            portfolio_ctx: Optional portfolio context for position sizing
            
        Returns:
            Recommendation with action, confidence, reasons, etc.
        """
        pass
