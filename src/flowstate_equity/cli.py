from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

from .engine import build_report
from .io import load_events
from .models import ControlPolicy, SavingsEvidence


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Flowstate Decision Learning & Savings Engine")
    p.add_argument("events", help="CSV of reviewed AI-assisted work events")
    p.add_argument("--output", "-o", help="write report JSON to this path")
    p.add_argument("--cross-function", action="store_true", help="require evidence from 2+ functions")
    p.add_argument("--cash-evidence", choices=["none", "spend", "budget", "contract"], default="none")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    events = load_events(args.events)
    policy = replace(ControlPolicy(), require_cross_function_evidence=args.cross_function)
    evidence = SavingsEvidence(
        recurring_spend_reduced=args.cash_evidence == "spend",
        budget_removed=args.cash_evidence == "budget",
        contract_reduced=args.cash_evidence == "contract",
    )
    report = build_report(events, policy, evidence)
    rendered = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

