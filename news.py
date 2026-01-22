#!/usr/bin/env python3
"""
market_news_analyzer.py

Analyze tickers using:
- Prices (yfinance)
- News headlines (RSS: Google News by default; optional additional feeds)
- Simple sentiment & keyword signal scoring
- Technical summary: returns, trend, vol, drawdown, volume spikes

No API keys required.

Examples:
  python market_news_analyzer.py --tickers MU WDC AMD INTC --days 180
  python market_news_analyzer.py --tickers MU --days 365 --keywords "HBM,DRAM,NAND,capex,AI" --out report.csv
  python market_news_analyzer.py --tickers MU WDC --json-out report.json --max-headlines 40
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Set

import numpy as np
import pandas as pd
import requests
import feedparser
import yfinance as yf
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# ----------------------------
# Enhanced sentiment + categorization
# ----------------------------
# Sentiment word categories
POS_WORDS = {
    "beats", "beat", "surge", "soar", "record", "strong", "upgrade", "upgraded",
    "growth", "rally", "bullish", "profit", "profits", "margin", "margins",
    "accelerate", "accelerates", "expands", "expansion", "demand", "wins", "win",
    "partnership", "contract", "orders", "guidance raised", "raised guidance"
}
NEG_WORDS = {
    "miss", "misses", "plunge", "drop", "falls", "weak", "downgrade", "downgraded",
    "cut", "cuts", "lawsuit", "probe", "investigation", "warning", "bearish",
    "loss", "losses", "margin pressure", "inventory", "oversupply",
    "layoffs", "delay", "delays", "slowdown", "slows", "guidance cut"
}

# News categories with keywords
NEWS_CATEGORIES = {
    "earnings": {
        "earnings", "quarterly", "q1", "q2", "q3", "q4", "eps", "revenue", "profit", "loss", 
        "beat", "miss", "guidance", "forecast", "estimate", "analyst", "upgrade", "downgrade"
    },
    "mergers": {
        "acquisition", "merger", "buyout", "takeover", "deal", "acquire", "purchase", 
        "sell", "spinoff", "divest", "joint venture", "partnership"
    },
    "products": {
        "product", "launch", "release", "new", "chip", "processor", "gpu", "cpu", 
        "memory", "storage", "hbm", "dram", "nand", "ssd", "datacenter", "ai", "ml"
    },
    "financial": {
        "financing", "debt", "credit", "loan", "cash", "investment", "funding", 
        "capital", "share", "stock", "dividend", "buyback", "offering"
    },
    "operations": {
        "plant", "factory", "production", "manufacturing", "supply", "chain", 
        "inventory", "operations", "facility", "expansion", "construction"
    },
    "legal": {
        "lawsuit", "legal", "court", "judge", "ruling", "patent", "infringement", 
        "settlement", "fine", "penalty", "regulation", "compliance"
    },
    "market": {
        "market", "sector", "industry", "competition", "competitor", "share", 
        "pricing", "demand", "supply", "trend", "outlook"
    }
}

# Event impact indicators
HIGH_IMPACT_WORDS = {
    "breakthrough", "revolutionary", "landmark", "historic", "unprecedented",
    "major", "significant", "substantial", "massive", "huge", "blockbuster"
}

MEDIUM_IMPACT_WORDS = {
    "notable", "important", "key", "strategic", "meaningful", "considerable"
}

def normalize_text(s: str) -> str:
    s = s.lower()
    s = re.sub(r"\s+", " ", s).strip()
    return s

def sentiment_score(text: str) -> int:
    """
    Very lightweight lexicon score:
    +1 for each positive keyword/word occurrence, -1 for negative.
    """
    t = normalize_text(text)
    score = 0
    for w in POS_WORDS:
        if w in t:
            score += 1
    for w in NEG_WORDS:
        if w in t:
            score -= 1
    return score

def keyword_hits(text: str, keywords: List[str]) -> Dict[str, int]:
    t = normalize_text(text)
    hits = {}
    for k in keywords:
        kk = normalize_text(k)
        hits[k] = 1 if kk and kk in t else 0
    return hits

def categorize_news(text: str) -> Dict[str, int]:
    """
    Categorize news headline into one or more categories.
    Returns dict with category names and hit counts.
    """
    t = normalize_text(text)
    categories = {}
    
    for cat_name, keywords in NEWS_CATEGORIES.items():
        hits = sum(1 for k in keywords if k in t)
        if hits > 0:
            categories[cat_name] = hits
    
    return categories

def impact_score(text: str) -> int:
    """
    Assess the potential impact/magnitude of the news.
    Returns: 2 for high impact, 1 for medium, 0 for normal/low
    """
    t = normalize_text(text)
    
    for word in HIGH_IMPACT_WORDS:
        if word in t:
            return 2
    
    for word in MEDIUM_IMPACT_WORDS:
        if word in t:
            return 1
    
    return 0

def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract potential entities like company names, people, locations.
    This is a simple implementation - in production you'd use NLP libraries.
    """
    # Simple capitalization-based entity extraction
    words = text.split()
    entities = {
        "companies": [],
        "people": [],
        "locations": []
    }
    
    # Look for potential company names (all caps or title case with common suffixes)
    company_suffixes = {"corp", "inc", "ltd", "llc", "co", "company", "technologies", "semiconductor"}
    for i, word in enumerate(words):
        if word.isupper() and len(word) > 1:
            entities["companies"].append(word)
        elif word.title() and any(suffix in word.lower() for suffix in company_suffixes):
            entities["companies"].append(word)
    
    return entities

