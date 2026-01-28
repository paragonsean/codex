"""
Portfolio Cycle Risk Analyzer

Implements bucket aggregation and portfolio-level cycle risk math.
Designed to answer:
  - "Portfolio is late/peaking because 38% of weight is in PEAKING signals"
  - "Memory bucket is the source of transition risk"
  - "Even if MU looks fine alone, the portfolio needs rotation"
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from domain.portfolio import (
    BucketAction,
    BucketAnalysis,
    BucketType,
    CyclePhase,
    DEFAULT_BUCKET_LIMITS,
    PHASE_SCORES,
    PHASE_THRESHOLDS,
    PortfolioMode,
    PortfolioRiskAnalysis,
    PositionAction,
    PositionInput,
    StockCycleAnalysis,
)


class PortfolioCycleAnalyzer:
    """
    Analyzes portfolio-level cycle risk through bucket aggregation.
    
    Key formulas:
    1. Bucket weighted pressure: P_b = sum(w_i * p_i)
    2. Bucket phase score: S_b = sum(w_i * phase_score_i)
    3. Bucket transition risk: R_b = clip(base_risk * multiplier, 0, 100)
       where multiplier = 1 + 0.8 * critical_breadth
    4. Portfolio transition risk: weighted blend of pressure, phase, concentration, story risks
    """
    
    def __init__(self, bucket_limits: Optional[Dict[BucketType, float]] = None):
        """
        Initialize analyzer with bucket limit policy.
        
        Args:
            bucket_limits: Max weight per bucket (default: DEFAULT_BUCKET_LIMITS)
        """
        self.bucket_limits = bucket_limits or DEFAULT_BUCKET_LIMITS
    
    def analyze_portfolio(
        self,
        positions: List[PositionInput],
        cycle_analyses: Dict[str, StockCycleAnalysis],
        total_value: float,
    ) -> PortfolioRiskAnalysis:
        """
        Perform complete portfolio cycle risk analysis.
        
        Args:
            positions: List of portfolio positions with weights and buckets
            cycle_analyses: Stock-level cycle analysis results keyed by ticker
            total_value: Total portfolio value
            
        Returns:
            Complete portfolio risk analysis with bucket breakdowns
        """
        # 1. Analyze each bucket
        buckets = self._analyze_buckets(positions, cycle_analyses)
        
        # 2. Calculate portfolio-level metrics
        portfolio_pressure = self._calculate_portfolio_pressure(positions, cycle_analyses)
        portfolio_phase = self._score_to_phase(portfolio_pressure)
        
        # 3. Calculate risk components
        pressure_risk = self._clip(2.0 * portfolio_pressure, 0, 100)
        
        peaking_weight, peaking_tickers = self._calculate_peaking_weight(positions, cycle_analyses)
        phase_concentration_risk = self._clip(250.0 * peaking_weight, 0, 100)
        
        bucket_concentration_risk = self._calculate_bucket_concentration_risk(buckets)
        
        story_weights, max_story_concentration = self._calculate_story_concentration(positions)
        story_concentration_risk = self._clip(200.0 * max_story_concentration, 0, 100)
        
        # 4. Calculate final transition risk (weighted blend)
        transition_risk = (
            0.35 * pressure_risk +
            0.25 * phase_concentration_risk +
            0.20 * bucket_concentration_risk +
            0.20 * story_concentration_risk
        )
        
        # 5. Determine portfolio mode
        mode = self._determine_portfolio_mode(transition_risk, portfolio_phase)
        
        return PortfolioRiskAnalysis(
            total_value=total_value,
            portfolio_pressure=portfolio_pressure,
            portfolio_phase=portfolio_phase,
            pressure_risk=pressure_risk,
            phase_concentration_risk=phase_concentration_risk,
            bucket_concentration_risk=bucket_concentration_risk,
            story_concentration_risk=story_concentration_risk,
            transition_risk=transition_risk,
            mode=mode,
            buckets=buckets,
            story_weights=story_weights,
            max_story_concentration=max_story_concentration,
            peaking_weight=peaking_weight,
            peaking_tickers=peaking_tickers,
        )
    
    def _analyze_buckets(
        self,
        positions: List[PositionInput],
        cycle_analyses: Dict[str, StockCycleAnalysis],
    ) -> Dict[BucketType, BucketAnalysis]:
        """Analyze each bucket's cycle risk."""
        # Group positions by bucket
        bucket_positions = defaultdict(list)
        for pos in positions:
            bucket_positions[pos.bucket].append(pos)
        
        bucket_analyses = {}
        for bucket_type, bucket_pos in bucket_positions.items():
            bucket_analyses[bucket_type] = self._analyze_single_bucket(
                bucket_type, bucket_pos, cycle_analyses
            )
        
        return bucket_analyses
    
    def _analyze_single_bucket(
        self,
        bucket: BucketType,
        positions: List[PositionInput],
        cycle_analyses: Dict[str, StockCycleAnalysis],
    ) -> BucketAnalysis:
        """
        Analyze a single bucket.
        
        Formulas:
        - Weighted pressure: P_b = sum(w_i * p_i)
        - Phase score: S_b = sum(w_i * phase_score_i)
        - Base risk: R_base = clip(2 * P_b, 0, 100)
        - Critical breadth: B_b = sum(w_i * c_i) / sum(w_i)
        - Risk multiplier: M_b = 1 + 0.8 * B_b
        - Transition risk: R_b = clip(R_base * M_b, 0, 100)
        """
        total_weight = sum(p.weight for p in positions)
        target_max = self.bucket_limits.get(bucket, 1.0)
        overage = max(0, total_weight - target_max)
        
        # Calculate weighted pressure
        weighted_pressure = 0.0
        phase_score = 0.0
        critical_weight = 0.0
        
        contributors = []
        
        for pos in positions:
            analysis = cycle_analyses.get(pos.ticker)
            if not analysis:
                continue
            
            pressure = analysis.cycle_pressure
            weighted_pressure += pos.weight * pressure
            
            # Phase score
            pos_phase_score = PHASE_SCORES.get(analysis.phase, 0)
            phase_score += pos.weight * pos_phase_score
            
            # Critical signals
            has_critical = len(analysis.critical_signals_fired) > 0
            if has_critical:
                critical_weight += pos.weight
            
            # Track contributors
            contribution = pos.weight * pressure
            contributors.append({
                'ticker': pos.ticker,
                'weight': pos.weight,
                'pressure': pressure,
                'contribution': contribution,
                'phase': analysis.phase.value,
                'critical_signals': analysis.critical_signals_fired,
            })
        
        # Sort contributors by contribution (descending)
        contributors.sort(key=lambda x: x['contribution'], reverse=True)
        top_contributors = contributors[:5]  # Top 5
        
        # Derive bucket phase from phase score
        bucket_phase = self._score_to_phase(phase_score)
        
        # Calculate risk components
        base_risk = self._clip(2.0 * weighted_pressure, 0, 100)
        critical_breadth = critical_weight / total_weight if total_weight > 0 else 0.0
        risk_multiplier = 1.0 + 0.8 * critical_breadth
        transition_risk = self._clip(base_risk * risk_multiplier, 0, 100)
        
        return BucketAnalysis(
            bucket=bucket,
            weight=total_weight,
            target_max=target_max,
            overage=overage,
            weighted_pressure=weighted_pressure,
            phase_score=phase_score,
            phase=bucket_phase,
            base_risk=base_risk,
            critical_breadth=critical_breadth,
            risk_multiplier=risk_multiplier,
            transition_risk=transition_risk,
            top_contributors=top_contributors,
        )
    
    def _calculate_portfolio_pressure(
        self,
        positions: List[PositionInput],
        cycle_analyses: Dict[str, StockCycleAnalysis],
    ) -> float:
        """
        Calculate portfolio-level weighted cycle pressure.
        
        Formula: P_port = sum(w_i * p_i)
        Cash positions have pressure = 0.
        """
        total_pressure = 0.0
        
        for pos in positions:
            if pos.bucket == BucketType.CASH:
                continue  # Cash has 0 pressure
            
            analysis = cycle_analyses.get(pos.ticker)
            if analysis:
                total_pressure += pos.weight * analysis.cycle_pressure
        
        return total_pressure
    
    def _calculate_peaking_weight(
        self,
        positions: List[PositionInput],
        cycle_analyses: Dict[str, StockCycleAnalysis],
    ) -> Tuple[float, List[str]]:
        """Calculate total weight in PEAKING or DOWNTURN phases."""
        peaking_weight = 0.0
        peaking_tickers = []
        
        for pos in positions:
            analysis = cycle_analyses.get(pos.ticker)
            if analysis and analysis.phase in [CyclePhase.PEAKING, CyclePhase.DOWNTURN]:
                peaking_weight += pos.weight
                peaking_tickers.append(pos.ticker)
        
        return peaking_weight, peaking_tickers
    
    def _calculate_bucket_concentration_risk(
        self,
        buckets: Dict[BucketType, BucketAnalysis],
    ) -> float:
        """
        Calculate risk from bucket concentration violations.
        
        Formula: R_conc = clip(200 * sum(overages), 0, 100)
        """
        total_overage = sum(b.overage for b in buckets.values())
        return self._clip(200.0 * total_overage, 0, 100)
    
    def _calculate_story_concentration(
        self,
        positions: List[PositionInput],
    ) -> Tuple[Dict[str, float], float]:
        """
        Calculate concentration by story/theme.
        
        Returns:
            (story_weights, max_concentration)
        """
        story_weights = defaultdict(float)
        
        for pos in positions:
            for story in pos.story_tags:
                story_weights[story] += pos.weight
        
        max_concentration = max(story_weights.values()) if story_weights else 0.0
        
        return dict(story_weights), max_concentration
    
    def _determine_portfolio_mode(
        self,
        transition_risk: float,
        portfolio_phase: CyclePhase,
    ) -> PortfolioMode:
        """
        Determine portfolio positioning mode.
        
        Rules:
        - OFFENSE: transition_risk < 30 AND phase <= MID
        - DEFENSE: transition_risk > 60 OR phase = PEAKING/DOWNTURN
        - BALANCED: otherwise
        """
        if transition_risk > 60 or portfolio_phase in [CyclePhase.PEAKING, CyclePhase.DOWNTURN]:
            return PortfolioMode.DEFENSE
        elif transition_risk < 30 and portfolio_phase in [CyclePhase.EARLY, CyclePhase.MID]:
            return PortfolioMode.OFFENSE
        else:
            return PortfolioMode.BALANCED
    
    def _score_to_phase(self, score: float) -> CyclePhase:
        """Convert numeric phase score to CyclePhase enum."""
        for low, high, phase in PHASE_THRESHOLDS:
            if low <= score < high:
                return phase
        return CyclePhase.MID  # Default
    
    def _clip(self, value: float, min_val: float, max_val: float) -> float:
        """Clip value to range [min_val, max_val]."""
        return max(min_val, min(max_val, value))
    
    def generate_bucket_actions(
        self,
        portfolio_analysis: PortfolioRiskAnalysis,
    ) -> List[BucketAction]:
        """
        Generate recommended bucket-level actions.
        
        Rules:
        - REDUCE if R_b > 70 OR bucket phase = PEAKING
        - Target: bring to policy limit
        - Urgency based on risk level
        """
        actions = []
        
        for bucket_type, bucket in portfolio_analysis.buckets.items():
            # Skip cash bucket
            if bucket_type == BucketType.CASH:
                continue
            
            # Determine if action needed
            needs_reduction = (
                bucket.transition_risk > 70 or
                bucket.phase == CyclePhase.PEAKING or
                bucket.overage > 0.05  # More than 5% over limit
            )
            
            if needs_reduction:
                urgency = "HIGH" if bucket.transition_risk > 80 else "MEDIUM"
                timeframe = "1-2 weeks" if urgency == "HIGH" else "2-4 weeks"
                
                reason_parts = []
                if bucket.transition_risk > 70:
                    reason_parts.append(f"High transition risk ({bucket.transition_risk:.0f})")
                if bucket.phase == CyclePhase.PEAKING:
                    reason_parts.append("Bucket phase is PEAKING")
                if bucket.overage > 0:
                    reason_parts.append(f"Over limit by {bucket.overage*100:.1f}%")
                if bucket.critical_breadth > 0.5:
                    reason_parts.append(f"Critical signal breadth: {bucket.critical_breadth*100:.0f}%")
                
                reason = "; ".join(reason_parts)
                
                actions.append(BucketAction(
                    bucket=bucket_type,
                    action_type="REDUCE",
                    current_weight=bucket.weight,
                    target_weight=bucket.target_max,
                    urgency=urgency,
                    reason=reason,
                    timeframe=timeframe,
                ))
            elif bucket.weight < bucket.target_max * 0.5 and bucket.transition_risk < 40:
                # Opportunity to add to under-weighted, low-risk buckets
                actions.append(BucketAction(
                    bucket=bucket_type,
                    action_type="ADD",
                    current_weight=bucket.weight,
                    target_weight=bucket.target_max * 0.75,
                    urgency="LOW",
                    reason=f"Under-weighted and low risk ({bucket.transition_risk:.0f})",
                    timeframe="4-8 weeks",
                ))
        
        # Sort by urgency (HIGH first)
        urgency_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        actions.sort(key=lambda a: urgency_order.get(a.urgency, 3))
        
        return actions
    
    def generate_position_actions(
        self,
        portfolio_analysis: PortfolioRiskAnalysis,
        positions: List[PositionInput],
        cycle_analyses: Dict[str, StockCycleAnalysis],
        bucket_actions: List[BucketAction],
    ) -> List[PositionAction]:
        """
        Generate position-level actions within flagged buckets.
        
        Rules:
        - Within buckets flagged for REDUCE:
          - Rank by (weight × cycle_pressure)
          - TRIM top contributors
          - HOLD/HEDGE mid-tier
        - Only ADD if portfolio mode is OFFENSE and stock opportunity is strong
        """
        actions = []
        
        # Get buckets that need reduction
        reduce_buckets = {a.bucket for a in bucket_actions if a.action_type == "REDUCE"}
        
        for bucket_type in reduce_buckets:
            bucket = portfolio_analysis.buckets.get(bucket_type)
            if not bucket:
                continue
            
            # Rank positions by contribution to risk
            for contributor in bucket.top_contributors:
                ticker = contributor['ticker']
                weight = contributor['weight']
                pressure = contributor['pressure']
                contribution = contributor['contribution']
                
                analysis = cycle_analyses.get(ticker)
                if not analysis:
                    continue
                
                # Determine action based on contribution and signals
                if contribution > 3.0 or len(contributor['critical_signals']) >= 2:
                    action_type = "TRIM"
                    priority = 1
                    target_weight = weight * 0.5  # Reduce by 50%
                    reason = f"Top risk contributor ({contribution:.1f}); Critical signals: {', '.join(contributor['critical_signals'][:2])}"
                elif contribution > 1.5:
                    action_type = "TRIM"
                    priority = 2
                    target_weight = weight * 0.7  # Reduce by 30%
                    reason = f"Significant risk contributor ({contribution:.1f})"
                else:
                    action_type = "HOLD"
                    priority = 3
                    target_weight = weight
                    reason = f"Monitor; bucket risk elevated but position contribution moderate"
                
                actions.append(PositionAction(
                    ticker=ticker,
                    action_type=action_type,
                    current_weight=weight,
                    target_weight=target_weight,
                    priority=priority,
                    reason=reason,
                    contribution_to_risk=contribution,
                    metadata={
                        'bucket': bucket_type.value,
                        'phase': contributor['phase'],
                        'critical_signals': contributor['critical_signals'],
                    }
                ))
        
        # Add opportunities (only in OFFENSE mode)
        if portfolio_analysis.mode == PortfolioMode.OFFENSE:
            for pos in positions:
                analysis = cycle_analyses.get(pos.ticker)
                if not analysis:
                    continue
                
                # Strong opportunity: high opportunity score, early/mid phase, low risk
                if (analysis.opportunity_total > 60 and
                    analysis.phase in [CyclePhase.EARLY, CyclePhase.MID] and
                    analysis.risk_total < 40):
                    
                    actions.append(PositionAction(
                        ticker=pos.ticker,
                        action_type="ADD",
                        current_weight=pos.weight,
                        target_weight=pos.weight * 1.5,  # Increase by 50%
                        priority=4,
                        reason=f"Strong opportunity ({analysis.opportunity_total:.0f}) in {analysis.phase.value} phase",
                        contribution_to_risk=pos.weight * analysis.cycle_pressure,
                        metadata={
                            'bucket': pos.bucket.value,
                            'phase': analysis.phase.value,
                        }
                    ))
        
        # Sort by priority
        actions.sort(key=lambda a: a.priority)
        
        return actions
