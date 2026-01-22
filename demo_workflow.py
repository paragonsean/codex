#!/usr/bin/env python3
"""
demo_workflow.py

Demonstration of the complete stock analysis and reporting workflow.
Shows how to use the enhanced news analyzer and report generator together.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and display results."""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}")
    print("-" * 40)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("🚀 Stock Analysis & Reporting Workflow Demo")
    print("=" * 60)
    
    # Step 1: Basic news analysis
    success = run_command(
        "python news.py --tickers MU WDC AMD --days 180 --max-headlines 5",
        "Step 1: Enhanced News Analysis"
    )
    
    if not success:
        print("❌ News analysis failed. Exiting.")
        return
    
    # Step 2: Generate comprehensive reports
    success = run_command(
        "python stock_report_generator.py --tickers MU WDC AMD --days 180 --max-headlines 15 --format both",
        "Step 2: Generate HTML & Markdown Reports"
    )
    
    if not success:
        print("❌ Report generation failed. Exiting.")
        return
    
    # Step 3: List available reports
    success = run_command(
        "python report_viewer.py --list",
        "Step 3: List Generated Reports"
    )
    
    # Step 4: Show usage instructions
    print(f"\n{'='*60}")
    print("📋 Workflow Complete! Next Steps:")
    print(f"{'='*60}")
    print("1. View the HTML report:")
    print("   python report_viewer.py --open stock_report_20260122_191649.html")
    print("\n2. Convert to PDF (requires weasyprint):")
    print("   pip install weasyprint")
    print("   python report_viewer.py --convert-pdf stock_report_20260122_191649.html")
    print("\n3. Analyze different stocks:")
    print("   python stock_report_generator.py --tickers AAPL TSLA NVDA --days 90")
    print("\n4. Custom keywords and queries:")
    print("   python news.py --tickers MU --keywords 'HBM,AI,chipsets' --extra-query 'Micron earnings'")
    
    print(f"\n🎉 Demo completed successfully!")
    print("📁 Reports are saved in the 'reports/' directory")


if __name__ == "__main__":
    main()