def news_quality_score(headline: str, source: Optional[str] = None) -> float:
    """
    Assess news quality based on source credibility and headline characteristics.
    Returns score between 0.0 and 1.0
    """
    score = 0.5  # baseline
    
    # Source credibility (simple heuristic)
    if source:
        high_quality_sources = {
            "reuters", "bloomberg", "wall street journal", "financial times",
            "associated press", "cnbc", "marketwatch", "yahoo finance"
        }
        medium_quality_sources = {
            "seeking alpha", "investor's business daily", "the motley fool",
            "benzinga", "business wire"
        }
        
        source_lower = source.lower()
        if any(hqs in source_lower for hqs in high_quality_sources):
            score += 0.3
        elif any(mqs in source_lower for mqs in medium_quality_sources):
            score += 0.15
    
    # Headline quality indicators
    if len(headline.split()) >= 8:  # substantial headline
        score += 0.1
    
    if any(fin_word in headline.lower() for fin_word in ["earnings", "revenue", "profit", "guidance"]):
        score += 0.1
    
    # Penalize clickbait patterns
    clickbait_indicators = ["!", "??", "shocking", "you won't believe", "revealed"]
    if any(indicator in headline.lower() for indicator in clickbait_indicators):
        score -= 0.2
    
    return max(0.0, min(1.0, score))


# ----------------------------
# RSS News fetching
# ----------------------------
def google_news_rss_url(ticker_or_query: str) -> str:
    """
    Google News RSS search endpoint. This typically works without keys.
    Note: This is a best-effort public RSS and can change over time.
    """
    q = requests.utils.quote(ticker_or_query)
    # "when:7d" biases recent headlines; change if desired
    return f"https://news.google.com/rss/search?q={q}%20when:7d&hl=en-US&gl=US&ceid=US:en"

@dataclass
class Headline:
    ticker: str
    title: str
    link: str
    published: str  # raw string
    published_ts: Optional[str]  # ISO timestamp best-effort
    source: Optional[str]
    sentiment: int
    keyword_score: int
    categories: Dict[str, int]  # news categories with hit counts
    impact: int  # 0=low, 1=medium, 2=high
    quality: float  # 0.0-1.0 quality score
    entities: Dict[str, List[str]]  # extracted entities

