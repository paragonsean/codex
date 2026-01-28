from __future__ import annotations

from typing import Dict

from domain.enums import RegimeLabel


class RegimeDetector:
    @staticmethod
    def detect_regime(technical: Dict[str, float]) -> RegimeLabel:
        volatility_20d = technical.get("volatility_20d", 0.0)
        
        if volatility_20d < 0.2:
            return RegimeLabel.LOW
        elif volatility_20d < 0.35:
            return RegimeLabel.NORMAL
        elif volatility_20d < 0.5:
            return RegimeLabel.ELEVATED
        else:
            return RegimeLabel.HIGH
    
    @staticmethod
    def get_regime_multipliers(regime: RegimeLabel) -> Dict[str, float]:
        multipliers = {
            RegimeLabel.LOW: {"opportunity": 1.2, "sell_risk": 0.8},
            RegimeLabel.NORMAL: {"opportunity": 1.0, "sell_risk": 1.0},
            RegimeLabel.ELEVATED: {"opportunity": 0.8, "sell_risk": 1.2},
            RegimeLabel.HIGH: {"opportunity": 0.6, "sell_risk": 1.5},
            RegimeLabel.UNKNOWN: {"opportunity": 1.0, "sell_risk": 1.0},
        }
        
        return multipliers.get(regime, {"opportunity": 1.0, "sell_risk": 1.0})
