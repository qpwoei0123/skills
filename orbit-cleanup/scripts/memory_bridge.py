#!/usr/bin/env python3
"""Bridge orbit-cleanup actions back into orbit memory files."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path


def orbit_home() -> Path:
    return Path(os.environ.get("REPO_ORBIT_HOME", Path.home() / ".orbit")).expanduser()


def project_memory_dir(project: str, base: Path | None = None) -> Path:
    root = base or orbit_home()
    parts = [part for part in project.strip("/").split("/") if part]
    return root.joinpath(*parts)


def view_memory_path(project: str, view: str, base: Path | None = None) -> Path:
    return project_memory_dir(project, base) / f"{view}.json"


def cleanup_log_path(project: str, base: Path | None = None) -> Path:
    return project_memory_dir(project, base) / "cleanup-log.json"


def load_json(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        return deepcopy(default) if default is not None else {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return deepcopy(default) if default is not None else {}


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def default_view_memory() -> dict:
    return {"last_scan_commit": None, "explored_files": [], "known_findings": {}}


def default_cleanup_log() -> dict:
    return {"last_run_at": None, "auto_close_runs": 0, "history": []}


def apply_cleanup_actions(memory: dict, actions: list[dict]) -> dict:
    """Apply close/suppress/batch cleanup state transitions to one view memory dict."""
    updated = deepcopy(memory)
    known = updated.setdefault("known_findings", {})

    for action in actions:
        fingerprint = action.get("fingerprint")
        if not fingerprint:
            continue
        entry = known.setdefault(fingerprint, {})
        category = action.get("category")

        if category == "RESOLVED" and action.get("confidence") == "high" and action.get("close"):
            entry["status"] = "closed"
            entry["cleanup_closed_at"] = action.get("run_at")
            continue

        if category == "DUP" and action.get("close"):
            entry["status"] = "suppressed"
            canonical = action.get("canonical_fingerprint")
            if canonical:
                entry["alias_of"] = canonical
            continue

        if category == "BATCH":
            module = action.get("batch_module")
            if not module:
                continue
            tag = f"batch:{module}"
            tags = entry.setdefault("cleanup_tags", [])
            if tag not in tags:
                tags.append(tag)

    return updated


def actions_by_view(actions: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for action in actions:
        view = action.get("view")
        if view:
            grouped.setdefault(view, []).append(action)
    return grouped


def update_view_memories(project: str, actions: list[dict], base: Path | None = None) -> None:
    """Persist action-derived status changes into each affected orbit view memory file."""
    for view, view_actions in actions_by_view(actions).items():
        path = view_memory_path(project, view, base)
        memory = load_json(path, default_view_memory())
        write_json(path, apply_cleanup_actions(memory, view_actions))


def load_cleanup_log(project: str, base: Path | None = None) -> dict:
    payload = load_json(cleanup_log_path(project, base), default_cleanup_log())
    payload.setdefault("history", [])
    payload.setdefault("auto_close_runs", 0)
    return payload


def record_cleanup_history(
    project: str,
    summary: dict,
    *,
    base: Path | None = None,
    run_at: str | None = None,
) -> dict:
    """Append a run summary and bump auto_close_runs only after actual closes."""
    log = load_cleanup_log(project, base)
    timestamp = run_at or datetime.now(timezone.utc).isoformat()
    entry = {"run_at": timestamp, **summary}
    log["last_run_at"] = timestamp
    log.setdefault("history", []).append(entry)
    if summary.get("closed", 0) > 0:
        log["auto_close_runs"] = int(log.get("auto_close_runs", 0)) + 1
    write_json(cleanup_log_path(project, base), log)
    return log
