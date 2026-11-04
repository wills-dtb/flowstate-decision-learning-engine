from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal

Decision = Literal["accepted", "rejected"]
SavingsKind = Literal["cash", "capacity"]


@dataclass(frozen=True)
class WorkEvent:
    event_id: str
    occurred_at: str
    function: str
    workflow: str
    tool: str
    decision: Decision
    quality_score: float
    baseline_minutes: float
    actual_minutes: float
    baseline_cost: float
    actual_cost: float
    defect: bool
    reviewer_role: str

    @property
    def minutes_released(self) -> float:
        return max(0.0, self.baseline_minutes - self.actual_minutes)

    @property
    def cost_avoided(self) -> float:
        return max(0.0, self.baseline_cost - self.actual_cost)


@dataclass(frozen=True)
class ControlPolicy:
    min_observations: int = 3
    min_acceptance_rate: float = 0.65
    min_quality_score: float = 0.8
    max_defect_rate: float = 0.1
    require_cross_function_evidence: bool = False
    cash_requires_evidence: bool = True


@dataclass(frozen=True)
class Recommendation:
    workflow: str
    tool: str
    observations: int
    functions: tuple[str, ...]
    acceptance_rate: float
    posterior_acceptance: float
    mean_quality: float
    defect_rate: float
    status: Literal["approved", "blocked"]
    reasons: tuple[str, ...]

    def to_dict(self) -> dict:
        value = asdict(self)
        value["functions"] = list(self.functions)
        value["reasons"] = list(self.reasons)
        return value


@dataclass(frozen=True)
class SavingsEvidence:
    recurring_spend_reduced: bool = False
    budget_removed: bool = False
    contract_reduced: bool = False

    @property
    def supports_cash(self) -> bool:
        return any(asdict(self).values())

