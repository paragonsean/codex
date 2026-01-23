from __future__ import annotations

from typing import List, Optional

from domain.enums import ActionType, Confidence
from domain.models import FeatureVector, Recommendation, SignalScore
from domain.portfolio import PortfolioContext
from decision.policy import Policy


class SemiconductorPolicy(Policy):
    def __init__(
        self,
        opportunity_buy_threshold: float = 60.0,
        sell_risk_trim_threshold: float = 60.0,
        sell_risk_sell_threshold: float = 80.0,
    ):
        self.opportunity_buy_threshold = opportunity_buy_threshold
        self.sell_risk_trim_threshold = sell_risk_trim_threshold
        self.sell_risk_sell_threshold = sell_risk_sell_threshold

    def recommend(
        self,
        signal: SignalScore,
        features: FeatureVector,
        portfolio_ctx: Optional[PortfolioContext] = None,
    ) -> Recommendation:
        reasons = []
        action = ActionType.HOLD
        confidence = 0.5
        tier = None
        urgency = "normal"
        
        if signal.sell_risk >= self.sell_risk_sell_threshold:
            action = ActionType.SELL
            confidence = 0.8
            urgency = "high"
            reasons.append(f"High sell risk: {signal.sell_risk:.1f}")
            reasons.extend(self._extract_sell_risk_reasons(signal))
        
        elif signal.sell_risk >= self.sell_risk_trim_threshold:
            action = ActionType.TRIM
            confidence = 0.7
            urgency = "medium"
            reasons.append(f"Elevated sell risk: {signal.sell_risk:.1f}")
            reasons.extend(self._extract_sell_risk_reasons(signal))
        
        elif signal.opportunity >= self.opportunity_buy_threshold:
            action = ActionType.BUY
            confidence = 0.75
            tier = self._determine_buy_tier(signal.opportunity)
            reasons.append(f"Strong opportunity: {signal.opportunity:.1f}")
            reasons.extend(self._extract_opportunity_reasons(signal))
        
        else:
            action = ActionType.HOLD
            confidence = 0.5
            reasons.append(f"Neutral signal: opp={signal.opportunity:.1f}, risk={signal.sell_risk:.1f}")
        
        segment = self._detect_semiconductor_segment(features)
        if segment:
            reasons.append(f"Segment: {segment}")
            action, confidence = self._adjust_for_segment(action, confidence, segment, features)
        
        key_levels = self._compute_key_levels(features)
        position_sizing = self._compute_position_sizing(signal, features, portfolio_ctx)
        hedge_suggestions = self._compute_hedge_suggestions(signal, features)
        
        return Recommendation(
            ticker=features.ticker,
            action=action,
            confidence=confidence,
            reasons=reasons,
            tier=tier,
            urgency=urgency,
            key_levels=key_levels,
            next_review_date=None,
            position_sizing=position_sizing,
            hedge_suggestions=hedge_suggestions,
            metadata={
                "signal_opportunity": signal.opportunity,
                "signal_sell_risk": signal.sell_risk,
                "signal_bias": signal.bias,
                "regime": features.regime.value,
                "segment": segment,
            },
        )

    def _extract_sell_risk_reasons(self, signal: SignalScore) -> List[str]:
        if not signal.contributors:
            return []
        
        risk_keywords = ["downward", "below", "overbought", "distribution", "not working", "negative"]
        return [r for r in signal.contributors if any(kw in r.lower() for kw in risk_keywords)][:3]

    def _extract_opportunity_reasons(self, signal: SignalScore) -> List[str]:
        if not signal.contributors:
            return []
        
        opp_keywords = ["upward", "above", "oversold", "accumulation", "working", "positive"]
        return [r for r in signal.contributors if any(kw in r.lower() for kw in opp_keywords)][:3]

    def _determine_buy_tier(self, opportunity: float) -> str:
        if opportunity >= 80:
            return "tier_1"
        elif opportunity >= 70:
            return "tier_2"
        else:
            return "tier_3"

    def _detect_semiconductor_segment(self, features: FeatureVector) -> Optional[str]:
        ticker = features.ticker.upper()
        
        memory_tickers = {"MU", "WDC", "STX"}
        equipment_tickers = {"AMAT", "LRCX", "KLAC", "ASML"}
        eda_tickers = {"CDNS", "SNPS"}
        foundry_tickers = {"TSM", "INTC"}
        
        if ticker in memory_tickers:
            return "memory"
        elif ticker in equipment_tickers:
            return "equipment"
        elif ticker in eda_tickers:
            return "eda"
        elif ticker in foundry_tickers:
            return "foundry"
        
        return None

    def _adjust_for_segment(
        self, action: ActionType, confidence: float, segment: str, features: FeatureVector
    ) -> tuple[ActionType, float]:
        if segment == "memory":
            if features.regime.value in ("elevated", "high"):
                confidence *= 0.9
        
        elif segment == "equipment":
            if action == ActionType.BUY:
                confidence *= 1.1
        
        return action, min(1.0, confidence)

    def _compute_key_levels(self, features: FeatureVector) -> dict:
        if not features.technical:
            return {}
        
        return {
            "sma_50": features.technical.get("sma_50", 0.0),
            "sma_200": features.technical.get("sma_200", 0.0),
            "high_20d": features.technical.get("high_20d", 0.0),
            "low_20d": features.technical.get("low_20d", 0.0),
        }

    def _compute_position_sizing(
        self,
        signal: SignalScore,
        features: FeatureVector,
        portfolio_ctx: Optional[PortfolioContext],
    ) -> dict:
        base_size = 1.0
        
        if signal.confidence == Confidence.HIGH:
            base_size = 1.5
        elif signal.confidence == Confidence.LOW:
            base_size = 0.5
        
        volatility = features.technical.get("volatility_20d", 0.3) if features.technical else 0.3
        vol_adjustment = max(0.5, min(1.5, 0.3 / volatility))
        
        adjusted_size = base_size * vol_adjustment
        
        return {
            "base_size": base_size,
            "volatility_adjustment": vol_adjustment,
            "suggested_size": adjusted_size,
        }

    def _compute_hedge_suggestions(self, signal: SignalScore, features: FeatureVector) -> List[str]:
        suggestions = []
        
        if signal.sell_risk > 50:
            suggestions.append("Consider hedging with SOXX puts")
        
        if features.regime.value == "high":
            suggestions.append("High volatility regime: consider reducing position size")
        
        return suggestions
