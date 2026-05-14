---
name: orbit-cleanup
license: Apache-2.0
metadata:
  version: 1.0.0
description: >
  Weekly curator for orbit-generated GitHub/GitLab issues. Labels duplicate,
  batchable, and already-resolved orbit issues, comments with a structured
  explanation, conditionally closes safe high-confidence issues, and updates
  ~/.orbit known_findings so future orbit runs skip closed/suppressed findings.
  Activate ONLY when the user types $orbit-cleanup or explicitly references the
  orbit-cleanup skill by name. Do NOT trigger for generic cleanup, issue triage,
  repo audit, or orbit analysis requests. 한국어: $orbit-cleanup 또는 orbit-cleanup
  스킬을 명시할 때만 실행한다.
---

# orbit-cleanup

orbit가 발행한 누적 이슈를 주 1회 정리하는 독립 스킬이다. orbit의 7개 view 분석 규칙은 변경하지 않고,
이미 발행된 이슈 큐레이션만 담당한다.

## 실행 계약

입력은 GitHub/GitLab 레포 URL이다.

```text
$orbit-cleanup https://github.com/owner/repo
$orbit-cleanup https://github.com/owner/repo --dry-run
```

레포 URL이 없으면 먼저 현재 작업 디렉터리의 remote URL을 확인한다. 확인할 수 없으면 사용자에게 URL을 요청한다.

## 4 Step Flow

1. **Scope 확인**
   - 대상 레포 URL과 `--dry-run` 여부를 확인한다.
   - `orbit/scripts/publish_issue.py`의 인증, 플랫폼 감지, 이슈 페이지네이션 유틸을 재사용한다.
   - schedule 등록 요청이 아닌 한 cron 등록은 하지 않는다.

2. **이슈 수집 및 분류**
   - 현재 HTML footer `<!-- orbit-fingerprint: pipeline:<repo>:<VIEW>:f-xxxxxxxx -->`가 있는 이슈만 대상으로 한다.
   - 필요하면 `references/classification-rules.md`를 읽는다.
   - `scripts/classify.py`의 DUP, BATCH, RESOLVED 판별을 사용한다.

3. **안전장치 적용 및 발행**
   - 필요하면 `references/action-matrix.md`와 `references/safety-rules.md`를 읽는다.
   - `scripts/cleanup_issue.py --repo-url <url> --dry-run`으로 plan을 먼저 확인한다.
   - 사용자가 실제 적용을 요청했거나 `$orbit-cleanup <repo_url>` 직접 실행 의도가 명확하면 dry-run 없이 실행한다.
   - 모든 close는 safety gate를 통과해야 한다.

4. **메모리 갱신 및 보고**
   - `scripts/memory_bridge.py`가 `~/.orbit/<owner>/<repo>/<VIEW>.json`의 `known_findings`를 갱신한다.
   - `cleanup-log.json`에 run summary를 남긴다.
   - 최종 보고에는 scanned, dup, batch, resolved, closed, label_only, errors를 포함한다.

## 핵심 정책

- DUP high: 사본만 `cleanup:duplicate` 라벨, 정형 comment, 조건부 close.
- BATCH high/medium/low: 묶음 신호만 남기고 close하지 않는다.
- RESOLVED high: 코드 상태와 merged PR 신호가 함께 있을 때만 조건부 close.
- close 전 최근 사람 코멘트, 보호 라벨, 점진 신뢰, 실행당 close 상한을 모두 확인한다.
- cleanup 라벨 색상은 회색 계열 `cccccc`를 사용해 orbit 발행 라벨과 구분한다.

## 직접 실행

```bash
python3 orbit-cleanup/scripts/cleanup_issue.py \
  --repo-url https://github.com/owner/repo \
  --dry-run
```

오프라인 테스트나 샌드박스 재현은 JSON 이슈 배열을 사용한다.

```bash
python3 orbit-cleanup/scripts/cleanup_issue.py \
  --repo-url https://github.com/owner/repo \
  --issues-file /tmp/orbit-issues.json \
  --dry-run
```

## 참고 문서

- `references/classification-rules.md`: DUP/BATCH/RESOLVED 신호
- `references/action-matrix.md`: confidence별 action
- `references/safety-rules.md`: close gate
- `references/comment-templates.md`: comment 형식
- `references/memory-schema.md`: known_findings와 cleanup-log 스키마
