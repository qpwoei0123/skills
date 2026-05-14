#!/usr/bin/env python3
"""Weekly cleanup runner for orbit-generated GitHub/GitLab issues."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

ORBIT_SCRIPTS = Path(__file__).resolve().parents[2] / "orbit" / "scripts"
if str(ORBIT_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(ORBIT_SCRIPTS))

import classify  # noqa: E402
import memory_bridge  # noqa: E402
import publish_issue as orbit_pub  # noqa: E402


MAX_CLOSE_PER_RUN = 10
KEEP_OPEN_LABELS = {"orbit:do-not-close", "orbit:keep", "pinned"}
CLEANUP_LABEL_COLOR = "cccccc"


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        return None


def label_names(issue: dict) -> set[str]:
    names: set[str] = set()
    for label in issue.get("labels") or []:
        if isinstance(label, str):
            names.add(label)
        else:
            name = label.get("name")
            if name:
                names.add(name)
    return names


def is_bot_comment(comment: dict) -> bool:
    user = comment.get("user") or comment.get("author") or {}
    if isinstance(user, str):
        login = user
        user_type = ""
    else:
        login = user.get("login") or user.get("username") or user.get("name") or ""
        user_type = user.get("type", "")
    return user_type.lower() == "bot" or login.endswith("[bot]")


def has_recent_human_comment(
    issue: dict,
    *,
    now: datetime,
    window_days: int = 14,
) -> bool:
    cutoff = now - timedelta(days=window_days)
    for comment in issue.get("comments") or []:
        if is_bot_comment(comment):
            continue
        created = parse_time(comment.get("created_at") or comment.get("updated_at"))
        if created and created >= cutoff:
            return True
    return False


def safety_holds(
    issue: dict,
    cleanup_log: dict,
    *,
    now: datetime,
) -> tuple[list[str], list[str]]:
    labels: list[str] = []
    reasons: list[str] = []

    if label_names(issue) & KEEP_OPEN_LABELS:
        labels.append("cleanup:held-do-not-close")
        reasons.append("protected label")

    if has_recent_human_comment(issue, now=now):
        labels.append("cleanup:held-recent-activity")
        reasons.append("recent human comment")

    if int(cleanup_log.get("auto_close_runs", 0)) < 3:
        labels.append("cleanup:held-trust-ramp")
        reasons.append("auto_close_runs")

    return labels, reasons


def render_comment(classification: classify.Classification, close: bool) -> str:
    issue = classification.issue
    number = classify.issue_number(issue)
    reasons = "; ".join(classification.reasons) or "cleanup rule matched"

    if classification.category == "DUP":
        canonical = classify.issue_number(classification.canonical_issue or {})
        target = f"#{canonical}" if canonical else classification.canonical_fingerprint
        return "\n".join(
            [
                "orbit-cleanup: duplicate issue detected.",
                f"- issue: #{number}",
                f"- canonical: {target}",
                f"- confidence: {classification.confidence}",
                f"- reason: {reasons}",
                f"- action: {'label/comment/close' if close else 'label/comment only'}",
            ]
        )

    if classification.category == "BATCH":
        related = ", ".join(f"#{classify.issue_number(item)}" for item in classification.related_issues)
        files = ", ".join(sorted(classification.evidence_files)) or "(none)"
        return "\n".join(
            [
                "orbit-cleanup: related issues can likely be handled as one batch.",
                f"- module: {classification.batch_module}",
                f"- related: {related}",
                f"- shared files: {files}",
                f"- confidence: {classification.confidence}",
            ]
        )

    return "\n".join(
        [
            "orbit-cleanup: this issue appears to be resolved by current repository state.",
            f"- issue: #{number}",
            f"- confidence: {classification.confidence}",
            f"- reason: {reasons}",
            f"- action: {'label/comment/close' if close else 'label/comment only'}",
        ]
    )


def action_from_classification(
    classification: classify.Classification,
    *,
    cleanup_log: dict,
    now: datetime,
    close_slots_remaining: int,
) -> dict:
    labels = list(classification.labels)
    hold_labels: list[str] = []
    hold_reasons: list[str] = []

    close = classification.close_allowed_by_classification and close_slots_remaining > 0
    if close:
        hold_labels, hold_reasons = safety_holds(classification.issue, cleanup_log, now=now)
        labels.extend(hold_labels)
        if hold_reasons:
            close = False
    elif classification.close_allowed_by_classification and close_slots_remaining <= 0:
        labels.append("cleanup:held-close-limit")
        hold_reasons.append("max close per run reached")

    action = {
        "issue_number": classify.issue_number(classification.issue),
        "fingerprint": classification.fingerprint,
        "view": classification.view,
        "category": classification.category,
        "confidence": classification.confidence,
        "labels": sorted(set(labels)),
        "comment": render_comment(classification, close),
        "close": close,
        "hold_reasons": hold_reasons,
        "reasons": classification.reasons,
        "canonical_fingerprint": classification.canonical_fingerprint,
        "batch_module": classification.batch_module,
    }
    if classification.canonical_issue:
        action["canonical_issue_number"] = classify.issue_number(classification.canonical_issue)
    return action


def build_cleanup_plan(
    issues: list[dict],
    *,
    repo_url: str,
    cleanup_log: dict | None = None,
    repo_path: Path | str | None = None,
    merged_issue_numbers: set[int] | None = None,
    now: datetime | None = None,
) -> dict:
    """Build a JSON-serializable cleanup plan without mutating remote issues."""
    del repo_url
    cleanup_log = cleanup_log or {}
    now = now or datetime.now(timezone.utc)
    classifications = classify.classify_issues(
        issues,
        repo_path=repo_path,
        merged_issue_numbers=merged_issue_numbers,
    )

    actions: list[dict] = []
    close_slots_remaining = MAX_CLOSE_PER_RUN
    for classification in classifications:
        action = action_from_classification(
            classification,
            cleanup_log=cleanup_log,
            now=now,
            close_slots_remaining=close_slots_remaining,
        )
        if action["close"]:
            close_slots_remaining -= 1
        actions.append(action)

    summary = summarize_actions(len(issues), actions)
    return {"summary": summary, "actions": actions}


def summarize_actions(scanned: int, actions: list[dict]) -> dict:
    return {
        "scanned": scanned,
        "dup": sum(1 for action in actions if action["category"] == "DUP"),
        "batch": sum(1 for action in actions if action["category"] == "BATCH"),
        "resolved": sum(1 for action in actions if action["category"] == "RESOLVED"),
        "closed": sum(1 for action in actions if action["close"]),
        "label_only": sum(1 for action in actions if not action["close"]),
        "errors": 0,
    }


def fetch_orbit_issues(repo_url: str) -> tuple[str, str, str, list[dict]]:
    """Fetch all GitHub/GitLab issues that carry a current orbit fingerprint footer."""
    platform, base_url, project = orbit_pub.detect_platform(repo_url)
    token, api_base = orbit_pub.load_auth(platform, base_url)
    if not token:
        raise orbit_pub.PublishFallback("인증 토큰이 없어 cleanup 대상 이슈를 조회할 수 없습니다.")

    iterator = (
        orbit_pub.iter_github_issues(api_base, project, token)
        if platform == "github"
        else orbit_pub.iter_gitlab_issues(api_base, project, token)
    )
    issues = [
        issue
        for issue in iterator
        if classify.parse_fingerprint(issue.get("body") or issue.get("description") or "")
    ]
    return platform, api_base, project, issues


def ensure_cleanup_labels(platform: str, api_base: str, project: str, token: str, labels: list[str]) -> None:
    cleanup_labels = [label for label in labels if label.startswith("cleanup:")]
    if not cleanup_labels:
        return

    if platform == "github":
        url = f"{api_base}/repos/{project}/labels?per_page=100"
        existing, _ = orbit_pub.api_request("GET", url, "github", token)
        existing_names = {item["name"] for item in existing}
        for label in cleanup_labels:
            if label not in existing_names:
                orbit_pub.api_request(
                    "POST",
                    f"{api_base}/repos/{project}/labels",
                    "github",
                    token,
                    {"name": label, "color": CLEANUP_LABEL_COLOR},
                )
        return

    encoded = urllib.parse.quote(project, safe="")
    url = f"{api_base}/api/v4/projects/{encoded}/labels?per_page=100"
    existing, _ = orbit_pub.api_request("GET", url, "gitlab", token)
    existing_names = {item["name"] for item in existing}
    for label in cleanup_labels:
        if label not in existing_names:
            orbit_pub.api_request(
                "POST",
                f"{api_base}/api/v4/projects/{encoded}/labels",
                "gitlab",
                token,
                {"name": label, "color": f"#{CLEANUP_LABEL_COLOR}"},
            )


def apply_remote_action(
    action: dict,
    issue: dict,
    *,
    platform: str,
    api_base: str,
    project: str,
    token: str,
) -> None:
    labels = sorted(label_names(issue) | set(action["labels"]))
    ensure_cleanup_labels(platform, api_base, project, token, labels)

    if platform == "github":
        number = action["issue_number"]
        orbit_pub.api_request(
            "POST",
            f"{api_base}/repos/{project}/issues/{number}/comments",
            "github",
            token,
            {"body": action["comment"]},
        )
        payload = {"labels": labels}
        if action["close"]:
            payload["state"] = "closed"
        orbit_pub.api_request(
            "PATCH",
            f"{api_base}/repos/{project}/issues/{number}",
            "github",
            token,
            payload,
        )
        return

    iid = action["issue_number"]
    encoded = urllib.parse.quote(project, safe="")
    orbit_pub.api_request(
        "POST",
        f"{api_base}/api/v4/projects/{encoded}/issues/{iid}/notes",
        "gitlab",
        token,
        {"body": action["comment"]},
    )
    payload = {"labels": ",".join(labels)}
    if action["close"]:
        payload["state_event"] = "close"
    orbit_pub.api_request(
        "PUT",
        f"{api_base}/api/v4/projects/{encoded}/issues/{iid}",
        "gitlab",
        token,
        payload,
    )


def run_cleanup(
    repo_url: str,
    *,
    repo_path: Path | str | None = None,
    issues: list[dict] | None = None,
    dry_run: bool = False,
    cleanup_home: Path | None = None,
) -> dict:
    platform, api_base, project = orbit_pub.detect_platform(repo_url)
    token = None
    if issues is None:
        platform, api_base, project, issues = fetch_orbit_issues(repo_url)
        token, _ = orbit_pub.load_auth(platform, api_base)

    cleanup_log = memory_bridge.load_cleanup_log(project, cleanup_home)
    plan = build_cleanup_plan(
        issues,
        repo_url=repo_url,
        cleanup_log=cleanup_log,
        repo_path=repo_path,
    )

    errors = 0
    applied_actions: list[dict] = []
    if not dry_run:
        if token is None:
            token, api_base = orbit_pub.load_auth(platform, api_base)
        if not token:
            raise orbit_pub.PublishFallback("인증 토큰이 없어 cleanup action을 적용할 수 없습니다.")
        issues_by_number = {classify.issue_number(issue): issue for issue in issues}
        for action in plan["actions"]:
            try:
                apply_remote_action(
                    action,
                    issues_by_number[action["issue_number"]],
                    platform=platform,
                    api_base=api_base,
                    project=project,
                    token=token,
                )
                applied_actions.append(action)
            except orbit_pub.PublishFallback:
                errors += 1
                action["error"] = "remote mutation failed"

        plan["summary"] = summarize_actions(len(issues), applied_actions)
        plan["summary"]["errors"] = errors
        memory_bridge.update_view_memories(project, applied_actions, cleanup_home)
        memory_bridge.record_cleanup_history(project, plan["summary"], base=cleanup_home)

    plan["platform"] = platform
    plan["project"] = project
    plan["dry_run"] = dry_run
    return plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="orbit cleanup issue curator")
    parser.add_argument("--repo-url", required=True, help="GitHub/GitLab repository URL")
    parser.add_argument("--repo-path", help="Local checkout used for resolved evidence checks")
    parser.add_argument("--issues-file", help="JSON array of issues for dry-run/offline testing")
    parser.add_argument("--dry-run", action="store_true", help="Build plan without remote mutation")
    return parser.parse_args()


def load_issues_file(path: str | None) -> list[dict] | None:
    if not path:
        return None
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise SystemExit("--issues-file must contain a JSON array")
    return payload


def main() -> None:
    args = parse_args()
    result = run_cleanup(
        args.repo_url,
        repo_path=args.repo_path,
        issues=load_issues_file(args.issues_file),
        dry_run=args.dry_run,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
