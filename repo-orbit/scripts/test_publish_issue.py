import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).resolve().parent / "publish_issue.py"
SPEC = importlib.util.spec_from_file_location("repo_orbit_publish_issue", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class PublishIssueTest(unittest.TestCase):
    def make_body(self, fingerprint):
        return "\n".join([
            "본문",
            "",
            "format_version: repo-orbit/v2",
            f"fingerprint: {fingerprint}",
        ])

    def test_missing_token_returns_manual_payload(self):
        fingerprint = "pipeline:owner/repo:SAFE:E1"
        with patch.object(MODULE, "load_auth", return_value=(None, "https://api.github.com")):
            result = MODULE.publish_issue(
                "https://github.com/owner/repo",
                "[view: SAFE] 테스트",
                self.make_body(fingerprint),
                fingerprint,
                ["automation"],
            )

        self.assertEqual(result["action"], "manual_required")
        self.assertIn("인증 토큰", result["reason"])
        self.assertIn(f"fingerprint: {fingerprint}", result["copy_paste_text"])

    def test_github_pagination_finds_issue_on_second_page(self):
        responses = [
            (
                [{
                    "number": 1,
                    "body": "\n".join([
                        "본문",
                        "",
                        "format_version: repo-orbit/v2",
                        "fingerprint: pipeline:owner/repo:SAFE:E0",
                    ]),
                }],
                {"Link": '<https://api.github.com/next>; rel="next"'},
            ),
            (
                [{
                    "number": 7,
                    "body": "\n".join([
                        "본문",
                        "",
                        "format_version: repo-orbit/v2",
                        "fingerprint: pipeline:owner/repo:SAFE:E1",
                    ]),
                }],
                {"Link": ""},
            ),
        ]

        def fake_api_request(method, url, platform, token, data=None):
            return responses.pop(0)

        with patch.object(MODULE, "api_request", side_effect=fake_api_request):
            issue = MODULE.find_existing_issue(
                "github",
                "https://api.github.com",
                "owner/repo",
                "token",
                "pipeline:owner/repo:SAFE:E1",
            )

        self.assertEqual(issue["number"], 7)
        self.assertEqual(len(responses), 0)

    def test_find_existing_issue_requires_exact_fingerprint_match(self):
        responses = [
            (
                [{
                    "number": 1,
                    "body": "\n".join([
                        "본문",
                        "",
                        "format_version: repo-orbit/v2",
                        "fingerprint: pipeline:owner/repo:SAFE:E10",
                    ]),
                }],
                {"Link": '<https://api.github.com/next>; rel="next"'},
            ),
            (
                [{
                    "number": 2,
                    "body": "\n".join([
                        "본문",
                        "",
                        "format_version: repo-orbit/v2",
                        "fingerprint: pipeline:owner/repo:SAFE:E1",
                    ]),
                }],
                {"Link": ""},
            ),
        ]

        def fake_api_request(method, url, platform, token, data=None):
            return responses.pop(0)

        with patch.object(MODULE, "api_request", side_effect=fake_api_request):
            issue = MODULE.find_existing_issue(
                "github",
                "https://api.github.com",
                "owner/repo",
                "token",
                "pipeline:owner/repo:SAFE:E1",
            )

        self.assertEqual(issue["number"], 2)
        self.assertEqual(len(responses), 0)

    def test_invalid_contract_returns_manual_payload(self):
        result = MODULE.publish_issue(
            "https://github.com/owner/repo",
            "[view: SAFE] 테스트",
            "본문만 있음",
            "pipeline:owner/repo:SAFE:E2",
            ["automation"],
        )

        self.assertEqual(result["action"], "manual_required")
        self.assertIn("format_version", result["reason"])

    def test_gitlab_closed_issue_reopens_on_update(self):
        fingerprint = "pipeline:owner/repo:BUILD:E1"
        with patch.object(MODULE, "load_auth", return_value=("token", "https://gitlab.example.com")):
            with patch.object(MODULE, "gitlab_ensure_labels"):
                with patch.object(
                    MODULE,
                    "find_existing_issue",
                    return_value={"iid": 9, "state": "closed"},
                ):
                    with patch.object(
                        MODULE,
                        "gitlab_update",
                        return_value={"iid": 9, "web_url": "https://gitlab.example.com/owner/repo/-/issues/9"},
                    ) as update_mock:
                        result = MODULE.publish_issue(
                            "https://gitlab.example.com/owner/repo",
                            "[view: BUILD] 테스트",
                            self.make_body(fingerprint),
                            fingerprint,
                            ["automation"],
                        )

        self.assertEqual(result["action"], "reopened")
        self.assertEqual(result["issue_id"], 9)
        self.assertEqual(update_mock.call_args.args[-2], ["automation"])
        self.assertEqual(update_mock.call_args.args[-1], "reopen")

    def test_title_is_trimmed_before_create(self):
        fingerprint = "pipeline:owner/repo:SAFE:E9"
        long_title = "[view: SAFE] " + ("a" * 80)

        with patch.object(MODULE, "load_auth", return_value=("token", "https://api.github.com")):
            with patch.object(MODULE, "github_ensure_labels"):
                with patch.object(MODULE, "find_existing_issue", return_value=None):
                    with patch.object(
                        MODULE,
                        "github_create",
                        return_value={"number": 11, "html_url": "https://github.com/owner/repo/issues/11"},
                    ) as create_mock:
                        result = MODULE.publish_issue(
                            "https://github.com/owner/repo",
                            long_title,
                            self.make_body(fingerprint),
                            fingerprint,
                            ["automation"],
                        )

        self.assertEqual(result["action"], "created")
        self.assertEqual(len(create_mock.call_args.args[3]), 50)

    def test_github_update_reapplies_labels(self):
        fingerprint = "pipeline:owner/repo:SAFE:E3"

        with patch.object(MODULE, "load_auth", return_value=("token", "https://api.github.com")):
            with patch.object(MODULE, "github_ensure_labels"):
                with patch.object(
                    MODULE,
                    "find_existing_issue",
                    return_value={"number": 5, "state": "open"},
                ):
                    with patch.object(
                        MODULE,
                        "github_update",
                        return_value={"number": 5, "html_url": "https://github.com/owner/repo/issues/5"},
                    ) as update_mock:
                        result = MODULE.publish_issue(
                            "https://github.com/owner/repo",
                            "[view: SAFE] 테스트",
                            self.make_body(fingerprint),
                            fingerprint,
                            ["automation"],
                        )

        self.assertEqual(result["action"], "updated")
        self.assertEqual(update_mock.call_args.args[-2], ["automation"])
        self.assertEqual(update_mock.call_args.args[-1], "open")


if __name__ == "__main__":
    unittest.main()
