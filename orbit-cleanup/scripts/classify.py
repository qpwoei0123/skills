#!/usr/bin/env python3
"""Classify noisy orbit issues into duplicate, batch, and resolved cleanup actions."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ORBIT_SCRIPTS = Path(__file__).resolve().parents[2] / "orbit" / "scripts"
if str(ORBIT_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(ORBIT_SCRIPTS))

import publish_issue as orbit_pub  # noqa: E402


FINGERPRINT_RE = re.compile(r"<!--\s*orbit-fingerprint:\s*([^>]+?)\s*-->")
EVIDENCE_RE = re.compile(
    r"(?<!https:)(?<!http:)(?P<path>(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+):(?P<line>\d+)"
)
TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class FingerprintInfo:
    fingerprint: str
    repo_scope: str
    view: str
    finding_id: str


@dataclass
class Classification:
    issue: dict
    fingerprint: str
    view: str
    category: str
    confidence: str
    labels: list[str]
    close_allowed_by_classification: bool
    reasons: list[str] = field(default_factory=list)
    canonical_issue: dict | None = None
    canonical_fingerprint: str | None = None
    batch_module: str | None = None
    related_issues: list[dict] = field(default_factory=list)
    evidence_files: set[str] = field(default_factory=set)


@dataclass
class IssueContext:
    issue: dict
    parsed: FingerprintInfo
    created_at: datetime
    evidence_points: set[str]
    evidence_files: set[str]
    title_tokens: set[str]


def parse_fingerprint(body: str | None) -> FingerprintInfo | None:
    """Extract the current orbit HTML fingerprint footer from issue body text."""
    if not body:
        return None

    match = FINGERPRINT_RE.search(body)
    if not match:
        return None

    fingerprint = match.group(1).strip()
    scope = orbit_pub.fingerprint_scope(fingerprint)
    if scope is None:
        return None

    finding_id = fingerprint.rsplit(":", 1)[-1]
    return FingerprintInfo(
        fingerprint=fingerprint,
        repo_scope=scope[0],
        view=scope[1],
        finding_id=finding_id,
    )


def extract_evidence_points(body: str | None) -> set[str]:
    """Return normalized file:line evidence references from an orbit issue body."""
    points: set[str] = set()
    if not body:
        return points

    for match in EVIDENCE_RE.finditer(body):
        path = match.group("path").strip("`.,)")
        line = match.group("line")
        points.add(f"{path}:{line}")
    return points


def evidence_files(points: Iterable[str]) -> set[str]:
    return {point.rsplit(":", 1)[0] for point in points if ":" in point}


def module_prefix(path: str) -> str:
    parts = [part for part in path.split("/") if part]
    if len(parts) >= 2:
        return "/".join(parts[:2])
    if parts:
        return parts[0]
    return "root"


def issue_number(issue: dict) -> int:
    value = issue.get("number", issue.get("iid", 0))
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def issue_body(issue: dict) -> str:
    return issue.get("body") or issue.get("description") or ""


def issue_created_at(issue: dict) -> datetime:
    raw = issue.get("created_at") or issue.get("updated_at") or ""
    if isinstance(raw, datetime):
        return raw
    if isinstance(raw, str) and raw:
        value = raw.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(value)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed
        except ValueError:
            pass
    return datetime.min.replace(tzinfo=timezone.utc)


def normalize_title_tokens(title: str) -> set[str]:
    title = re.sub(r"^\[view:\s*[A-Z]+\]\s*", "", title.strip(), flags=re.IGNORECASE)
    return set(TOKEN_RE.findall(title.lower()))


def jaccard(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def has_label(issue: dict, names: set[str]) -> bool:
    for label in issue.get("labels") or []:
        if isinstance(label, str):
            name = label
        else:
            name = label.get("name", "")
        if name in names:
            return True
    return False


def build_contexts(issues: Iterable[dict]) -> list[IssueContext]:
    contexts: list[IssueContext] = []
    for issue in issues:
        parsed = parse_fingerprint(issue_body(issue))
        if parsed is None:
            continue
        points = extract_evidence_points(issue_body(issue))
        contexts.append(
            IssueContext(
                issue=issue,
                parsed=parsed,
                created_at=issue_created_at(issue),
                evidence_points=points,
                evidence_files=evidence_files(points),
                title_tokens=normalize_title_tokens(issue.get("title", "")),
            )
        )
    return contexts


def classify_issues(
    issues: Iterable[dict],
    *,
    known_findings: dict | None = None,
    repo_path: Path | str | None = None,
    merged_issue_numbers: set[int] | None = None,
) -> list[Classification]:
    """Return cleanup classifications for orbit issues with current fingerprint footers."""
    contexts = build_contexts(issues)
    known_findings = known_findings or {}
    merged_issue_numbers = merged_issue_numbers or set()
    classifications: list[Classification] = []
    classified_keys: set[tuple[int, str]] = set()
    terminal_issue_numbers: set[int] = set()

    def add(classification: Classification) -> None:
        number = issue_number(classification.issue)
        key = (number, classification.category)
        if key in classified_keys:
            return
        if classification.category in {"DUP", "RESOLVED"}:
            if number in terminal_issue_numbers:
                return
            terminal_issue_numbers.add(number)
        classifications.append(classification)
        classified_keys.add(key)

    classify_duplicate_fingerprints(contexts, add)
    classify_duplicate_aliases(contexts, known_findings, add)
    classify_duplicate_evidence(contexts, add)
    classify_resolved(contexts, repo_path, merged_issue_numbers, add)
    classify_batch(contexts, terminal_issue_numbers, add)

    return classifications


def classify_duplicate_fingerprints(contexts: list[IssueContext], add) -> None:
    by_fingerprint: dict[str, list[IssueContext]] = {}
    for context in contexts:
        by_fingerprint.setdefault(context.parsed.fingerprint, []).append(context)

    for fingerprint, group in by_fingerprint.items():
        if len(group) < 2:
            continue
        ordered = sorted(group, key=lambda item: (item.created_at, issue_number(item.issue)))
        canonical = ordered[0]
        for duplicate in ordered[1:]:
            add(
                Classification(
                    issue=duplicate.issue,
                    fingerprint=fingerprint,
                    view=duplicate.parsed.view,
                    category="DUP",
                    confidence="high",
                    labels=["cleanup:duplicate"],
                    close_allowed_by_classification=True,
                    reasons=[
                        f"same fingerprint as canonical issue #{issue_number(canonical.issue)}"
                    ],
                    canonical_issue=canonical.issue,
                    canonical_fingerprint=canonical.parsed.fingerprint,
                    evidence_files=duplicate.evidence_files,
                )
            )


def classify_duplicate_aliases(
    contexts: list[IssueContext],
    known_findings: dict,
    add,
) -> None:
    context_by_fingerprint = {context.parsed.fingerprint: context for context in contexts}
    for context in contexts:
        entry = known_findings.get(context.parsed.fingerprint)
        if not isinstance(entry, dict):
            continue
        alias_of = entry.get("alias_of")
        if not alias_of:
            continue
        canonical = context_by_fingerprint.get(alias_of)
        add(
            Classification(
                issue=context.issue,
                fingerprint=context.parsed.fingerprint,
                view=context.parsed.view,
                category="DUP",
                confidence="high",
                labels=["cleanup:duplicate"],
                close_allowed_by_classification=True,
                reasons=[f"known_findings marks this fingerprint as alias_of {alias_of}"],
                canonical_issue=canonical.issue if canonical else None,
                canonical_fingerprint=alias_of,
                evidence_files=context.evidence_files,
            )
        )


def classify_duplicate_evidence(contexts: list[IssueContext], add) -> None:
    ordered = sorted(contexts, key=lambda item: (item.created_at, issue_number(item.issue)))
    for index, left in enumerate(ordered):
        for right in ordered[index + 1 :]:
            if left.parsed.view != right.parsed.view:
                continue
            if not (left.evidence_points & right.evidence_points):
                continue
            if jaccard(left.title_tokens, right.title_tokens) < 0.85:
                continue
            add(
                Classification(
                    issue=right.issue,
                    fingerprint=right.parsed.fingerprint,
                    view=right.parsed.view,
                    category="DUP",
                    confidence="high",
                    labels=["cleanup:duplicate"],
                    close_allowed_by_classification=True,
                    reasons=[
                        f"same evidence and near-identical title as issue #{issue_number(left.issue)}"
                    ],
                    canonical_issue=left.issue,
                    canonical_fingerprint=left.parsed.fingerprint,
                    evidence_files=right.evidence_files,
                )
            )


def classify_resolved(
    contexts: list[IssueContext],
    repo_path: Path | str | None,
    merged_issue_numbers: set[int],
    add,
) -> None:
    repo = Path(repo_path) if repo_path else None
    for context in contexts:
        missing_evidence = False
        if repo is not None and context.evidence_files:
            missing_evidence = any(not (repo / path).exists() for path in context.evidence_files)

        merged_pr_reference = issue_number(context.issue) in merged_issue_numbers
        if not missing_evidence and not merged_pr_reference:
            continue

        confidence = "high" if missing_evidence and merged_pr_reference else "medium"
        labels = ["cleanup:auto-resolved"] if confidence == "high" else ["cleanup:likely-resolved"]
        add(
            Classification(
                issue=context.issue,
                fingerprint=context.parsed.fingerprint,
                view=context.parsed.view,
                category="RESOLVED",
                confidence=confidence,
                labels=labels,
                close_allowed_by_classification=confidence == "high",
                reasons=[
                    reason
                    for reason, enabled in (
                        ("evidence file is absent in current HEAD", missing_evidence),
                        ("merged PR references this issue", merged_pr_reference),
                    )
                    if enabled
                ],
                evidence_files=context.evidence_files,
            )
        )


def classify_batch(contexts: list[IssueContext], terminal_issue_numbers: set[int], add) -> None:
    by_view_file: dict[tuple[str, str], list[IssueContext]] = {}
    for context in contexts:
        if issue_number(context.issue) in terminal_issue_numbers:
            continue
        for path in context.evidence_files:
            by_view_file.setdefault((context.parsed.view, path), []).append(context)

    seen_issue_numbers: set[int] = set()
    for (_view, path), group in by_view_file.items():
        if len(group) < 2:
            continue
        ordered = sorted(group, key=lambda item: (item.created_at, issue_number(item.issue)))
        if (ordered[-1].created_at - ordered[0].created_at).days > 14:
            continue

        shared = set.intersection(*(context.evidence_files for context in ordered))
        shared_count = len(shared)
        confidence = "high" if shared_count >= 3 else "medium" if shared_count >= 2 else "low"
        module = module_prefix(path)
        related = [context.issue for context in ordered]

        for context in ordered:
            number = issue_number(context.issue)
            if number in seen_issue_numbers:
                continue
            seen_issue_numbers.add(number)
            add(
                Classification(
                    issue=context.issue,
                    fingerprint=context.parsed.fingerprint,
                    view=context.parsed.view,
                    category="BATCH",
                    confidence=confidence,
                    labels=[f"cleanup:batch:{module}"],
                    close_allowed_by_classification=False,
                    reasons=[f"shares evidence file {path} with {len(ordered) - 1} issue(s)"],
                    batch_module=module,
                    related_issues=related,
                    evidence_files=context.evidence_files,
                )
            )
