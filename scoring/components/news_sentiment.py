from __future__ import annotations

from typing import List, Tuple

from domain.models import FeatureVector
from scoring.scorer import ScoreComponent


class NewsSentimentComponent(ScoreComponent):
    def compute(self, features: FeatureVector) -> Tuple[float, List[str]]:
        if not features.news:
            return 0.0, ["No news data available"]
        
        score = 0.0
        reasons = []
        
        avg_sentiment = features.news.get("avg_sentiment", 0.0)
        positive_count = features.news.get("positive_count", 0)
        negative_count = features.news.get("negative_count", 0)
        total_count = features.news.get("total_count", 0)
        
        if avg_sentiment > 0.3:
            score += 0.4
            reasons.append(f"Positive news sentiment: {avg_sentiment:.2f}")
        elif avg_sentiment < -0.3:
            score -= 0.4
            reasons.append(f"Negative news sentiment: {avg_sentiment:.2f}")
        
        if total_count > 0:
            pos_ratio = positive_count / total_count
            neg_ratio = negative_count / total_count
            
            if pos_ratio > 0.6:
                score += 0.2
                reasons.append(f"High positive news ratio: {pos_ratio:.1%}")
            elif neg_ratio > 0.6:
                score -= 0.2
                reasons.append(f"High negative news ratio: {neg_ratio:.1%}")
        
        avg_quality = features.news.get("avg_quality", 0.0)
        if avg_quality > 0.7:
            score *= 1.2
            reasons.append(f"High quality news sources: {avg_quality:.2f}")
        
        return max(-1.0, min(1.0, score)), reasons