def parse_published(entry) -> Tuple[str, Optional[str]]:
    raw = getattr(entry, "published", "") or getattr(entry, "updated", "") or ""
    # feedparser sometimes provides parsed struct_time
    if getattr(entry, "published_parsed", None):
        dt = datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
        return raw, dt.isoformat()
    if getattr(entry, "updated_parsed", None):
        dt = datetime.fromtimestamp(time.mktime(entry.updated_parsed), tz=timezone.utc)
        return raw, dt.isoformat()
    return raw, None

def fetch_headlines_for_ticker(
    ticker: str,
    max_items: int,
    keywords: List[str],
    extra_queries: Optional[List[str]] = None,
    timeout: int = 20,
) -> List[Headline]:
    """
    Fetch headlines from Google News RSS for:
    - the ticker
    - optional extra queries (e.g., "Micron HBM", "WDC NAND pricing")
    """
    queries = [ticker]
    if extra_queries:
        queries.extend(extra_queries)

    headlines: List[Headline] = []
    seen_titles = set()

    for q in queries:
        url = google_news_rss_url(q)
        feed = feedparser.parse(url)

        for entry in feed.entries[: max_items * 2]:
            title = getattr(entry, "title", "").strip()
            if not title or title in seen_titles:
                continue
            seen_titles.add(title)

            link = getattr(entry, "link", "")
            raw_pub, iso_pub = parse_published(entry)
            source = None
            if hasattr(entry, "source") and entry.source:
                source = getattr(entry.source, "title", None)

            sent = sentiment_score(title)
            hits = keyword_hits(title, keywords)
            kscore = sum(hits.values())
            cats = categorize_news(title)
            imp = impact_score(title)
            qual = news_quality_score(title, source)
            ents = extract_entities(title)

            headlines.append(
                Headline(
                    ticker=ticker,
                    title=title,
                    link=link,
                    published=raw_pub,
                    published_ts=iso_pub,
                    source=source,
                    sentiment=sent,
                    keyword_score=kscore,
                    categories=cats,
                    impact=imp,
                    quality=qual,
                    entities=ents,
                )
            )

    # Enhanced sorting: quality + impact + keyword relevance + sentiment magnitude + recency
    def sort_key(h: Headline):
        rec = h.published_ts or ""
        return (h.quality, h.impact, h.keyword_score, abs(h.sentiment), rec)

    headlines.sort(key=sort_key, reverse=True)
    return headlines[:max_items]


# ----------------------------
# Price analysis
# ----------------------------
@dataclass
class PriceSummary:
    ticker: str
    last_close: float
    ret_5d: float
    ret_21d: float
    ret_63d: float
    vol_21d_ann: float
    max_drawdown: float
    trend_50_200: str
    rsi_14: float
    volume_z_20: float

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    # Wilder's smoothing
    roll_up = up.ewm(alpha=1/period, adjust=False).mean()
    roll_down = down.ewm(alpha=1/period, adjust=False).mean()
    rs = roll_up / (roll_down.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)

def max_drawdown(close: pd.Series) -> float:
    peak = close.cummax()
    dd = (close / peak) - 1.0
    return float(dd.min())

def zscore_last(x: pd.Series, window: int) -> float:
    if len(x) < window + 1:
        return float("nan")
    w = x.iloc[-window:]
    mu = w.mean()
    sd = w.std(ddof=0)
    if sd == 0:
        return 0.0
    return float((x.iloc[-1] - mu) / sd)

def extract_series(df: pd.DataFrame, column: str, ticker: Optional[str] = None) -> pd.Series:
    """
    Return a float Series for a column that may be single-index or multi-index.
    yfinance can return MultiIndex columns (field, ticker), even for one ticker.
    """
    if column in df.columns:
        series_or_df = df[column]
    elif isinstance(df.columns, pd.MultiIndex) and column in df.columns.get_level_values(0):
        series_or_df = df[column]
    else:
        raise KeyError(f"Column '{column}' not found in DataFrame")

    if isinstance(series_or_df, pd.DataFrame):
        if ticker and ticker in series_or_df.columns:
            series = series_or_df[ticker]
        elif series_or_df.shape[1] == 1:
            series = series_or_df.iloc[:, 0]
        else:
            series = series_or_df.iloc[:, 0]
    else:
        series = series_or_df

    return series.astype(float)

