from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Tuple

from domain.models import FeatureVector


class ScoreComponent(ABC):
    @abstractmethod
    def compute(self, features: FeatureVector) -> Tuple[float, List[str]]:
        """
        Compute a score component.
        
        Returns:
            (score, reasons) where score is typically -1.0 to 1.0
            and reasons is a list of explanation strings.
        """
        pass
