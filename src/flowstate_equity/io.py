from __future__ import annotations

import csv
from pathlib import Path

from .models import WorkEvent

REQUIRED = {
    "event_id", "occurred_at", "function", "workflow", "tool", "decision",
    "quality_score", "baseline_minutes", "actual_minutes", "baseline_cost",
    "actual_cost", "defect", "reviewer_role",
}


def load_events(path: str | Path) -> list[WorkEvent]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing columns: {', '.join(sorted(missing))}")
        events = [_parse(row) for row in reader]
    if len({event.event_id for event in events}) != len(events):
        raise ValueError("event_id values must be unique")
    return events


def _parse(row: dict[str, str]) -> WorkEvent:
    decision = row["decision"].strip().lower()
    if decision not in {"accepted", "rejected"}:
        raise ValueError(f"invalid decision: {decision}")
    quality = float(row["quality_score"])
    if not 0 <= quality <= 1:
        raise ValueError("quality_score must be between 0 and 1")
    numeric = {name: float(row[name]) for name in (
        "baseline_minutes", "actual_minutes", "baseline_cost", "actual_cost"
    )}
    if any(value < 0 for value in numeric.values()):
        raise ValueError("time and cost values cannot be negative")
    return WorkEvent(
        event_id=row["event_id"], occurred_at=row["occurred_at"],
        function=row["function"], workflow=row["workflow"], tool=row["tool"],
        decision=decision, quality_score=quality, defect=_bool(row["defect"]),
        reviewer_role=row["reviewer_role"], **numeric,
    )


def _bool(value: str) -> bool:
    normalised = value.strip().lower()
    if normalised not in {"true", "false"}:
        raise ValueError(f"invalid boolean: {value}")
    return normalised == "true"

