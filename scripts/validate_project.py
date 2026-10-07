#!/usr/bin/env python3
"""Validate repository artifacts without third-party dependencies."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise SystemExit(f"Validation failed: {message}")


def load_json(relative_path: str):
    path = ROOT / relative_path
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        fail(f"{relative_path} is not valid JSON: {exc}")


def validate_workflow() -> None:
    workflow = load_json("workflows/crypto-alert-pipeline.json")
    nodes = workflow.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        fail("workflow has no nodes")

    names = [node.get("name") for node in nodes]
    if len(names) != len(set(names)):
        fail("workflow node names must be unique")

    known_names = set(names)
    connections = workflow.get("connections", {})
    for source, outputs in connections.items():
        if source not in known_names:
            fail(f"connection source does not exist: {source}")
        for output_group in outputs.get("main", []):
            for edge in output_group:
                target = edge.get("node")
                if target not in known_names:
                    fail(f"connection target does not exist: {target}")

    node_types = {node.get("type") for node in nodes}
    required_types = {
        "n8n-nodes-base.scheduleTrigger",
        "n8n-nodes-base.manualTrigger",
        "n8n-nodes-base.httpRequest",
        "n8n-nodes-base.code",
        "n8n-nodes-base.if",
    }
    missing = required_types - node_types
    if missing:
        fail(f"workflow is missing required node types: {sorted(missing)}")


def validate_config() -> None:
    config = load_json("config/watchlist.example.json")
    coins = config.get("coins", [])
    if not coins:
        fail("watchlist has no coins")
    for coin in coins:
        for key in ("id", "symbol", "name", "warning_abs_pct", "critical_abs_pct"):
            if key not in coin:
                fail(f"watchlist coin missing key: {key}")
        if float(coin["warning_abs_pct"]) >= float(coin["critical_abs_pct"]):
            fail(f"warning threshold must be below critical threshold for {coin['id']}")


def validate_sample_output() -> None:
    output = load_json("docs/sample-output.json")
    if output.get("alert_count", 0) < 1:
        fail("sample output should demonstrate at least one alert")
    if output.get("highest_severity") not in {"normal", "warning", "critical"}:
        fail("sample output has invalid highest_severity")


def validate_simulator() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/simulate_signal_engine.py",
            "--config",
            "config/watchlist.example.json",
            "--input",
            "docs/sample-market-response.json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    output = json.loads(result.stdout)
    if output["alert_count"] < 1:
        fail("simulator should produce at least one sample alert")
    if output["asset_count"] != 3:
        fail("simulator should score three sample assets")


def validate_readme() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    required_phrases = [
        "Business Problem",
        "Architecture",
        "Quick Start",
        "Local Validation",
        "Portfolio Notes",
    ]
    for phrase in required_phrases:
        if phrase not in readme:
            fail(f"README missing section: {phrase}")


def main() -> None:
    load_json("docs/sample-market-response.json")
    validate_workflow()
    validate_config()
    validate_sample_output()
    validate_simulator()
    validate_readme()
    print("All project validation checks passed.")


if __name__ == "__main__":
    main()
