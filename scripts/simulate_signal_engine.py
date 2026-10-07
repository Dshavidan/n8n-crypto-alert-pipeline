#!/usr/bin/env python3
"""Local simulator for the n8n crypto signal logic."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SEVERITY_ORDER = {"normal": 0, "warning": 1, "critical": 2}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def score_coin(coin: dict[str, Any], market: dict[str, Any], currency: str) -> dict[str, Any]:
    coin_id = coin["id"]
    record = market.get(coin_id, {})
    price = record.get(currency)
    change_key = f"{currency}_24h_change"
    change = record.get(change_key)

    if price is None or change is None:
        return {
            "id": coin_id,
            "symbol": coin["symbol"],
            "name": coin["name"],
            "price": None,
            "change_24h_pct": None,
            "direction": "unknown",
            "severity": "warning",
            "alert": True,
            "threshold_hit": None,
            "reason": "missing_price_or_change",
        }

    change_value = round(float(change), 2)
    abs_change = abs(change_value)
    warning_threshold = float(coin["warning_abs_pct"])
    critical_threshold = float(coin["critical_abs_pct"])

    if abs_change >= critical_threshold:
        severity = "critical"
        threshold_hit = critical_threshold
    elif abs_change >= warning_threshold:
        severity = "warning"
        threshold_hit = warning_threshold
    else:
        severity = "normal"
        threshold_hit = None

    return {
        "id": coin_id,
        "symbol": coin["symbol"],
        "name": coin["name"],
        "price": round(float(price), 2),
        "change_24h_pct": change_value,
        "direction": "up" if change_value >= 0 else "down",
        "severity": severity,
        "alert": severity != "normal",
        "threshold_hit": threshold_hit,
    }


def build_summary(config: dict[str, Any], market: dict[str, Any]) -> dict[str, Any]:
    currency = config["currency"]
    rows = [score_coin(coin, market, currency) for coin in config["coins"]]
    alerts = [row for row in rows if row["alert"]]
    highest = "normal"
    if alerts:
        highest = max(alerts, key=lambda row: SEVERITY_ORDER[row["severity"]])["severity"]

    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "currency": currency,
        "asset_count": len(rows),
        "alert_count": len(alerts),
        "highest_severity": highest,
        "alerts": alerts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate the crypto alert scoring logic.")
    parser.add_argument("--config", type=Path, default=Path("config/watchlist.example.json"))
    parser.add_argument("--input", type=Path, default=Path("docs/sample-market-response.json"))
    args = parser.parse_args()

    summary = build_summary(load_json(args.config), load_json(args.input))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
