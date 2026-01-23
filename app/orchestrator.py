from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.config import Config
from data.market_data_service import MarketDataService
from data.news_service import NewsService
from decision.risk_manager import RiskManager
from decision.semiconductor_policy import SemiconductorPolicy
from domain.models import RunRequest, RunResult
from domain.portfolio import PortfolioContext
from features.feature_pipeline import FeaturePipeline
from output.alerts import AlertsManager
from output.html_reporter import HTMLReporter
from output.markdown_reporter import MarkdownReporter
from output.report_builder import ReportBuilder
from scoring.rules_scorer import RulesScorer


class Orchestrator:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        
        self.market_data_service = MarketDataService()
        self.news_service = NewsService()
        
        self.feature_pipeline = FeaturePipeline()
        
        self.scorer = RulesScorer()
        
        self.policy = SemiconductorPolicy(
            opportunity_buy_threshold=self.config.opportunity_buy_threshold,
            sell_risk_trim_threshold=self.config.sell_risk_trim_threshold,
            sell_risk_sell_threshold=self.config.sell_risk_sell_threshold,
        )
        
        self.risk_manager = RiskManager(
            max_position_pct=self.config.max_position_pct,
            max_sector_pct=self.config.max_sector_pct,
            min_cash_buffer=self.config.min_cash_buffer,
        )
        
        self.report_builder = ReportBuilder()
        self.html_reporter = HTMLReporter()
        self.markdown_reporter = MarkdownReporter()
        
        if self.config.enable_alerts:
            self.alerts_manager = AlertsManager()
        else:
            self.alerts_manager = None

    def run_analysis(
        self,
        tickers: List[str],
        portfolio_ctx: Optional[PortfolioContext] = None,
    ) -> RunResult:
        request = RunRequest(
            tickers=tickers,
            days=self.config.lookback_days,
            max_headlines=self.config.max_headlines,
            benchmark_ticker=self.config.benchmark_ticker,
        )
        
        results = []
        errors = {}
        
        benchmark_series = None
        if self.config.benchmark_ticker:
            try:
                benchmark_series = self.market_data_service.fetch_price_series(
                    self.config.benchmark_ticker,
                    self.config.lookback_days,
                    as_of_date=self.config.as_of_date,
                )
            except Exception as e:
                print(f"Warning: Could not fetch benchmark {self.config.benchmark_ticker}: {e}")
        
        for ticker in tickers:
            try:
                result = self._analyze_single_ticker(ticker, benchmark_series, portfolio_ctx)
                results.append(result)
            except Exception as e:
                errors[ticker] = str(e)
                print(f"Error analyzing {ticker}: {e}")
        
        return RunResult(
            request=request,
            created_at=datetime.now(),
            results=results,
            errors=errors if errors else None,
        )

    def _analyze_single_ticker(
        self,
        ticker: str,
        benchmark_series,
        portfolio_ctx: Optional[PortfolioContext],
    ) -> dict:
        print(f"\nAnalyzing {ticker}...")
        
        price_series = self.market_data_service.fetch_price_series(
            ticker,
            self.config.lookback_days,
            as_of_date=self.config.as_of_date,
        )
        
        news_events = self.news_service.fetch_news_events(
            ticker,
            max_items=self.config.max_headlines,
            as_of_date=self.config.as_of_date,
        )
        
        # Enrich news events with sentiment scores for reporting
        from features.news_features import NewsFeatures
        enriched_news_events = NewsFeatures.enrich_events(news_events)
        
        features = self.feature_pipeline.build_feature_vector(
            ticker=ticker,
            price_series=price_series,
            news_events=news_events,
            benchmark_series=benchmark_series,
        )
        
        signal = self.scorer.score(features)
        
        recommendation = self.policy.recommend(signal, features, portfolio_ctx)
        
        is_valid, violations = self.risk_manager.validate_recommendation(
            recommendation, portfolio_ctx
        )
        if not is_valid:
            recommendation.reasons.extend([f"Risk violation: {v}" for v in violations])
        
        if self.alerts_manager:
            alerts = self.alerts_manager.check_alerts(ticker, signal, recommendation)
            if alerts:
                print(f"  Generated {len(alerts)} alert(s)")
        
        report_data = self.report_builder.build_analysis_report(
            ticker, features, signal, recommendation, price_series.df, enriched_news_events
        )
        
        return {
            "ticker": ticker,
            "features": features,
            "signal": signal,
            "recommendation": recommendation,
            "report_data": report_data,
            "is_valid": is_valid,
            "violations": violations,
        }

    def generate_reports(self, run_result: RunResult) -> None:
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for result in run_result.results:
            ticker = result["ticker"]
            report_data = result["report_data"]
            
            html_content = self.html_reporter.render_analysis_report(report_data)
            html_path = output_dir / f"{ticker}_report_{timestamp}.html"
            with open(html_path, "w") as f:
                f.write(html_content)
            print(f"Generated HTML report: {html_path}")
            
            md_content = self.markdown_reporter.render_analysis_report(report_data)
            md_path = output_dir / f"{ticker}_report_{timestamp}.md"
            with open(md_path, "w") as f:
                f.write(md_content)
            print(f"Generated Markdown report: {md_path}")
