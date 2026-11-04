from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from typing import Iterable

from .models import ControlPolicy, Recommendation, SavingsEvidence, WorkEvent


def learn_recommendations(
    events: Iterable[WorkEvent], policy: ControlPolicy
) -> list[Recommendation]:
    """Learn cohort recommendations, then pass every candidate through controls.

    A Beta(1,1) posterior prevents tiny samples from appearing certain. The
    controls are intentionally deterministic and explain every blocked result.
    """
    cohorts: dict[tuple[str, str], list[WorkEvent]] = defaultdict(list)
    for event in events:
        cohorts[(event.workflow, event.tool)].append(event)

    results = []
    for (workflow, tool), rows in sorted(cohorts.items()):
        n = len(rows)
        accepted = sum(row.decision == "accepted" for row in rows)
        acceptance = accepted / n
        posterior = (accepted + 1) / (n + 2)
        quality = sum(row.quality_score for row in rows) / n
        defects = sum(row.defect for row in rows) / n
        functions = tuple(sorted({row.function for row in rows}))
        reasons = []
        if n < policy.min_observations:
            reasons.append(f"needs {policy.min_observations - n} more observation(s)")
        if posterior < policy.min_acceptance_rate:
            reasons.append("acceptance evidence below threshold")
        if quality < policy.min_quality_score:
            reasons.append("mean quality below threshold")
        if defects > policy.max_defect_rate:
            reasons.append("defect rate exceeds threshold")
        if policy.require_cross_function_evidence and len(functions) < 2:
            reasons.append("cross-function evidence required")
        results.append(Recommendation(
            workflow=workflow, tool=tool, observations=n, functions=functions,
            acceptance_rate=round(acceptance, 4),
            posterior_acceptance=round(posterior, 4),
            mean_quality=round(quality, 4), defect_rate=round(defects, 4),
            status="blocked" if reasons else "approved", reasons=tuple(reasons),
        ))
    return results


def classify_savings(
    events: Iterable[WorkEvent], evidence: SavingsEvidence
) -> dict:
    """Keep released time separate from cash unless spend evidence exists."""
    accepted = [event for event in events if event.decision == "accepted"]
    capacity_hours = sum(event.minutes_released for event in accepted) / 60
    potential_cost = sum(event.cost_avoided for event in accepted)
    cash = potential_cost if evidence.supports_cash else 0.0
    return {
        "realised_cash_savings": round(cash, 2),
        "released_capacity_hours": round(capacity_hours, 2),
        "unvalidated_cost_avoidance": round(potential_cost - cash, 2),
        "cash_evidence": asdict(evidence),
        "method": "accepted work only; no rejected-work benefits counted",
    }


def build_report(events, policy, evidence) -> dict:
    return {
        "recommendations": [r.to_dict() for r in learn_recommendations(events, policy)],
        "savings": classify_savings(events, evidence),
        "controls": asdict(policy),
        "lineage": {"input_events": len(events), "unique_event_ids": len({e.event_id for e in events})},
    }

