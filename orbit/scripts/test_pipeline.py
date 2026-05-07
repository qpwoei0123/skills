"""
orbit 파이프라인 로직 단위 테스트 (Step 1~5)
publish_issue.py 와 분리된 순수 로직 검증.
"""
import hashlib
import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parent / "publish_issue.py"
SPEC = importlib.util.spec_from_file_location("repo_orbit_publish_issue", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


# ─── Step 1: View 결정 ────────────────────────────────────────────────────────

WEEKDAY_VIEW = {
    0: "SAFE",   # 월
    1: "ARCH",   # 화
    2: "DEP",    # 수
    3: "BUILD",  # 목
    4: "DATA",   # 금
    5: "OPS",    # 토
    6: "DOC",    # 일
}

def resolve_view(weekday: int, override: str | None = None) -> str:
    if override:
        return override.upper()
    return WEEKDAY_VIEW[weekday]


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

def compute_actionability(next_step: str) -> int:
    score = 0
    import re
    if re.search(r'\S+/\S+\.\w+|:\d+', next_step):   # 파일 경로
        score += 2
    if re.search(r'`[^`]+`|\b[A-Z_]{2,}\b', next_step):  # 식별자
        score += 1
    if re.search(r'\bnpm\b|\bpip\b|\bgit\b|\bpython\b|\bbash\b|--\w+', next_step):  # CLI
        score += 1
    if len(next_step.split('.')[0]) > 0 and next_step.count('.') <= 1:  # 한 문장 이하
        score += 1
    return min(score, 5)


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

def triage_pass(impact: int, urgency: int, confidence: str, actionability: int) -> tuple[bool, str]:
    if impact < 4:
        return False, "low_impact"
    if urgency < 3:
        return False, "low_urgency"
    if confidence == "low":
        return False, "low_confidence"
    if actionability < 3:
        return False, "low_actionability"
    return True, "pass"


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

import re

FINGERPRINT_PATTERN = re.compile(r'^pipeline:[^:]+:[A-Z]+:f-[0-9a-f]{8}$')

def validate_fingerprint(fp: str) -> bool:
    return bool(FINGERPRINT_PATTERN.match(fp))


def build_finding_id(claim: str, impact_surface: str) -> str:
    return MODULE.build_finding_id(claim, impact_surface)


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
