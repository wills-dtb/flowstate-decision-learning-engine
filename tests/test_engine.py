import unittest

from flowstate_equity.engine import classify_savings, learn_recommendations
from flowstate_equity.io import load_events
from flowstate_equity.models import ControlPolicy, SavingsEvidence


def events():
    return load_events("fixtures/work_events.csv")


class EngineTests(unittest.TestCase):
    def test_good_cross_function_pattern_is_approved(self):
        recs = learn_recommendations(events(), ControlPolicy(require_cross_function_evidence=True))
        campaign = next(r for r in recs if r.workflow == "campaign-brief")
        self.assertEqual(campaign.status, "approved")
        self.assertEqual(campaign.posterior_acceptance, 0.8)
        self.assertEqual(len(campaign.functions), 3)


    def test_low_quality_pattern_is_blocked_with_reasons(self):
        recs = learn_recommendations(events(), ControlPolicy())
        policy = next(r for r in recs if r.workflow == "policy-summary")
        self.assertEqual(policy.status, "blocked")
        self.assertIn("mean quality below threshold", policy.reasons)
        self.assertIn("acceptance evidence below threshold", policy.reasons)


    def test_capacity_is_not_mislabelled_as_cash(self):
        result = classify_savings(events(), SavingsEvidence())
        self.assertGreater(result["released_capacity_hours"], 0)
        self.assertEqual(result["realised_cash_savings"], 0)
        self.assertGreater(result["unvalidated_cost_avoidance"], 0)


    def test_cash_requires_explicit_evidence(self):
        result = classify_savings(events(), SavingsEvidence(contract_reduced=True))
        self.assertEqual(result["realised_cash_savings"], 248)
        self.assertEqual(result["unvalidated_cost_avoidance"], 0)


if __name__ == "__main__":
    unittest.main()

