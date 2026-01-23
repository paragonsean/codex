from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from domain.models import Recommendation, SignalScore


class AlertsManager:
    def __init__(self, state_file: str = "alerts_state.json"):
        self.state_file = Path(state_file)
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, any]:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {"alerts": [], "last_check": None}
        return {"alerts": [], "last_check": None}

    def _save_state(self) -> None:
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def check_alerts(
        self,
        ticker: str,
        signal: SignalScore,
        recommendation: Recommendation,
    ) -> List[Dict[str, any]]:
        alerts = []
        
        if signal.sell_risk >= 80:
            alerts.append({
                "ticker": ticker,
                "type": "high_sell_risk",
                "severity": "critical",
                "message": f"{ticker}: High sell risk ({signal.sell_risk:.1f})",
                "timestamp": datetime.now().isoformat(),
            })
        
        if signal.opportunity >= 80:
            alerts.append({
                "ticker": ticker,
                "type": "high_opportunity",
                "severity": "info",
                "message": f"{ticker}: Strong buy opportunity ({signal.opportunity:.1f})",
                "timestamp": datetime.now().isoformat(),
            })
        
        if recommendation.action.value == "sell" and recommendation.urgency == "high":
            alerts.append({
                "ticker": ticker,
                "type": "urgent_sell",
                "severity": "critical",
                "message": f"{ticker}: Urgent sell recommendation",
                "timestamp": datetime.now().isoformat(),
            })
        
        for alert in alerts:
            self.state["alerts"].append(alert)
        
        self.state["last_check"] = datetime.now().isoformat()
        self._save_state()
        
        return alerts

    def get_active_alerts(self, severity: Optional[str] = None) -> List[Dict[str, any]]:
        alerts = self.state.get("alerts", [])
        
        if severity:
            alerts = [a for a in alerts if a.get("severity") == severity]
        
        return alerts

    def clear_alerts(self, ticker: Optional[str] = None) -> None:
        if ticker:
            self.state["alerts"] = [
                a for a in self.state.get("alerts", [])
                if a.get("ticker") != ticker
            ]
        else:
            self.state["alerts"] = []
        
        self._save_state()