def fetch_prices(ticker: str, days: int) -> pd.DataFrame:
    """
    Fetch daily prices from yfinance for the last `days` calendar days.
    """
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days + 10)  # buffer for trading days
    df = yf.download(
        tickers=ticker,
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False,
    )
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.dropna()
    return df

def summarize_prices(ticker: str, df: pd.DataFrame) -> Optional[PriceSummary]:
    if df is None or df.empty:
        return None

    close = extract_series(df, "Close", ticker)
    vol = extract_series(df, "Volume", ticker) if ("Volume" in df.columns or (isinstance(df.columns, pd.MultiIndex) and "Volume" in df.columns.get_level_values(0))) else pd.Series(index=df.index, dtype=float)

    last = float(close.iloc[-1])

    def ret_n(n: int) -> float:
        if len(close) <= n:
            return float("nan")
        return float((close.iloc[-1] / close.iloc[-1 - n]) - 1.0)

    # Ann vol from daily returns
    rets = close.pct_change().dropna()
    vol_21 = rets.tail(21).std(ddof=0) * math.sqrt(252) if len(rets) >= 21 else float("nan")

    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()

    trend = "unknown"
    if not np.isnan(ma50.iloc[-1]) and not np.isnan(ma200.iloc[-1]):
        trend = "bullish (50>200)" if ma50.iloc[-1] > ma200.iloc[-1] else "bearish (50<200)"

    rsi14 = float(rsi(close, 14).iloc[-1])
    v_z = zscore_last(vol, 20) if len(vol.dropna()) >= 21 else float("nan")

    return PriceSummary(
        ticker=ticker,
        last_close=last,
        ret_5d=ret_n(5),
        ret_21d=ret_n(21),
        ret_63d=ret_n(63),
        vol_21d_ann=float(vol_21) if not np.isnan(vol_21) else float("nan"),
        max_drawdown=max_drawdown(close),
        trend_50_200=trend,
        rsi_14=rsi14,
        volume_z_20=v_z,
    )


# ----------------------------
# Combined scoring
# ----------------------------
@dataclass
class TickerReport:
    ticker: str
    price: Optional[PriceSummary]
    headlines: List[Headline]
    news_sentiment_total: int
    news_keyword_total: int
    combined_signal: float
    notes: List[str]

def compute_combined_signal(price: Optional[PriceSummary], headlines: List[Headline]) -> Tuple[float, List[str]]:
    """
    Enhanced combined score with news categorization and quality weighting.
    - Price momentum: 21d and 63d returns
    - Trend bonus if 50>200
    - RSI penalty if too hot
    - News: sentiment + keyword relevance + quality + impact weighting
    - Category-specific bonuses
    """
    notes = []
    score = 0.0

    # Enhanced news analysis
    news_sent = sum(h.sentiment for h in headlines)
    news_key = sum(h.keyword_score for h in headlines)
    high_impact_count = sum(1 for h in headlines if h.impact == 2)
    avg_quality = sum(h.quality for h in headlines) / len(headlines) if headlines else 0
    
    # Category analysis
    category_counts = {}
    for h in headlines:
        for cat in h.categories:
            category_counts[cat] = category_counts.get(cat, 0) + h.categories[cat]
    
    # News component with quality and impact weighting
    news_weight = 0.7 * avg_quality  # Quality-weighted news component
    score += news_weight * news_sent + 0.5 * news_key
    
    # Impact bonuses
    if high_impact_count >= 2:
        score += 2.0
        notes.append(f"Multiple high-impact news events ({high_impact_count}).")
    elif high_impact_count >= 1:
        score += 1.0
        notes.append("High-impact news detected.")
    
    # Category-specific bonuses
    if category_counts.get("earnings", 0) >= 3:
        score += 1.5
        notes.append("Strong earnings-related news coverage.")
    if category_counts.get("products", 0) >= 3:
        score += 1.0
        notes.append("Multiple product announcements.")
    if category_counts.get("mergers", 0) >= 1:
        score += 2.0
        notes.append("M&A activity detected.")
    if category_counts.get("legal", 0) >= 2:
        score -= 1.5
        notes.append("Multiple legal/regulatory issues.")
    
    # Quality bonus
    if avg_quality >= 0.8:
        score += 1.0
        notes.append("High-quality news sources.")
    
    # General news sentiment notes
    if news_key >= 5:
        notes.append("News has multiple keyword hits (high relevance).")
    if news_sent >= 3:
        notes.append("Headlines skew positive.")
    elif news_sent <= -3:
        notes.append("Headlines skew negative.")

    # Price component (unchanged but with better notes)
    if price:
        if not math.isnan(price.ret_21d):
            score += 40.0 * price.ret_21d
        if not math.isnan(price.ret_63d):
            score += 25.0 * price.ret_63d

        if "bullish" in price.trend_50_200:
            score += 1.5
            notes.append("Uptrend (50DMA above 200DMA).")
        elif "bearish" in price.trend_50_200:
            score -= 1.5
            notes.append("Downtrend (50DMA below 200DMA).")

        if price.rsi_14 >= 70:
            score -= 1.0
            notes.append("RSI suggests overbought (>=70).")
        elif price.rsi_14 <= 30:
            score += 1.0
            notes.append("RSI suggests oversold (<=30).")

        if not math.isnan(price.volume_z_20) and price.volume_z_20 >= 2.0:
            notes.append("Volume spike (z>=2).")

        if price.max_drawdown <= -0.25:
            notes.append("Large drawdown from peak (<= -25%).")

    return score, notes


