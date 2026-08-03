"""
orbit 파이프라인 로직 단위 테스트 (Step 1~5)
publish_issue.py 와 분리된 순수 로직 검증.
"""
import hashlib
import unittest

from pipeline_contracts import (
    build_finding_id,
    compute_actionability,
    is_current_fingerprint as validate_fingerprint,
    resolve_view,
    triage_pass,
)


# ─── Step 1: View 결정 ────────────────────────────────────────────────────────

class ViewResolutionTest(unittest.TestCase):
    def test_weekday_mapping(self):
        self.assertEqual(resolve_view(0), "SAFE")
        self.assertEqual(resolve_view(2), "DEP")
        self.assertEqual(resolve_view(6), "DOC")

    def test_override_ignores_weekday(self):
        self.assertEqual(resolve_view(0, override="SAFE"), "SAFE")
        self.assertEqual(resolve_view(3, override="safe"), "SAFE")
        self.assertEqual(resolve_view(6, override="ARCH"), "ARCH")

    def test_all_seven_views_covered(self):
        views = {resolve_view(d) for d in range(7)}
        self.assertEqual(views, {"SAFE", "ARCH", "DEP", "BUILD", "DATA", "OPS", "DOC"})


# ─── Step 4: actionability 채점 공식 ─────────────────────────────────────────

class ActionabilityTest(unittest.TestCase):
    def test_full_score_five(self):
        next_step = "`src/middleware/auth.ts:12`에 경로 추가 후 `npm test` 실행"
        self.assertGreaterEqual(compute_actionability(next_step), 3)

    def test_vague_step_low_score(self):
        next_step = "개선한다"
        self.assertLess(compute_actionability(next_step), 3)

    def test_with_file_path_gets_bonus(self):
        next_step = "src/utils/helper.ts:42를 수정한다"
        self.assertGreaterEqual(compute_actionability(next_step), 2)


# ─── Step 5: Triage 통과 조건 ─────────────────────────────────────────────────

class TriageTest(unittest.TestCase):
    def test_all_conditions_met(self):
        passed, reason = triage_pass(4, 3, "high", 3)
        self.assertTrue(passed)
        self.assertEqual(reason, "pass")

    def test_low_impact_skipped(self):
        passed, reason = triage_pass(3, 5, "high", 4)
        self.assertFalse(passed)
        self.assertEqual(reason, "low_impact")

    def test_low_urgency_skipped(self):
        passed, reason = triage_pass(5, 2, "high", 4)
        self.assertFalse(passed)
        self.assertEqual(reason, "low_urgency")

    def test_low_confidence_skipped(self):
        passed, reason = triage_pass(5, 5, "low", 4)
        self.assertFalse(passed)
        self.assertEqual(reason, "low_confidence")

    def test_low_actionability_skipped(self):
        passed, reason = triage_pass(4, 4, "high", 2)
        self.assertFalse(passed)
        self.assertEqual(reason, "low_actionability")

    def test_medium_confidence_passes(self):
        passed, _ = triage_pass(4, 3, "medium", 3)
        self.assertTrue(passed)

    def test_boundary_impact_4_passes(self):
        passed, _ = triage_pass(4, 3, "high", 3)
        self.assertTrue(passed)

    def test_boundary_urgency_3_passes(self):
        passed, _ = triage_pass(4, 3, "high", 3)
        self.assertTrue(passed)


# ─── Step 4: fingerprint 형식 검증 ───────────────────────────────────────────

class FingerprintTest(unittest.TestCase):
    def test_valid_fingerprint(self):
        self.assertTrue(validate_fingerprint("pipeline:owner/repo:SAFE:f-12ab34cd"))
        self.assertTrue(validate_fingerprint("pipeline:org/project:DEP:f-abcdef12"))

    def test_invalid_missing_segment(self):
        self.assertFalse(validate_fingerprint("pipeline:owner/repo:SAFE"))
        self.assertFalse(validate_fingerprint("owner/repo:SAFE:f-12ab34cd"))

    def test_invalid_empty(self):
        self.assertFalse(validate_fingerprint(""))

    def test_invalid_legacy_sequence_finding_id(self):
        self.assertFalse(validate_fingerprint("pipeline:owner/repo:SAFE:E1"))

    def test_finding_id_uses_normalized_claim_and_impact_surface(self):
        claim = "  CI   Uses Floating Node Version  "
        impact_surface = " All   Deploy Jobs "
        expected = "f-" + hashlib.sha1(
            b"ci uses floating node version\nall deploy jobs"
        ).hexdigest()[:8]

        self.assertEqual(build_finding_id(claim, impact_surface), expected)

    def test_finding_id_ignores_evidence_order_and_neighbor_findings(self):
        finding = {
            "claim": "CI uses floating Node version",
            "impact_surface": "All deploy jobs",
            "evidence": [".github/workflows/release.yml:20", "package.json:8"],
        }
        same_finding_reordered = {
            "claim": finding["claim"],
            "impact_surface": finding["impact_surface"],
            "evidence": list(reversed(finding["evidence"])),
        }
        other_finding = {
            "claim": "Docker build omits lockfile",
            "impact_surface": "Container deploy path",
            "evidence": ["Dockerfile:5"],
        }

        base_id = build_finding_id(finding["claim"], finding["impact_surface"])
        reordered_id = build_finding_id(
            same_finding_reordered["claim"],
            same_finding_reordered["impact_surface"],
        )
        with_neighbor_id = [
            build_finding_id(item["claim"], item["impact_surface"])
            for item in [other_finding, same_finding_reordered]
        ][1]

        self.assertEqual(base_id, reordered_id)
        self.assertEqual(base_id, with_neighbor_id)


if __name__ == "__main__":
    unittest.main()
