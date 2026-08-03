"""orbit Step 1, 4, 5의 순수 계약 로직."""

from __future__ import annotations

import hashlib
import re


WEEKDAY_VIEW = {
    0: "SAFE",
    1: "ARCH",
    2: "DEP",
    3: "BUILD",
    4: "DATA",
    5: "OPS",
    6: "DOC",
}

_CURRENT_FINGERPRINT_RE = re.compile(r"^pipeline:[^:]+:[A-Z]+:f-[0-9a-f]{8}$")
_WHITESPACE_RE = re.compile(r"\s+")


def resolve_view(weekday: int, override: str | None = None) -> str:
    if override:
        return override.upper()
    return WEEKDAY_VIEW[weekday]


def compute_actionability(next_step: str) -> int:
    score = 0
    if re.search(r"\S+/\S+\.\w+|:\d+", next_step):
        score += 2
    if re.search(r"`[^`]+`|\b[A-Z_]{2,}\b", next_step):
        score += 1
    if re.search(r"\bnpm\b|\bpip\b|\bgit\b|\bpython\b|\bbash\b|--\w+", next_step):
        score += 1
    if len(next_step.split(".")[0]) > 0 and next_step.count(".") <= 1:
        score += 1
    return min(score, 5)


def triage_pass(
    impact: int,
    urgency: int,
    confidence: str,
    actionability: int,
) -> tuple[bool, str]:
    if impact < 4:
        return False, "low_impact"
    if urgency < 3:
        return False, "low_urgency"
    if confidence == "low":
        return False, "low_confidence"
    if actionability < 3:
        return False, "low_actionability"
    return True, "pass"


def is_current_fingerprint(fingerprint: str) -> bool:
    return bool(_CURRENT_FINGERPRINT_RE.match(fingerprint))


def normalize_finding_part(value: str) -> str:
    return _WHITESPACE_RE.sub(" ", value.lower().strip())


def build_finding_id(claim: str, impact_surface: str) -> str:
    payload = f"{normalize_finding_part(claim)}\n{normalize_finding_part(impact_surface)}"
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:8]
    return f"f-{digest}"
