import csv
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class PortfolioPosition:
    ticker: str
    shares: float
    cost_basis: float
    purchase_date: str = ""
    notes: str = ""


class PortfolioManager:
    def __init__(self, portfolio_file: str):
        self.portfolio_file = portfolio_file

    def load(self) -> Dict:
        if self.portfolio_file and os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, "r") as f:
                    data = json.load(f)
                if isinstance(data, dict) and "positions" in data:
                    return data
            except Exception:
                pass
        return {"portfolio_name": "My Portfolio", "positions": []}

    def save(self, portfolio: Dict) -> None:
        if not self.portfolio_file:
            raise ValueError("portfolio_file is not set")
        with open(self.portfolio_file, "w") as f:
            json.dump(portfolio, f, indent=2)

    def set_portfolio_file(self, portfolio_file: str) -> None:
        self.portfolio_file = portfolio_file

    def add_position(self, portfolio: Dict, position: PortfolioPosition) -> Tuple[Dict, str]:
        positions: List[Dict] = portfolio.get("positions", [])
        ticker = position.ticker.strip().upper()

        for existing in positions:
            if existing.get("ticker", "").upper() == ticker:
                return portfolio, f"{ticker} already exists in portfolio"

        positions.append(
            {
                "ticker": ticker,
                "shares": float(position.shares),
                "cost_basis": float(position.cost_basis),
                "purchase_date": position.purchase_date,
                "notes": position.notes,
            }
        )
        portfolio["positions"] = positions
        return portfolio, "ok"

    def remove_position(self, portfolio: Dict, ticker: str) -> Tuple[Dict, bool]:
        ticker_u = ticker.strip().upper()
        positions: List[Dict] = portfolio.get("positions", [])
        before = len(positions)
        positions = [p for p in positions if p.get("ticker", "").upper() != ticker_u]
        portfolio["positions"] = positions
        return portfolio, len(positions) != before

    def edit_position(
        self,
        portfolio: Dict,
        ticker: str,
        shares: Optional[float] = None,
        cost_basis: Optional[float] = None,
        purchase_date: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Tuple[Dict, bool]:
        ticker_u = ticker.strip().upper()
        positions: List[Dict] = portfolio.get("positions", [])
        updated = False
        for p in positions:
            if p.get("ticker", "").upper() == ticker_u:
                if shares is not None:
                    p["shares"] = float(shares)
                if cost_basis is not None:
                    p["cost_basis"] = float(cost_basis)
                if purchase_date is not None:
                    p["purchase_date"] = purchase_date
                if notes is not None:
                    p["notes"] = notes
                updated = True
                break
        portfolio["positions"] = positions
        return portfolio, updated

    def import_csv(self, csv_path: str) -> Dict:
        if not os.path.exists(csv_path):
            raise FileNotFoundError(csv_path)

        imported: List[Dict] = []
        with open(csv_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            required = {"ticker", "num_shares", "cost_per_share"}
            if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                raise ValueError(f"CSV must contain columns: {', '.join(sorted(required))}")

            for row in reader:
                ticker = (row.get("ticker") or "").strip().upper()
                if not ticker:
                    continue

                shares = float(row.get("num_shares") or 0)
                cost = float(row.get("cost_per_share") or 0)
                if shares <= 0 or cost <= 0:
                    continue

                imported.append(
                    {
                        "ticker": ticker,
                        "shares": shares,
                        "cost_basis": cost,
                        "purchase_date": (row.get("purchase_date") or "").strip(),
                        "notes": (row.get("notes") or "").strip(),
                    }
                )

        return {"portfolio_name": "Imported Portfolio", "positions": imported}

    def export_csv(self, portfolio: Dict, csv_path: str) -> None:
        positions: List[Dict] = portfolio.get("positions", [])
        fieldnames = ["ticker", "num_shares", "cost_per_share", "purchase_date", "notes"]

        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for p in positions:
                writer.writerow(
                    {
                        "ticker": p.get("ticker", ""),
                        "num_shares": p.get("shares", ""),
                        "cost_per_share": p.get("cost_basis", ""),
                        "purchase_date": p.get("purchase_date", ""),
                        "notes": p.get("notes", ""),
                    }
                )
