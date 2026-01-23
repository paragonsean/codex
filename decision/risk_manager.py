from __future__ import annotations

from typing import Dict, List, Optional

from domain.models import Recommendation
from domain.portfolio import Portfolio, PortfolioContext


class RiskManager:
    def __init__(
        self,
        max_position_pct: float = 0.15,
        max_sector_pct: float = 0.40,
        min_cash_buffer: float = 0.10,
    ):
        self.max_position_pct = max_position_pct
        self.max_sector_pct = max_sector_pct
        self.min_cash_buffer = min_cash_buffer

    def validate_recommendation(
        self,
        recommendation: Recommendation,
        portfolio_ctx: Optional[PortfolioContext] = None,
    ) -> tuple[bool, List[str]]:
        if portfolio_ctx is None:
            return True, []
        
        violations = []
        
        if recommendation.action.value == "buy":
            violations.extend(self._check_concentration_limits(recommendation, portfolio_ctx))
            violations.extend(self._check_cash_buffer(recommendation, portfolio_ctx))
        
        is_valid = len(violations) == 0
        return is_valid, violations

    def _check_concentration_limits(
        self, recommendation: Recommendation, portfolio_ctx: PortfolioContext
    ) -> List[str]:
        violations = []
        
        if portfolio_ctx.sector_weights:
            semiconductor_weight = portfolio_ctx.sector_weights.get("semiconductor", 0.0)
            if semiconductor_weight >= self.max_sector_pct:
                violations.append(
                    f"Sector concentration limit: {semiconductor_weight:.1%} >= {self.max_sector_pct:.1%}"
                )
        
        return violations

    def _check_cash_buffer(
        self, recommendation: Recommendation, portfolio_ctx: PortfolioContext
    ) -> List[str]:
        violations = []
        
        if portfolio_ctx.cash is not None and portfolio_ctx.total_value is not None:
            cash_pct = portfolio_ctx.cash / portfolio_ctx.total_value
            if cash_pct < self.min_cash_buffer:
                violations.append(
                    f"Cash buffer too low: {cash_pct:.1%} < {self.min_cash_buffer:.1%}"
                )
        
        return violations

    def compute_max_drawdown_limit(self, portfolio_ctx: PortfolioContext) -> float:
        return -0.20

    def check_portfolio_risk(self, portfolio_ctx: PortfolioContext) -> Dict[str, any]:
        risk_metrics = {
            "concentration_ok": True,
            "cash_buffer_ok": True,
            "warnings": [],
        }
        
        if portfolio_ctx.sector_weights:
            for sector, weight in portfolio_ctx.sector_weights.items():
                if weight > self.max_sector_pct:
                    risk_metrics["concentration_ok"] = False
                    risk_metrics["warnings"].append(
                        f"Sector {sector} over limit: {weight:.1%}"
                    )
        
        if portfolio_ctx.cash is not None and portfolio_ctx.total_value is not None:
            cash_pct = portfolio_ctx.cash / portfolio_ctx.total_value
            if cash_pct < self.min_cash_buffer:
                risk_metrics["cash_buffer_ok"] = False
                risk_metrics["warnings"].append(
                    f"Cash buffer below minimum: {cash_pct:.1%}"
                )
        
        return risk_metrics
