import json
import os
from typing import Any, Dict, List, Optional


class SettingsManager:
    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = settings_file
        self._settings: Dict[str, Any] = {}
        self._load()

    def _default_settings(self) -> Dict[str, Any]:
        return {
            "portfolio_file": "portfolio.json",
            "default_keywords": ["AI", "HBM", "DRAM", "NAND", "chipsets", "semiconductor", "datacenter", "cloud"],
            "default_days": 180,
            "default_max_headlines": 20,
            "ticker_aliases": {"BRK.B": "BRK-B"},
        }

    def _load(self) -> None:
        self._settings = self._default_settings()
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    self._settings.update(loaded)
            except Exception:
                pass

    def save(self) -> None:
        with open(self.settings_file, "w") as f:
            json.dump(self._settings, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._settings[key] = value

    @property
    def portfolio_file(self) -> str:
        return str(self.get("portfolio_file"))

    @property
    def default_keywords(self) -> List[str]:
        return list(self.get("default_keywords", []))

    @property
    def default_days(self) -> int:
        return int(self.get("default_days", 180))

    @property
    def default_max_headlines(self) -> int:
        return int(self.get("default_max_headlines", 20))

    def normalize_ticker(self, ticker: str) -> str:
        t = ticker.strip().upper()
        aliases: Dict[str, str] = self.get("ticker_aliases", {}) or {}
        return aliases.get(t, t)
