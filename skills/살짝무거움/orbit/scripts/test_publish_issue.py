import importlib.util
import io
import json
import unittest
from contextlib import redirect_stdout
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
            "format_version: orbit/v2.1",
            f"<!-- orbit-fingerprint: {fingerprint} -->",
        ])

    def test_api_request_serializes_gitlab_auth_and_json_payload(self):
        class FakeResponse:
            headers = {"X-Next-Page": ""}

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self):
                return b'{"iid": 7}'

        with patch.object(
            MODULE.urllib.request,
            "urlopen",
            return_value=FakeResponse(),
        ) as urlopen:
            payload, headers = MODULE.api_request(
                "POST",
                "https://gitlab.example.com/api/v4/projects/owner%2Frepo/issues",
                "gitlab",
                "test-token",
                {"title": "test"},
            )

        request = urlopen.call_args.args[0]
        request_headers = {key.lower(): value for key, value in request.header_items()}
        self.assertEqual(request.method, "POST")
        self.assertEqual(request_headers["private-token"], "test-token")
        self.assertEqual(json.loads(request.data), {"title": "test"})
        self.assertEqual(payload, {"iid": 7})
        self.assertEqual(headers, {"X-Next-Page": ""})

    def test_fingerprint_candidates_keeps_current_then_unique_legacy_aliases(self):
        self.assertEqual(
            MODULE.fingerprint_candidates(
                " pipeline:owner/repo:BUILD:f-12345678 ",
                [
                    "pipeline:owner/repo:BUILD:E1",
                    "pipeline:owner/repo:BUILD:E1",
                    "",
                    " pipeline:owner/repo:BUILD:f-12345678 ",
                ],
            ),
            [
                "pipeline:owner/repo:BUILD:f-12345678",
                "pipeline:owner/repo:BUILD:E1",
            ],
        )

    def test_missing_token_returns_manual_payload(self):
        fingerprint = "pipeline:owner/repo:SAFE:f-11111111"
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
        self.assertIn(f"<!-- orbit-fingerprint: {fingerprint} -->", result["copy_paste_text"])

    def test_github_pagination_finds_issue_on_second_page(self):
        responses = [
            (
                [{
                    "number": 1,
                    "body": "\n".join([
                        "본문",
                        "",
                        "format_version: orbit/v2.1",
                        "<!-- orbit-fingerprint: pipeline:owner/repo:SAFE:f-00000000 -->",
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
                        "format_version: orbit/v2.1",
                        "<!-- orbit-fingerprint: pipeline:owner/repo:SAFE:f-11111111 -->",
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
                "pipeline:owner/repo:SAFE:f-11111111",
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
                        "format_version: orbit/v2.1",
                        "<!-- orbit-fingerprint: pipeline:owner/repo:SAFE:f-11111110 -->",
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
                        "format_version: orbit/v2.1",
                        "<!-- orbit-fingerprint: pipeline:owner/repo:SAFE:f-11111111 -->",
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
                "pipeline:owner/repo:SAFE:f-11111111",
            )

        self.assertEqual(issue["number"], 2)
        self.assertEqual(len(responses), 0)

    def test_find_existing_issue_accepts_legacy_footer_for_migration(self):
        fingerprint = "pipeline:owner/repo:SAFE:f-12121212"
        responses = [
            (
                [{
                    "number": 3,
                    "body": "\n".join([
                        "본문",
                        "",
                        "`format_version: orbit/v2.1` · "
                        f"`fingerprint: {fingerprint}`",
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
                fingerprint,
            )

        self.assertEqual(issue["number"], 3)
        self.assertEqual(len(responses), 0)

    def test_find_existing_issue_accepts_legacy_two_line_footer_for_migration(self):
        fingerprint = "pipeline:owner/repo:SAFE:f-34343434"
        body = "\n".join([
            "본문",
            "",
            "format_version: orbit/v2",
            f"fingerprint: {fingerprint}",
        ])

        self.assertTrue(MODULE.has_matching_fingerprint(body, fingerprint))

    def test_legacy_fingerprint_mention_in_body_text_does_not_match(self):
        fingerprint = "pipeline:owner/repo:BUILD:E1"
        body = "\n".join([
            "본문",
            "",
            f"duplicate of fingerprint: {fingerprint}",
            "관련 이슈 설명일 뿐 orbit footer가 아니다.",
        ])

        self.assertFalse(MODULE.has_matching_fingerprint(body, fingerprint))

    def test_find_existing_issue_accepts_legacy_alias_for_id_migration(self):
        new_fingerprint = "pipeline:owner/repo:BUILD:f-12345678"
        legacy_fingerprint = "pipeline:owner/repo:BUILD:E1"
        responses = [
            (
                [{
                    "number": 4,
                    "body": "\n".join([
                        "본문",
                        "",
                        "`format_version: orbit/v2.1` · "
                        f"`fingerprint: {legacy_fingerprint}`",
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
                new_fingerprint,
                legacy_fingerprints=[legacy_fingerprint],
            )

        self.assertEqual(issue["number"], 4)
        self.assertEqual(len(responses), 0)

    def test_issue_contract_rejects_legacy_footer_for_new_body(self):
        fingerprint = "pipeline:owner/repo:SAFE:f-56565656"
        body = "\n".join([
            "본문",
            "",
            "format_version: orbit/v2.1",
            f"fingerprint: {fingerprint}",
        ])

        result = MODULE.publish_issue(
            "https://github.com/owner/repo",
            "[view: SAFE] 테스트",
            body,
            fingerprint,
            ["automation"],
        )

        self.assertEqual(result["action"], "manual_required")
        self.assertIn("HTML comment fingerprint", result["reason"])

    def test_issue_contract_rejects_legacy_finding_id_in_current_footer(self):
        fingerprint = "pipeline:owner/repo:SAFE:E1"

        result = MODULE.publish_issue(
            "https://github.com/owner/repo",
            "[view: SAFE] 테스트",
            self.make_body(fingerprint),
            fingerprint,
            ["automation"],
        )

        self.assertEqual(result["action"], "manual_required")
        self.assertIn("fingerprint 형식", result["reason"])

    def test_invalid_contract_returns_manual_payload(self):
        result = MODULE.publish_issue(
            "https://github.com/owner/repo",
            "[view: SAFE] 테스트",
            "본문만 있음",
            "pipeline:owner/repo:SAFE:f-22222222",
            ["automation"],
        )

        self.assertEqual(result["action"], "manual_required")
        self.assertIn("format_version", result["reason"])

    def test_invalid_contract_manual_payload_contains_discoverable_footer(self):
        fingerprint = "pipeline:owner/repo:SAFE:f-22222222"
        expected_footer = f"<!-- orbit-fingerprint: {fingerprint} -->"

        result = MODULE.publish_issue(
            "https://github.com/owner/repo",
            "[view: SAFE] 테스트",
            "본문만 있음",
            fingerprint,
            ["automation"],
        )

        self.assertEqual(result["action"], "manual_required")
        self.assertIn(expected_footer, result["copy_paste_text"])
        self.assertTrue(
            MODULE.has_matching_fingerprint(result["copy_paste_text"], fingerprint)
        )

    def test_dry_run_copy_text_contains_discoverable_footer(self):
        fingerprint = "pipeline:owner/repo:BUILD:f-12345678"
        expected_footer = f"<!-- orbit-fingerprint: {fingerprint} -->"
        output = io.StringIO()

        with patch(
            "sys.argv",
            [
                "publish_issue.py",
                "--repo-url",
                "https://github.com/owner/repo",
                "--title",
                "[view: BUILD] 테스트",
                "--body",
                "본문만 있음",
                "--fingerprint",
                fingerprint,
                "--dry-run",
            ],
        ):
            with redirect_stdout(output):
                MODULE.main()

        result = json.loads(output.getvalue())
        self.assertEqual(result["action"], "dry_run")
        self.assertIn(expected_footer, result["copy_paste_text"])
        self.assertTrue(
            MODULE.has_matching_fingerprint(result["copy_paste_text"], fingerprint)
        )

    def test_legacy_footer_only_matches_same_fingerprint_value(self):
        legacy_fingerprint = "pipeline:owner/repo:BUILD:E1"
        new_fingerprint = "pipeline:owner/repo:BUILD:f-12345678"
        body = "\n".join([
            "본문",
            "",
            "`format_version: orbit/v2.1` · "
            f"`fingerprint: {legacy_fingerprint}`",
        ])

        self.assertTrue(MODULE.has_matching_fingerprint(body, legacy_fingerprint))
        self.assertFalse(MODULE.has_matching_fingerprint(body, new_fingerprint))

    def test_legacy_alias_does_not_match_other_view_issue(self):
        new_fingerprint = "pipeline:owner/repo:BUILD:f-12345678"
        other_view_fingerprint = "pipeline:owner/repo:DEP:E1"
        body = "\n".join([
            "본문",
            "",
            "`format_version: orbit/v2.1` · "
            f"`fingerprint: {other_view_fingerprint}`",
        ])

        self.assertFalse(
            MODULE.has_matching_fingerprint(
                body,
                new_fingerprint,
                legacy_fingerprints=[other_view_fingerprint],
            )
        )

    def test_publish_issue_rejects_cross_view_legacy_alias(self):
        new_fingerprint = "pipeline:owner/repo:BUILD:f-12345678"
        other_view_fingerprint = "pipeline:owner/repo:DEP:E1"

        with patch.object(MODULE, "load_auth", side_effect=AssertionError("should not load auth")):
            result = MODULE.publish_issue(
                "https://github.com/owner/repo",
                "[view: BUILD] 테스트",
                self.make_body(new_fingerprint),
                new_fingerprint,
                ["automation"],
                legacy_fingerprints=[other_view_fingerprint],
            )

        self.assertEqual(result["action"], "manual_required")
        self.assertIn("같은 repo/view", result["reason"])

    def test_publish_issue_updates_legacy_alias_with_current_fingerprint_body(self):
        new_fingerprint = "pipeline:owner/repo:BUILD:f-12345678"
        legacy_fingerprint = "pipeline:owner/repo:BUILD:E1"
        body = self.make_body(new_fingerprint)
        responses = [
            ([{"name": "automation"}], {}),
            (
                [{
                    "number": 8,
                    "state": "open",
                    "body": "\n".join([
                        "본문",
                        "",
                        "`format_version: orbit/v2.1` · "
                        f"`fingerprint: {legacy_fingerprint}`",
                    ]),
                    "html_url": "https://github.com/owner/repo/issues/8",
                }],
                {"Link": ""},
            ),
            ({"number": 8, "html_url": "https://github.com/owner/repo/issues/8"}, {}),
        ]
        update_payloads = []

        def fake_api_request(method, url, platform, token, data=None):
            if method == "PATCH":
                update_payloads.append(data)
            return responses.pop(0)

        with patch.object(MODULE, "load_auth", return_value=("token", "https://api.github.com")):
            with patch.object(MODULE, "api_request", side_effect=fake_api_request):
                result = MODULE.publish_issue(
                    "https://github.com/owner/repo",
                    "[view: BUILD] 테스트",
                    body,
                    new_fingerprint,
                    ["automation"],
                    legacy_fingerprints=[legacy_fingerprint],
                )

        self.assertEqual(result["action"], "updated")
        self.assertEqual(update_payloads[0]["body"], body)
        self.assertIn(f"<!-- orbit-fingerprint: {new_fingerprint} -->", update_payloads[0]["body"])
        self.assertNotIn(f"fingerprint: {legacy_fingerprint}", update_payloads[0]["body"])
        self.assertEqual(len(responses), 0)

    def test_gitlab_closed_issue_returns_skipped_closed(self):
        """닫힌 이슈는 사람이 의도적으로 닫은 것이므로 재오픈하지 않는다."""
        fingerprint = "pipeline:owner/repo:BUILD:f-33333333"
        with patch.object(MODULE, "load_auth", return_value=("token", "https://gitlab.example.com")):
            with patch.object(MODULE, "gitlab_ensure_labels"):
                with patch.object(
                    MODULE,
                    "find_existing_issue",
                    return_value={"iid": 9, "state": "closed", "web_url": "https://gitlab.example.com/owner/repo/-/issues/9"},
                ):
                    result = MODULE.publish_issue(
                        "https://gitlab.example.com/owner/repo",
                        "[view: BUILD] 테스트",
                        self.make_body(fingerprint),
                        fingerprint,
                        ["automation"],
                    )

        self.assertEqual(result["action"], "skipped_closed")
        self.assertEqual(result["issue_id"], 9)

    def test_closed_issue_lookup_uses_fixture_body_without_find_existing_mock(self):
        fingerprint = "pipeline:owner/repo:SAFE:f-44444444"
        responses = [
            ([{"name": "automation"}], {}),
            (
                [{
                    "number": 12,
                    "state": "closed",
                    "body": self.make_body(fingerprint),
                    "html_url": "https://github.com/owner/repo/issues/12",
                }],
                {"Link": ""},
            ),
        ]
        seen_urls = []

        def fake_api_request(method, url, platform, token, data=None):
            seen_urls.append(url)
            return responses.pop(0)

        with patch.object(MODULE, "load_auth", return_value=("token", "https://api.github.com")):
            with patch.object(MODULE, "api_request", side_effect=fake_api_request):
                result = MODULE.publish_issue(
                    "https://github.com/owner/repo",
                    "[view: SAFE] 테스트",
                    self.make_body(fingerprint),
                    fingerprint,
                    ["automation"],
                )

        self.assertEqual(result["action"], "skipped_closed")
        self.assertEqual(result["issue_id"], 12)
        self.assertTrue(any("state=all" in url for url in seen_urls))
        self.assertEqual(len(responses), 0)

    def test_title_is_trimmed_before_create(self):
        fingerprint = "pipeline:owner/repo:SAFE:f-99999999"
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
        fingerprint = "pipeline:owner/repo:SAFE:f-33333333"
        responses = [
            ([{"name": "automation"}], {}),
            ([{
                "number": 5,
                "state": "open",
                "body": self.make_body(fingerprint),
            }], {"Link": ""}),
            ({"number": 5, "html_url": "https://github.com/owner/repo/issues/5"}, {}),
        ]
        requests = []

        def fake_api_request(method, url, platform, token, data=None):
            requests.append((method, url, platform, token, data))
            return responses.pop(0)

        with patch.object(MODULE, "load_auth", return_value=("token", "https://api.github.com")):
            with patch.object(MODULE, "api_request", side_effect=fake_api_request):
                result = MODULE.publish_issue(
                    "https://github.com/owner/repo",
                    "[view: SAFE] 테스트",
                    self.make_body(fingerprint),
                    fingerprint,
                    ["automation"],
                )

        self.assertEqual(result["action"], "updated")
        patch_request = next(request for request in requests if request[0] == "PATCH")
        self.assertEqual(
            patch_request[-1],
            {
                "title": "[view: SAFE] 테스트",
                "body": self.make_body(fingerprint),
                "labels": ["automation"],
            },
        )
        self.assertEqual(len(responses), 0)

    def test_gitlab_create_encodes_project_and_payload(self):
        with patch.object(
            MODULE,
            "api_request",
            return_value=({"iid": 7, "web_url": "https://gitlab.example.com/issues/7"}, {}),
        ) as api_request:
            result = MODULE.gitlab_create(
                "https://gitlab.example.com",
                "owner/repo",
                "token",
                "title",
                "body",
                ["automation", "orbit"],
            )

        api_request.assert_called_once_with(
            "POST",
            "https://gitlab.example.com/api/v4/projects/owner%2Frepo/issues",
            "gitlab",
            "token",
            {
                "title": "title",
                "description": "body",
                "labels": "automation,orbit",
            },
        )
        self.assertEqual(result["iid"], 7)

    def test_gitlab_update_omits_state_event_when_none(self):
        with patch.object(
            MODULE,
            "api_request",
            return_value=({"iid": 7, "web_url": "https://gitlab.example.com/issues/7"}, {}),
        ) as api_request:
            MODULE.gitlab_update(
                "https://gitlab.example.com",
                "owner/repo",
                "token",
                7,
                "title",
                "body",
                ["automation"],
                None,
            )

        method, url, platform, token, data = api_request.call_args.args
        self.assertEqual(method, "PUT")
        self.assertEqual(
            url,
            "https://gitlab.example.com/api/v4/projects/owner%2Frepo/issues/7",
        )
        self.assertEqual(platform, "gitlab")
        self.assertEqual(token, "token")
        self.assertEqual(
            data,
            {"title": "title", "description": "body", "labels": "automation"},
        )


if __name__ == "__main__":
    unittest.main()