# ----------------------------
# Output
# ----------------------------
def print_report(reports: List[TickerReport], max_headlines: int):
    for r in reports:
        print("=" * 80)
        print(f"{r.ticker} | combined_signal={r.combined_signal:.2f} | news_sent={r.news_sentiment_total} | news_kw={r.news_keyword_total}")
        if r.price:
            p = r.price
            print(
                f"Price: last={p.last_close:.2f} | 5d={p.ret_5d:+.2%} 21d={p.ret_21d:+.2%} 63d={p.ret_63d:+.2%} | "
                f"vol(21d ann)={p.vol_21d_ann:.1%} | mdd={p.max_drawdown:.1%} | {p.trend_50_200} | RSI14={p.rsi_14:.1f} | vol_z20={p.volume_z_20:.2f}"
            )
        else:
            print("Price: (no data)")

        # News analysis summary
        if r.headlines:
            avg_quality = sum(h.quality for h in r.headlines) / len(r.headlines)
            high_impact = sum(1 for h in r.headlines if h.impact == 2)
            categories = {}
            for h in r.headlines:
                for cat in h.categories:
                    categories[cat] = categories.get(cat, 0) + 1
            
            print(f"News Analysis: {len(r.headlines)} headlines | avg_quality={avg_quality:.2f} | high_impact={high_impact}")
            if categories:
                cats_str = ", ".join([f"{cat}({count})" for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]])
                print(f"Categories: {cats_str}")

        if r.notes:
            print("Notes:")
            for n in r.notes:
                print(f"  - {n}")

        print("\nTop headlines:")
        for h in r.headlines[:max_headlines]:
            src = f" [{h.source}]" if h.source else ""
            ts = f" ({h.published_ts})" if h.published_ts else ""
            qual = f" Q:{h.quality:.2f}" if h.quality else ""
            impact_str = {0: "Low", 1: "Med", 2: "High"}.get(h.impact, "?")
            cats_str = ",".join(h.categories.keys()) if h.categories else "none"
            
            print(f"  - ({h.sentiment:+d}, kw={h.keyword_score}, {impact_str}Impact{qual}){src}{ts} [{cats_str}] {h.title}")
            print(f"    {h.link}")
            
            # Show entities if any found
            if any(h.entities.values()):
                entities_parts = []
                for ent_type, entities in h.entities.items():
                    if entities:
                        entities_parts.append(f"{ent_type}:{','.join(entities[:3])}")
                if entities_parts:
                    print(f"    Entities: {' | '.join(entities_parts)}")

