"""
Example: Portfolio Cycle Risk Analysis

Demonstrates how to use the portfolio cycle risk analyzer to:
  - Analyze bucket-level risk
  - Calculate portfolio transition risk
  - Generate rotation recommendations
"""

from domain.portfolio import (
    BucketType,
    CyclePhase,
    PositionInput,
    ProfileType,
    StockCycleAnalysis,
)
from portfolio.portfolio_cycle_analyzer import PortfolioCycleAnalyzer
from portfolio.portfolio_reporter import PortfolioReporter


def example_portfolio_analysis():
    """
    Example portfolio showing:
      - Memory bucket overweight and peaking
      - Portfolio in DEFENSE mode
      - Need for rotation
    """
    
    # Define portfolio positions
    positions = [
        # Memory bucket - OVERWEIGHT (28% vs 18% limit)
        PositionInput(
            ticker="MU",
            market_value=120_000,
            weight=0.12,
            bucket=BucketType.MEMORY,
            profile=ProfileType.MEMORY,
            story_tags=["AI_Compute", "Memory_Pricing"],
        ),
        PositionInput(
            ticker="WDC",
            market_value=80_000,
            weight=0.08,
            bucket=BucketType.MEMORY,
            profile=ProfileType.MEMORY,
            story_tags=["Memory_Pricing", "Data_Center"],
        ),
        PositionInput(
            ticker="STX",
            market_value=80_000,
            weight=0.08,
            bucket=BucketType.MEMORY,
            profile=ProfileType.MEMORY,
            story_tags=["Memory_Pricing"],
        ),
        
        # Equipment bucket - healthy
        PositionInput(
            ticker="AMAT",
            market_value=100_000,
            weight=0.10,
            bucket=BucketType.EQUIPMENT,
            profile=ProfileType.EQUIPMENT,
            story_tags=["AI_Capex", "China_Export"],
        ),
        PositionInput(
            ticker="LRCX",
            market_value=80_000,
            weight=0.08,
            bucket=BucketType.EQUIPMENT,
            profile=ProfileType.EQUIPMENT,
            story_tags=["AI_Capex"],
        ),
        
        # EDA bucket - early cycle
        PositionInput(
            ticker="CDNS",
            market_value=70_000,
            weight=0.07,
            bucket=BucketType.EDA,
            profile=ProfileType.EDA,
            story_tags=["AI_Design"],
        ),
        PositionInput(
            ticker="SNPS",
            market_value=60_000,
            weight=0.06,
            bucket=BucketType.EDA,
            profile=ProfileType.EDA,
            story_tags=["AI_Design"],
        ),
        
        # Analog bucket
        PositionInput(
            ticker="ADI",
            market_value=90_000,
            weight=0.09,
            bucket=BucketType.ANALOG,
            profile=ProfileType.ANALOG,
            story_tags=["Industrial", "Auto"],
        ),
        
        # Foundry
        PositionInput(
            ticker="TSM",
            market_value=120_000,
            weight=0.12,
            bucket=BucketType.FOUNDRY,
            profile=ProfileType.FOUNDRY,
            story_tags=["AI_Compute", "AI_Capex"],
        ),
        
        # Power
        PositionInput(
            ticker="MPWR",
            market_value=50_000,
            weight=0.05,
            bucket=BucketType.POWER,
            profile=ProfileType.POWER,
            story_tags=["AI_Compute", "Crypto"],
        ),
        
        # Cash
        PositionInput(
            ticker="CASH",
            market_value=150_000,
            weight=0.15,
            bucket=BucketType.CASH,
            profile=ProfileType.MEMORY,  # Doesn't matter for cash
            story_tags=[],
        ),
    ]
    
    # Define cycle analyses for each stock
    cycle_analyses = {
        # Memory - PEAKING with high risk
        "MU": StockCycleAnalysis(
            ticker="MU",
            risk_total=75.0,
            opportunity_total=22.0,
            cycle_pressure=53.0,  # 75 - 22
            phase=CyclePhase.PEAKING,
            transition_risk=84.0,
            data_quality_ok=True,
            critical_signals_fired=["RELATIVE_STRENGTH_VS_SOX", "GOOD_NEWS_EFFECTIVENESS"],
        ),
        "WDC": StockCycleAnalysis(
            ticker="WDC",
            risk_total=68.0,
            opportunity_total=25.0,
            cycle_pressure=43.0,
            phase=CyclePhase.LATE,
            transition_risk=72.0,
            data_quality_ok=True,
            critical_signals_fired=["FIRST_50DMA_FAILURE"],
        ),
        "STX": StockCycleAnalysis(
            ticker="STX",
            risk_total=70.0,
            opportunity_total=20.0,
            cycle_pressure=50.0,
            phase=CyclePhase.PEAKING,
            transition_risk=78.0,
            data_quality_ok=True,
            critical_signals_fired=["RELATIVE_STRENGTH_VS_SOX"],
        ),
        
        # Equipment - MID cycle, healthy
        "AMAT": StockCycleAnalysis(
            ticker="AMAT",
            risk_total=35.0,
            opportunity_total=55.0,
            cycle_pressure=-20.0,
            phase=CyclePhase.MID,
            transition_risk=28.0,
            data_quality_ok=True,
            critical_signals_fired=[],
        ),
        "LRCX": StockCycleAnalysis(
            ticker="LRCX",
            risk_total=40.0,
            opportunity_total=50.0,
            cycle_pressure=-10.0,
            phase=CyclePhase.MID,
            transition_risk=32.0,
            data_quality_ok=True,
            critical_signals_fired=[],
        ),
        
        # EDA - EARLY cycle, strong opportunity
        "CDNS": StockCycleAnalysis(
            ticker="CDNS",
            risk_total=25.0,
            opportunity_total=65.0,
            cycle_pressure=-40.0,
            phase=CyclePhase.EARLY,
            transition_risk=18.0,
            data_quality_ok=True,
            critical_signals_fired=[],
        ),
        "SNPS": StockCycleAnalysis(
            ticker="SNPS",
            risk_total=28.0,
            opportunity_total=62.0,
            cycle_pressure=-34.0,
            phase=CyclePhase.EARLY,
            transition_risk=20.0,
            data_quality_ok=True,
            critical_signals_fired=[],
        ),
        
        # Analog - MID cycle
        "ADI": StockCycleAnalysis(
            ticker="ADI",
            risk_total=38.0,
            opportunity_total=48.0,
            cycle_pressure=-10.0,
            phase=CyclePhase.MID,
            transition_risk=30.0,
            data_quality_ok=True,
            critical_signals_fired=[],
        ),
        
        # Foundry - LATE cycle
        "TSM": StockCycleAnalysis(
            ticker="TSM",
            risk_total=52.0,
            opportunity_total=38.0,
            cycle_pressure=14.0,
            phase=CyclePhase.LATE,
            transition_risk=48.0,
            data_quality_ok=True,
            critical_signals_fired=[],
        ),
        
        # Power - MID cycle
        "MPWR": StockCycleAnalysis(
            ticker="MPWR",
            risk_total=42.0,
            opportunity_total=45.0,
            cycle_pressure=-3.0,
            phase=CyclePhase.MID,
            transition_risk=35.0,
            data_quality_ok=True,
            critical_signals_fired=[],
        ),
    }
    
    # Analyze portfolio
    analyzer = PortfolioCycleAnalyzer()
    portfolio_analysis = analyzer.analyze_portfolio(
        positions=positions,
        cycle_analyses=cycle_analyses,
        total_value=1_000_000,
    )
    
    # Generate actions
    bucket_actions = analyzer.generate_bucket_actions(portfolio_analysis)
    position_actions = analyzer.generate_position_actions(
        portfolio_analysis=portfolio_analysis,
        positions=positions,
        cycle_analyses=cycle_analyses,
        bucket_actions=bucket_actions,
    )
    
    # Generate report
    reporter = PortfolioReporter()
    report = reporter.generate_full_report(
        analysis=portfolio_analysis,
        bucket_actions=bucket_actions,
        position_actions=position_actions,
    )
    
    print(report)
    
    # Print key insights
    print("\n" + "=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)
    print(f"\n1. Portfolio is in {portfolio_analysis.mode.value} mode")
    print(f"   Transition risk: {portfolio_analysis.transition_risk:.0f}")
    print(f"   Portfolio phase: {portfolio_analysis.portfolio_phase.value}")
    
    print(f"\n2. {portfolio_analysis.peaking_weight*100:.0f}% of portfolio is PEAKING/DOWNTURN")
    print(f"   Tickers: {', '.join(portfolio_analysis.peaking_tickers)}")
    
    memory_bucket = portfolio_analysis.buckets[BucketType.MEMORY]
    print(f"\n3. Memory bucket is {memory_bucket.weight*100:.0f}% (limit {memory_bucket.target_max*100:.0f}%)")
    print(f"   Bucket risk: {memory_bucket.transition_risk:.0f}")
    print(f"   Critical breadth: {memory_bucket.critical_breadth*100:.0f}%")
    
    print(f"\n4. Top story concentration: {max(portfolio_analysis.story_weights.items(), key=lambda x: x[1])}")
    
    print(f"\n5. Recommended actions:")
    print(f"   - {len([a for a in bucket_actions if a.action_type == 'REDUCE'])} buckets to reduce")
    print(f"   - {len([a for a in position_actions if a.action_type == 'TRIM'])} positions to trim")
    print(f"   - {len([a for a in position_actions if a.action_type == 'ADD'])} opportunities to add")


if __name__ == "__main__":
    example_portfolio_analysis()
