#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from datetime import datetime

from app.config import Config
from app.orchestrator import Orchestrator


def main():
    parser = argparse.ArgumentParser(
        description="Semiconductor Stock Analysis System"
    )
    parser.add_argument(
        "tickers",
        nargs="+",
        help="Stock tickers to analyze (e.g., MU WDC AMAT)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=180,
        help="Lookback period in days (default: 180)",
    )
    parser.add_argument(
        "--max-headlines",
        type=int,
        default=25,
        help="Maximum news headlines to fetch (default: 25)",
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        default="SOXX",
        help="Benchmark ticker for excess returns (default: SOXX)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="reports",
        help="Output directory for reports (default: reports)",
    )
    parser.add_argument(
        "--no-alerts",
        action="store_true",
        help="Disable alerts generation",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Historical analysis date (format: MM/DD/YYYY). If specified, only data up to this date will be used.",
    )
    
    args = parser.parse_args()
    
    # Parse historical date if provided
    as_of_date = None
    if args.date:
        try:
            as_of_date = datetime.strptime(args.date, "%m/%d/%Y")
            print(f"Historical analysis mode: Using data as of {as_of_date.strftime('%Y-%m-%d')}")
        except ValueError:
            print(f"Error: Invalid date format '{args.date}'. Expected MM/DD/YYYY (e.g., 12/20/2024)")
            return 1
    
    config = Config(
        lookback_days=args.days,
        max_headlines=args.max_headlines,
        benchmark_ticker=args.benchmark,
        output_dir=args.output_dir,
        enable_alerts=not args.no_alerts,
        as_of_date=as_of_date,
    )
    
    orchestrator = Orchestrator(config)
    
    print(f"Analyzing {len(args.tickers)} ticker(s): {', '.join(args.tickers)}")
    print(f"Lookback: {args.days} days | Benchmark: {args.benchmark}")
    print("-" * 60)
    
    run_result = orchestrator.run_analysis(args.tickers)
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    
    for result in run_result.results:
        ticker = result["ticker"]
        rec = result["recommendation"]
        signal = result["signal"]
        
        print(f"\n{ticker}:")
        print(f"  Action: {rec.action.value.upper()} (confidence: {rec.confidence:.1%})")
        print(f"  Opportunity: {signal.opportunity:.1f} | Sell Risk: {signal.sell_risk:.1f}")
        print(f"  Reasons: {', '.join(rec.reasons[:2])}")
    
    if run_result.errors:
        print("\nErrors:")
        for ticker, error in run_result.errors.items():
            print(f"  {ticker}: {error}")
    
    print("\nGenerating reports...")
    orchestrator.generate_reports(run_result)
    
    print("\nDone!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
