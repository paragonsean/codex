"""
Portfolio Cycle Risk Reporter

Generates human-readable reports showing:
  - "Portfolio is late/peaking because 38% of weight is in PEAKING signals"
  - "Memory bucket is the source of transition risk"
  - "Even if MU looks fine alone, the portfolio needs rotation"
"""

from __future__ import annotations

from typing import List

from domain.portfolio import (
    BucketAction,
    BucketAnalysis,
    BucketType,
    CyclePhase,
    PortfolioMode,
    PortfolioRiskAnalysis,
    PositionAction,
)


class PortfolioReporter:
    """Generate portfolio cycle risk reports."""
    
    def generate_portfolio_summary(self, analysis: PortfolioRiskAnalysis) -> str:
        """
        Generate executive summary of portfolio cycle risk.
        
        Example output:
        "Portfolio is LATE/PEAKING because 38% of weight is in PEAKING signals.
         Transition risk: 72 (HIGH). Mode: DEFENSE.
         Memory bucket is the primary source of risk."
        """
        lines = []
        
        # Portfolio phase and mode
        phase_desc = self._get_phase_description(analysis.portfolio_phase)
        lines.append(f"Portfolio Phase: {analysis.portfolio_phase.value} ({phase_desc})")
        lines.append(f"Portfolio Mode: {analysis.mode.value}")
        lines.append(f"Transition Risk: {analysis.transition_risk:.0f} ({self._risk_level(analysis.transition_risk)})")
        lines.append("")
        
        # Peaking concentration
        if analysis.peaking_weight > 0.15:  # More than 15%
            lines.append(f"⚠️  {analysis.peaking_weight*100:.0f}% of portfolio is in PEAKING/DOWNTURN phase")
            lines.append(f"   Tickers: {', '.join(analysis.peaking_tickers[:5])}")
            lines.append("")
        
        # Risk component breakdown
        lines.append("Risk Components:")
        lines.append(f"  • Pressure Risk: {analysis.pressure_risk:.0f}")
        lines.append(f"  • Phase Concentration: {analysis.phase_concentration_risk:.0f}")
        lines.append(f"  • Bucket Concentration: {analysis.bucket_concentration_risk:.0f}")
        lines.append(f"  • Story Concentration: {analysis.story_concentration_risk:.0f}")
        lines.append("")
        
        # Top story concentrations
        if analysis.story_weights:
            top_stories = sorted(analysis.story_weights.items(), key=lambda x: x[1], reverse=True)[:3]
            lines.append("Top Story Concentrations:")
            for story, weight in top_stories:
                lines.append(f"  • {story}: {weight*100:.0f}%")
            lines.append("")
        
        # Identify highest-risk buckets
        high_risk_buckets = [
            (b.bucket, b.transition_risk)
            for b in analysis.buckets.values()
            if b.transition_risk > 60
        ]
        high_risk_buckets.sort(key=lambda x: x[1], reverse=True)
        
        if high_risk_buckets:
            lines.append("High-Risk Buckets:")
            for bucket, risk in high_risk_buckets:
                lines.append(f"  • {bucket.value}: Risk {risk:.0f}")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_bucket_report(self, bucket: BucketAnalysis) -> str:
        """
        Generate detailed report for a single bucket.
        
        Example output:
        Memory Bucket
          • Weight: 28% (limit 18%) → over by 10%
          • Bucket Pressure: 22.4 (High)
          • Critical Breadth: 62% (High)
          • Bucket Risk: 84 (PEAKING)
          • Top contributors:
            - MU: 12% × pressure 35 → 4.2
            - WDC: 8% × pressure 28 → 2.2
        """
        lines = []
        
        lines.append(f"{bucket.bucket.value} Bucket")
        lines.append("=" * 50)
        
        # Weight and overage
        weight_pct = bucket.weight * 100
        limit_pct = bucket.target_max * 100
        if bucket.overage > 0:
            overage_pct = bucket.overage * 100
            lines.append(f"Weight: {weight_pct:.1f}% (limit {limit_pct:.0f}%) → ⚠️  over by {overage_pct:.1f}%")
        else:
            lines.append(f"Weight: {weight_pct:.1f}% (limit {limit_pct:.0f}%)")
        
        # Bucket metrics
        lines.append(f"Bucket Pressure: {bucket.weighted_pressure:.1f} ({self._pressure_level(bucket.weighted_pressure)})")
        lines.append(f"Bucket Phase: {bucket.phase.value}")
        lines.append(f"Critical Breadth: {bucket.critical_breadth*100:.0f}% ({self._breadth_level(bucket.critical_breadth)})")
        lines.append(f"Bucket Risk: {bucket.transition_risk:.0f} ({self._risk_level(bucket.transition_risk)})")
        lines.append("")
        
        # Top contributors
        if bucket.top_contributors:
            lines.append("Top Contributors:")
            for contrib in bucket.top_contributors[:5]:
                ticker = contrib['ticker']
                weight = contrib['weight'] * 100
                pressure = contrib['pressure']
                contribution = contrib['contribution']
                phase = contrib['phase']
                
                critical_str = ""
                if contrib['critical_signals']:
                    critical_str = f" 🔴 [{', '.join(contrib['critical_signals'][:2])}]"
                
                lines.append(f"  • {ticker}: {weight:.1f}% × pressure {pressure:.1f} → {contribution:.1f} ({phase}){critical_str}")
        
        lines.append("")
        return "\n".join(lines)
    
    def generate_action_report(
        self,
        bucket_actions: List[BucketAction],
        position_actions: List[PositionAction],
    ) -> str:
        """
        Generate action recommendations report.
        
        Example output:
        Bucket Actions:
          1. [HIGH] REDUCE Memory from 28% → 18% over 2-4 weeks
             Reason: High transition risk (84); Bucket phase is PEAKING
          
        Position Actions:
          1. [Priority 1] TRIM MU from 12% → 6%
             Reason: Top risk contributor (4.2); Critical signals: RELATIVE_STRENGTH_VS_SOX, GOOD_NEWS_EFFECTIVENESS
        """
        lines = []
        
        # Bucket actions
        if bucket_actions:
            lines.append("BUCKET ACTIONS")
            lines.append("=" * 50)
            for i, action in enumerate(bucket_actions, 1):
                urgency_emoji = "🔴" if action.urgency == "HIGH" else "🟡" if action.urgency == "MEDIUM" else "🟢"
                
                if action.action_type == "REDUCE":
                    lines.append(f"{i}. {urgency_emoji} [{action.urgency}] {action.action_type} {action.bucket.value}")
                    lines.append(f"   From {action.current_weight*100:.1f}% → {action.target_weight*100:.1f}% over {action.timeframe}")
                elif action.action_type == "ADD":
                    lines.append(f"{i}. {urgency_emoji} [{action.urgency}] {action.action_type} to {action.bucket.value}")
                    lines.append(f"   From {action.current_weight*100:.1f}% → {action.target_weight*100:.1f}% over {action.timeframe}")
                
                lines.append(f"   Reason: {action.reason}")
                lines.append("")
        
        # Position actions
        if position_actions:
            lines.append("POSITION ACTIONS")
            lines.append("=" * 50)
            
            # Group by action type
            trims = [a for a in position_actions if a.action_type == "TRIM"]
            holds = [a for a in position_actions if a.action_type == "HOLD"]
            adds = [a for a in position_actions if a.action_type == "ADD"]
            
            if trims:
                lines.append("TRIM Positions:")
                for action in trims[:10]:  # Top 10
                    lines.append(f"  • [{action.priority}] {action.ticker}: {action.current_weight*100:.1f}% → {action.target_weight*100:.1f}%")
                    lines.append(f"    {action.reason}")
                    if action.metadata and 'critical_signals' in action.metadata:
                        signals = action.metadata['critical_signals']
                        if signals:
                            lines.append(f"    Critical: {', '.join(signals[:2])}")
                lines.append("")
            
            if adds:
                lines.append("ADD Opportunities:")
                for action in adds[:5]:  # Top 5
                    lines.append(f"  • [{action.priority}] {action.ticker}: {action.current_weight*100:.1f}% → {action.target_weight*100:.1f}%")
                    lines.append(f"    {action.reason}")
                lines.append("")
            
            if holds:
                lines.append(f"HOLD/Monitor: {len(holds)} positions")
                lines.append("")
        
        return "\n".join(lines)
    
    def generate_full_report(
        self,
        analysis: PortfolioRiskAnalysis,
        bucket_actions: List[BucketAction],
        position_actions: List[PositionAction],
    ) -> str:
        """Generate complete portfolio cycle risk report."""
        lines = []
        
        lines.append("=" * 70)
        lines.append("PORTFOLIO CYCLE RISK ANALYSIS")
        lines.append("=" * 70)
        lines.append("")
        
        # Executive summary
        lines.append(self.generate_portfolio_summary(analysis))
        lines.append("")
        
        # Bucket details
        lines.append("BUCKET ANALYSIS")
        lines.append("=" * 70)
        lines.append("")
        
        # Sort buckets by risk (descending)
        sorted_buckets = sorted(
            analysis.buckets.values(),
            key=lambda b: b.transition_risk,
            reverse=True
        )
        
        for bucket in sorted_buckets:
            if bucket.bucket == BucketType.CASH:
                continue  # Skip cash in detailed report
            lines.append(self.generate_bucket_report(bucket))
        
        # Actions
        lines.append("")
        lines.append(self.generate_action_report(bucket_actions, position_actions))
        
        return "\n".join(lines)
    
    def _get_phase_description(self, phase: CyclePhase) -> str:
        """Get human-readable phase description."""
        descriptions = {
            CyclePhase.EARLY: "Early cycle, strong momentum building",
            CyclePhase.MID: "Mid-cycle, healthy advance",
            CyclePhase.LATE: "Late cycle, momentum slowing",
            CyclePhase.PEAKING: "Peaking, high risk of reversal",
            CyclePhase.DOWNTURN: "Downturn, defensive positioning needed",
        }
        return descriptions.get(phase, "Unknown")
    
    def _risk_level(self, risk: float) -> str:
        """Convert risk score to level."""
        if risk >= 75:
            return "CRITICAL"
        elif risk >= 60:
            return "HIGH"
        elif risk >= 40:
            return "MODERATE"
        else:
            return "LOW"
    
    def _pressure_level(self, pressure: float) -> str:
        """Convert pressure to level."""
        if pressure >= 20:
            return "Very High"
        elif pressure >= 10:
            return "High"
        elif pressure >= 0:
            return "Moderate"
        else:
            return "Low"
    
    def _breadth_level(self, breadth: float) -> str:
        """Convert critical breadth to level."""
        if breadth >= 0.6:
            return "High"
        elif breadth >= 0.3:
            return "Moderate"
        else:
            return "Low"
