import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_DIR = Path(__file__).resolve().parent


def load_module(name: str):
    path = SCRIPT_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"repo_orbit_cleanup_{name}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CleanupIssueTest(unittest.TestCase):
    def setUp(self):
        self.classify = load_module("classify")
        self.cleanup = load_module("cleanup_issue")
        self.memory_bridge = load_module("memory_bridge")

    def body(self, fingerprint, evidence="src/app/service.py:12"):
        return "\n".join(
            [
                "## 근거",
                f"- {evidence}",
                "",
                "format_version: orbit/v2.1",
                f"<!-- orbit-fingerprint: {fingerprint} -->",
            ]
        )

    def issue(self, number, title, fingerprint, created_at, labels=None, body=None):
        return {
            "number": number,
            "title": title,
            "body": body if body is not None else self.body(fingerprint),
            "state": "open",
            "created_at": created_at,
            "updated_at": created_at,
            "labels": labels or [],
            "comments": [],
            "html_url": f"https://github.com/owner/repo/issues/{number}",
        }

    def test_parses_current_orbit_fingerprint_footer(self):
        fingerprint = "pipeline:owner/repo:BUILD:f-11111111"
        parsed = self.classify.parse_fingerprint(self.body(fingerprint))

        self.assertEqual(parsed.fingerprint, fingerprint)
        self.assertEqual(parsed.repo_scope, "owner/repo")
        self.assertEqual(parsed.view, "BUILD")
        self.assertEqual(parsed.finding_id, "f-11111111")

    def test_duplicate_same_fingerprint_keeps_oldest_open_issue(self):
        fingerprint = "pipeline:owner/repo:SAFE:f-11111111"
        issues = [
            self.issue(9, "[view: SAFE] duplicated copy", fingerprint, "2026-05-03T00:00:00Z"),
            self.issue(2, "[view: SAFE] canonical", fingerprint, "2026-05-01T00:00:00Z"),
        ]

        findings = self.classify.classify_issues(issues)
        duplicate = next(item for item in findings if item.issue["number"] == 9)

        self.assertEqual(duplicate.category, "DUP")
        self.assertEqual(duplicate.confidence, "high")
        self.assertEqual(duplicate.canonical_issue["number"], 2)
        self.assertIn("cleanup:duplicate", duplicate.labels)
        self.assertTrue(duplicate.close_allowed_by_classification)

    def test_batch_group_uses_shared_files_and_module_prefix_without_closing(self):
        issues = [
            self.issue(
                1,
                "[view: BUILD] CI script drift",
                "pipeline:owner/repo:BUILD:f-11111111",
                "2026-05-01T00:00:00Z",
                body=self.body("pipeline:owner/repo:BUILD:f-11111111", "src/payments/build.py:10"),
            ),
            self.issue(
                2,
                "[view: BUILD] local build mismatch",
                "pipeline:owner/repo:BUILD:f-22222222",
                "2026-05-08T00:00:00Z",
                body=self.body("pipeline:owner/repo:BUILD:f-22222222", "src/payments/build.py:30"),
            ),
        ]

        findings = self.classify.classify_issues(issues)
        batch = [item for item in findings if item.category == "BATCH"]

        self.assertEqual({item.issue["number"] for item in batch}, {1, 2})
        self.assertTrue(all(item.confidence == "low" for item in batch))
        self.assertTrue(all("cleanup:batch:src/payments" in item.labels for item in batch))
        self.assertTrue(all(not item.close_allowed_by_classification for item in batch))

    def test_resolved_high_requires_missing_evidence_and_merged_pr_reference(self):
        issue = self.issue(
            7,
            "[view: DATA] stale schema warning",
            "pipeline:owner/repo:DATA:f-77777777",
            "2026-05-01T00:00:00Z",
            body=self.body("pipeline:owner/repo:DATA:f-77777777", "src/schema.py:44"),
        )

        with tempfile.TemporaryDirectory() as tmp:
            findings = self.classify.classify_issues(
                [issue],
                repo_path=Path(tmp),
                merged_issue_numbers={7},
            )

        resolved = next(item for item in findings if item.issue["number"] == 7)
        self.assertEqual(resolved.category, "RESOLVED")
        self.assertEqual(resolved.confidence, "high")
        self.assertIn("cleanup:auto-resolved", resolved.labels)
        self.assertTrue(resolved.close_allowed_by_classification)

    def test_duplicate_takes_priority_over_resolved_for_same_issue(self):
        fingerprint = "pipeline:owner/repo:SAFE:f-11111111"
        issues = [
            self.issue(9, "[view: SAFE] copy", fingerprint, "2026-05-03T00:00:00Z"),
            self.issue(2, "[view: SAFE] canonical", fingerprint, "2026-05-01T00:00:00Z"),
        ]

        with tempfile.TemporaryDirectory() as tmp:
            findings = self.classify.classify_issues(
                issues,
                repo_path=Path(tmp),
                merged_issue_numbers={9},
            )

        issue_9_findings = [item for item in findings if item.issue["number"] == 9]
        self.assertEqual([item.category for item in issue_9_findings], ["DUP"])

    def test_close_gate_holds_until_trust_ramp_completes(self):
        fingerprint = "pipeline:owner/repo:SAFE:f-11111111"
        duplicate = self.issue(9, "[view: SAFE] copy", fingerprint, "2026-05-03T00:00:00Z")
        canonical = self.issue(2, "[view: SAFE] canonical", fingerprint, "2026-05-01T00:00:00Z")

        plan = self.cleanup.build_cleanup_plan(
            [duplicate, canonical],
            repo_url="https://github.com/owner/repo",
            cleanup_log={"auto_close_runs": 2},
        )
        duplicate_action = next(item for item in plan["actions"] if item["issue_number"] == 9)

        self.assertEqual(duplicate_action["category"], "DUP")
        self.assertFalse(duplicate_action["close"])
        self.assertIn("cleanup:held-trust-ramp", duplicate_action["labels"])
        self.assertIn("auto_close_runs", duplicate_action["hold_reasons"])

    def test_memory_bridge_marks_closed_suppressed_and_batch_tags(self):
        memory = {
            "known_findings": {
                "pipeline:owner/repo:DATA:f-11111111": {"status": "open"},
                "pipeline:owner/repo:DATA:f-22222222": {"status": "open"},
                "pipeline:owner/repo:DATA:f-33333333": {"status": "open"},
            }
        }
        actions = [
            {
                "category": "RESOLVED",
                "confidence": "high",
                "close": True,
                "fingerprint": "pipeline:owner/repo:DATA:f-11111111",
            },
            {
                "category": "DUP",
                "confidence": "high",
                "close": True,
                "fingerprint": "pipeline:owner/repo:DATA:f-22222222",
                "canonical_fingerprint": "pipeline:owner/repo:DATA:f-99999999",
            },
            {
                "category": "BATCH",
                "confidence": "low",
                "close": False,
                "fingerprint": "pipeline:owner/repo:DATA:f-33333333",
                "batch_module": "src/payments",
            },
        ]

        updated = self.memory_bridge.apply_cleanup_actions(memory, actions)

        self.assertEqual(
            updated["known_findings"]["pipeline:owner/repo:DATA:f-11111111"]["status"],
            "closed",
        )
        duplicate = updated["known_findings"]["pipeline:owner/repo:DATA:f-22222222"]
        self.assertEqual(duplicate["status"], "suppressed")
        self.assertEqual(duplicate["alias_of"], "pipeline:owner/repo:DATA:f-99999999")
        self.assertIn(
            "batch:src/payments",
            updated["known_findings"]["pipeline:owner/repo:DATA:f-33333333"]["cleanup_tags"],
        )

    def test_run_cleanup_persists_only_successfully_applied_actions(self):
        first = "pipeline:owner/repo:SAFE:f-11111111"
        second = "pipeline:owner/repo:SAFE:f-22222222"
        issues = [
            self.issue(
                9,
                "[view: SAFE] first copy",
                first,
                "2026-05-03T00:00:00Z",
                body=self.body(first, "src/first.py:1"),
            ),
            self.issue(
                2,
                "[view: SAFE] first canonical",
                first,
                "2026-05-01T00:00:00Z",
                body=self.body(first, "src/first.py:1"),
            ),
            self.issue(
                10,
                "[view: SAFE] second copy",
                second,
                "2026-05-03T00:00:00Z",
                body=self.body(second, "src/second.py:1"),
            ),
            self.issue(
                3,
                "[view: SAFE] second canonical",
                second,
                "2026-05-01T00:00:00Z",
                body=self.body(second, "src/second.py:1"),
            ),
        ]

        with (
            patch.object(self.cleanup.orbit_pub, "load_auth", return_value=("token", "https://api.github.com")),
            patch.object(
                self.cleanup,
                "apply_remote_action",
                side_effect=[None, self.cleanup.orbit_pub.PublishFallback("boom")],
            ),
            patch.object(
                self.cleanup.memory_bridge,
                "load_cleanup_log",
                return_value={"auto_close_runs": 3, "history": []},
            ),
            patch.object(self.cleanup.memory_bridge, "update_view_memories") as update_view_memories,
            patch.object(self.cleanup.memory_bridge, "record_cleanup_history") as record_cleanup_history,
        ):
            plan = self.cleanup.run_cleanup(
                "https://github.com/owner/repo",
                issues=issues,
                dry_run=False,
            )

        self.assertEqual(plan["summary"]["errors"], 1)
        successful_actions = update_view_memories.call_args.args[1]
        self.assertEqual([action["issue_number"] for action in successful_actions], [9])
        self.assertEqual(record_cleanup_history.call_args.args[1]["closed"], 1)


if __name__ == "__main__":
    unittest.main()