def write_csv(path: str, reports: List[TickerReport]):
    fields = [
        "ticker",
        "combined_signal",
        "news_sentiment_total",
        "news_keyword_total",
        "last_close",
        "ret_5d",
        "ret_21d",
        "ret_63d",
        "vol_21d_ann",
        "max_drawdown",
        "trend_50_200",
        "rsi_14",
        "volume_z_20",
        "top_headline",
        "top_headline_link",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in reports:
            p = r.price
            top = r.headlines[0] if r.headlines else None
            row = {
                "ticker": r.ticker,
                "combined_signal": round(r.combined_signal, 3),
                "news_sentiment_total": r.news_sentiment_total,
                "news_keyword_total": r.news_keyword_total,
                "last_close": getattr(p, "last_close", None),
                "ret_5d": getattr(p, "ret_5d", None),
                "ret_21d": getattr(p, "ret_21d", None),
                "ret_63d": getattr(p, "ret_63d", None),
                "vol_21d_ann": getattr(p, "vol_21d_ann", None),
                "max_drawdown": getattr(p, "max_drawdown", None),
                "trend_50_200": getattr(p, "trend_50_200", None),
                "rsi_14": getattr(p, "rsi_14", None),
                "volume_z_20": getattr(p, "volume_z_20", None),
                "top_headline": getattr(top, "title", None),
                "top_headline_link": getattr(top, "link", None),
            }
            w.writerow(row)

def write_json(path: str, reports: List[TickerReport]):
    payload = []
    for r in reports:
        payload.append({
            "ticker": r.ticker,
            "combined_signal": r.combined_signal,
            "news_sentiment_total": r.news_sentiment_total,
            "news_keyword_total": r.news_keyword_total,
            "price": asdict(r.price) if r.price else None,
            "notes": r.notes,
            "headlines": [asdict(h) for h in r.headlines],
        })
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", nargs="+", required=True, help="Tickers to analyze, e.g. MU WDC AMD")
    ap.add_argument("--days", type=int, default=365, help="Calendar days of price history to fetch")
    ap.add_argument("--max-headlines", type=int, default=25, help="Max headlines per ticker to keep")
    ap.add_argument("--keywords", type=str, default="AI,HBM,DRAM,NAND,capex,guidance,inventory,datacenter,chip,foundry",
                    help="Comma-separated keywords to score in headlines")
    ap.add_argument("--extra-query", action="append", default=[],
                    help="Add extra news queries per ticker (can be repeated). Example: --extra-query 'Micron HBM'")
    ap.add_argument("--out", type=str, default=None, help="Write summary CSV")
    ap.add_argument("--json-out", type=str, default=None, help="Write full JSON report")
    args = ap.parse_args()

    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]

    reports: List[TickerReport] = []
    for t in args.tickers:
        df = fetch_prices(t, args.days)
        ps = summarize_prices(t, df)
        headlines = fetch_headlines_for_ticker(
            ticker=t,
            max_items=args.max_headlines,
            keywords=keywords,
            extra_queries=args.extra_query if args.extra_query else None,
        )

        news_sent_total = sum(h.sentiment for h in headlines)
        news_kw_total = sum(h.keyword_score for h in headlines)
        combined, notes = compute_combined_signal(ps, headlines)

        reports.append(TickerReport(
            ticker=t,
            price=ps,
            headlines=headlines,
            news_sentiment_total=news_sent_total,
            news_keyword_total=news_kw_total,
            combined_signal=combined,
            notes=notes,
        ))

    # Sort by strongest combined signal
    reports.sort(key=lambda r: r.combined_signal, reverse=True)

    print_report(reports, max_headlines=min(8, args.max_headlines))

    if args.out:
        write_csv(args.out, reports)
        print(f"\nWrote CSV: {args.out}")

    if args.json_out:
        write_json(args.json_out, reports)
        print(f"Wrote JSON: {args.json_out}")

if __name__ == "__main__":
    main()
