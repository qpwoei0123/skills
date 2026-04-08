#!/usr/bin/env python3
"""
repo-orbit issue publisher
GitHub / GitLab 이슈 생성, 업데이트, reopen을 담당한다.
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


# 재시도 정책: 429(rate limit) 와 5xx(일시 오류) 에 한정
_RETRY_STATUS = {429, 500, 502, 503, 504}
_MAX_RETRIES = 3
_BASE_DELAY = 1.0  # seconds


class PublishFallback(Exception):
    """자동 발행 대신 수동 복붙 출력을 내려야 할 때 사용한다."""


MAX_TITLE_LENGTH = 50


def load_auth(platform: str, base_url: str) -> tuple[str | None, str]:
    """토큰과 API base를 반환한다."""
    auth_path = Path.home() / ".repo-orbit" / "auth.json"
    auth_file: dict[str, str] = {}

    if auth_path.exists():
        try:
            auth_file = json.loads(auth_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            auth_file = {}

    if platform == "github":
        token = os.environ.get("GITHUB_TOKEN") or auth_file.get("github_token")
        return token, "https://api.github.com"

    token = os.environ.get("GITLAB_TOKEN") or auth_file.get("gitlab_token")
    resolved_base = auth_file.get("gitlab_base_url", base_url).rstrip("/")
    return token, resolved_base


def detect_platform(repo_url: str) -> tuple[str, str, str]:
    """repo_url을 파싱해 플랫폼, base_url, project 경로를 반환한다."""
    parsed = urllib.parse.urlparse(repo_url)
    host = parsed.netloc.lower()
    project = parsed.path.strip("/")

    if "github.com" in host:
        return "github", "https://api.github.com", project

    scheme = parsed.scheme or "https"
    return "gitlab", f"{scheme}://{host}", project


def parse_link_header(header: str | None) -> dict[str, str]:
    """GitHub Link 헤더에서 rel별 URL을 추출한다."""
    if not header:
        return {}

    links: dict[str, str] = {}
    for part in header.split(","):
        section = part.strip().split(";")
        if len(section) < 2:
            continue
        url = section[0].strip().lstrip("<").rstrip(">")
        rel = ""
        for item in section[1:]:
            item = item.strip()
            if item.startswith("rel="):
                rel = item.split("=", 1)[1].strip('"')
        if rel:
            links[rel] = url
    return links


def get_header(headers: dict, key: str) -> str:
    """헤더를 대소문자 구분 없이 읽는다."""
    lowered = key.lower()
    for name, value in headers.items():
        if name.lower() == lowered:
            return value
    return ""


def normalize_title(title: str) -> str:
    """제목 길이를 계약에 맞게 자른다."""
    return title[:MAX_TITLE_LENGTH]


def has_exact_fingerprint(body: str | None, fingerprint: str) -> bool:
    """본문 footer에 exact fingerprint가 있는지 확인한다."""
    if not body:
        return False
    expected = f"fingerprint: {fingerprint}"
    return any(line.strip() == expected for line in body.splitlines())


def validate_issue_contract(title: str, body: str, fingerprint: str) -> str:
    """repo-orbit 발행 계약을 검증한다."""
    normalized_title = normalize_title(title)

    if not normalized_title.startswith("[view: "):
        raise PublishFallback("제목은 반드시 [view: <view_id>] 접두어로 시작해야 합니다.")
    if "format_version: repo-orbit/v2" not in body:
        raise PublishFallback("본문 하단에 format_version: repo-orbit/v2 가 필요합니다.")
    if not has_exact_fingerprint(body, fingerprint):
        raise PublishFallback("본문 하단 fingerprint 값이 요청 fingerprint와 일치해야 합니다.")

    return normalized_title


def api_request(
    method: str,
    url: str,
    platform: str,
    token: str,
    data: dict | None = None,
) -> tuple[object, dict]:
    """JSON API 요청을 보내고 본문과 헤더를 반환한다.

    429(rate limit)와 5xx(일시 오류)는 최대 _MAX_RETRIES 회 지수 백오프 재시도한다.
    그 외 4xx는 즉시 PublishFallback을 올린다.
    """
    body = json.dumps(data).encode("utf-8") if data is not None else None
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    if platform == "github":
        headers["Authorization"] = f"Bearer {token}"
    else:
        headers["PRIVATE-TOKEN"] = token

    last_error: Exception | None = None

    for attempt in range(_MAX_RETRIES + 1):
        request = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request) as response:
                raw = response.read().decode("utf-8")
                payload = json.loads(raw) if raw else {}
                return payload, dict(response.headers.items())
        except urllib.error.HTTPError as error:
            if error.code in _RETRY_STATUS and attempt < _MAX_RETRIES:
                # Retry-After 헤더가 있으면 그 값을 존중한다
                retry_after_raw = error.headers.get("Retry-After", "")
                try:
                    delay = float(retry_after_raw)
                except (ValueError, TypeError):
                    delay = _BASE_DELAY * (2 ** attempt)
                last_error = error
                time.sleep(delay)
                continue
            raw = error.read().decode("utf-8", errors="replace")
            raise PublishFallback(f"HTTP {error.code} - {url}\n{raw}") from error
        except urllib.error.URLError as error:
            if attempt < _MAX_RETRIES:
                time.sleep(_BASE_DELAY * (2 ** attempt))
                last_error = error
                continue
            raise PublishFallback(f"네트워크 오류 - {error.reason}") from error

    # 재시도 소진
    raise PublishFallback(f"재시도 {_MAX_RETRIES}회 초과: {last_error}") from last_error


def build_manual_payload(
    reason: str,
    repo_url: str,
    platform: str,
    project: str,
    title: str,
    body: str,
    fingerprint: str,
    labels: list[str],
) -> dict:
    """자동 발행이 불가능할 때 수동 발행용 payload를 만든다."""
    label_text = ", ".join(labels) if labels else "(없음)"
    return {
        "action": "manual_required",
        "reason": reason,
        "repo_url": repo_url,
        "platform": platform,
        "project": project,
        "title": title,
        "body": body,
        "fingerprint": fingerprint,
        "labels": labels,
        "copy_paste_text": "\n".join([
            "[manual issue publish]",
            f"title: {title}",
            f"labels: {label_text}",
            f"fingerprint: {fingerprint}",
            "",
            body,
        ]),
    }


def iter_github_issues(api_base: str, project: str, token: str):
    """GitHub 이슈를 페이지네이션으로 순회한다."""
    next_url = f"{api_base}/repos/{project}/issues?state=all&per_page=100"

    while next_url:
        issues, headers = api_request("GET", next_url, "github", token)
        for issue in issues:
            if issue.get("pull_request"):
                continue
            yield issue
        next_url = parse_link_header(get_header(headers, "Link")).get("next")


def iter_gitlab_issues(api_base: str, project: str, token: str):
    """GitLab 이슈를 페이지네이션으로 순회한다."""
    encoded = urllib.parse.quote(project, safe="")
    next_page = "1"

    while next_page:
        url = (
            f"{api_base}/api/v4/projects/{encoded}/issues"
            f"?state=all&per_page=100&page={next_page}"
        )
        issues, headers = api_request("GET", url, "gitlab", token)
        for issue in issues:
            yield issue
        next_page = get_header(headers, "X-Next-Page")
        if next_page in ("", "0"):
            break


def find_existing_issue(
    platform: str,
    api_base: str,
    project: str,
    token: str,
    fingerprint: str,
) -> dict | None:
    """동일 fingerprint 이슈를 찾아 반환한다."""
    iterator = (
        iter_github_issues(api_base, project, token)
        if platform == "github"
        else iter_gitlab_issues(api_base, project, token)
    )

    for issue in iterator:
        body = issue.get("body") if platform == "github" else issue.get("description")
        if has_exact_fingerprint(body, fingerprint):
            return issue
    return None


def github_ensure_labels(api_base: str, project: str, token: str, labels: list[str]) -> None:
    """GitHub 라벨을 보장한다."""
    url = f"{api_base}/repos/{project}/labels?per_page=100"
    existing, _ = api_request("GET", url, "github", token)
    existing_names = {item["name"] for item in existing}

    for label in labels:
        if label not in existing_names:
            api_request(
                "POST",
                f"{api_base}/repos/{project}/labels",
                "github",
                token,
                {"name": label, "color": "0075ca"},
            )


def gitlab_ensure_labels(api_base: str, project: str, token: str, labels: list[str]) -> None:
    """GitLab 라벨을 보장한다."""
    encoded = urllib.parse.quote(project, safe="")
    url = f"{api_base}/api/v4/projects/{encoded}/labels?per_page=100"
    existing, _ = api_request("GET", url, "gitlab", token)
    existing_names = {item["name"] for item in existing}

    for label in labels:
        if label not in existing_names:
            api_request(
                "POST",
                f"{api_base}/api/v4/projects/{encoded}/labels",
                "gitlab",
                token,
                {"name": label, "color": "#0075ca"},
            )


def github_create(api_base: str, project: str, token: str, title: str, body: str, labels: list[str]) -> dict:
    """GitHub 이슈를 생성한다."""
    payload, _ = api_request(
        "POST",
        f"{api_base}/repos/{project}/issues",
        "github",
        token,
        {"title": title, "body": body, "labels": labels},
    )
    return payload


def github_update(
    api_base: str,
    project: str,
    token: str,
    number: int,
    title: str,
    body: str,
    labels: list[str],
    state: str = "open",
) -> dict:
    """GitHub 이슈를 업데이트한다."""
    payload, _ = api_request(
        "PATCH",
        f"{api_base}/repos/{project}/issues/{number}",
        "github",
        token,
        {"title": title, "body": body, "labels": labels, "state": state},
    )
    return payload


def gitlab_create(api_base: str, project: str, token: str, title: str, body: str, labels: list[str]) -> dict:
    """GitLab 이슈를 생성한다."""
    encoded = urllib.parse.quote(project, safe="")
    payload, _ = api_request(
        "POST",
        f"{api_base}/api/v4/projects/{encoded}/issues",
        "gitlab",
        token,
        {"title": title, "description": body, "labels": ",".join(labels)},
    )
    return payload


def gitlab_update(
    api_base: str,
    project: str,
    token: str,
    iid: int,
    title: str,
    body: str,
    labels: list[str],
    state_event: str | None = None,
) -> dict:
    """GitLab 이슈를 업데이트한다."""
    encoded = urllib.parse.quote(project, safe="")
    payload = {"title": title, "description": body, "labels": ",".join(labels)}
    if state_event:
        payload["state_event"] = state_event

    response, _ = api_request(
        "PUT",
        f"{api_base}/api/v4/projects/{encoded}/issues/{iid}",
        "gitlab",
        token,
        payload,
    )
    return response


def publish_issue(
    repo_url: str,
    title: str,
    body: str,
    fingerprint: str,
    labels: list[str],
) -> dict:
    """repo-orbit finding 하나를 발행한다."""
    platform, base_url, project = detect_platform(repo_url)
    safe_title = normalize_title(title)

    try:
        title = validate_issue_contract(title, body, fingerprint)
    except PublishFallback as error:
        return build_manual_payload(
            str(error),
            repo_url,
            platform,
            project,
            safe_title,
            body,
            fingerprint,
            labels,
        )

    token, api_base = load_auth(platform, base_url)

    if not token:
        return build_manual_payload(
            "인증 토큰이 없어 자동 발행을 건너뛰었습니다.",
            repo_url,
            platform,
            project,
            title,
            body,
            fingerprint,
            labels,
        )

    try:
        if platform == "github":
            github_ensure_labels(api_base, project, token, labels)
        else:
            gitlab_ensure_labels(api_base, project, token, labels)

        existing = find_existing_issue(platform, api_base, project, token, fingerprint)

        if existing is None:
            if platform == "github":
                result = github_create(api_base, project, token, title, body, labels)
                return {
                    "action": "created",
                    "platform": platform,
                    "project": project,
                    "issue_id": result["number"],
                    "issue_url": result["html_url"],
                }

            result = gitlab_create(api_base, project, token, title, body, labels)
            return {
                "action": "created",
                "platform": platform,
                "project": project,
                "issue_id": result["iid"],
                "issue_url": result["web_url"],
            }

        is_closed = (existing.get("state") or "") == "closed"

        if platform == "github":
            result = github_update(
                api_base,
                project,
                token,
                existing["number"],
                title,
                body,
                labels,
                "open",
            )
            action = "reopened" if is_closed else "updated"
            return {
                "action": action,
                "platform": platform,
                "project": project,
                "issue_id": result["number"],
                "issue_url": result["html_url"],
            }

        result = gitlab_update(
            api_base,
            project,
            token,
            existing["iid"],
            title,
            body,
            labels,
            "reopen" if is_closed else None,
        )
        action = "reopened" if is_closed else "updated"
        return {
            "action": action,
            "platform": platform,
            "project": project,
            "issue_id": result["iid"],
            "issue_url": result["web_url"],
        }
    except PublishFallback as error:
        return build_manual_payload(
            f"자동 발행 중 오류가 발생했습니다.\n{error}",
            repo_url,
            platform,
            project,
            title,
            body,
            fingerprint,
            labels,
        )


def parse_args() -> argparse.Namespace:
    """CLI 인자를 파싱한다."""
    parser = argparse.ArgumentParser(description="repo-orbit issue publisher")
    parser.add_argument("--repo-url", required=True, help="레포 URL")
    parser.add_argument("--title", required=True, help="이슈 제목")
    parser.add_argument("--body", help="이슈 본문 문자열")
    parser.add_argument("--body-file", help="이슈 본문 파일 경로")
    parser.add_argument("--fingerprint", required=True, help="중복 체크용 fingerprint")
    parser.add_argument("--labels", default="automation", help="쉼표 구분 라벨 목록")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="API 호출 없이 발행 payload만 출력한다.",
    )
    return parser.parse_args()


def read_body(args: argparse.Namespace) -> str:
    """body 또는 body-file에서 본문을 읽는다."""
    if args.body:
        return args.body
    if args.body_file:
        return Path(args.body_file).read_text(encoding="utf-8")
    raise SystemExit("body 또는 body-file 중 하나는 필요합니다.")


def main() -> None:
    """CLI 진입점."""
    args = parse_args()
    body = read_body(args)
    labels = [item.strip() for item in args.labels.split(",") if item.strip()]

    if args.dry_run:
        platform, _, project = detect_platform(args.repo_url)
        safe_title = normalize_title(args.title)
        label_text = ", ".join(labels) if labels else "(없음)"
        result = {
            "action": "dry_run",
            "platform": platform,
            "project": project,
            "title": safe_title,
            "fingerprint": args.fingerprint,
            "labels": labels,
            "copy_paste_text": "\n".join([
                "[dry-run — 실제 발행 없음]",
                f"title: {safe_title}",
                f"labels: {label_text}",
                f"fingerprint: {args.fingerprint}",
                "",
                body,
            ]),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    result = publish_issue(args.repo_url, args.title, body, args.fingerprint, labels)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
