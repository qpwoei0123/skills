# coverage-log 스키마

매 실행마다 Orchestrator가 view별 메모리 파일에 기록한다.
triage-rules.md의 재검토 트리거와 탐색 나침반이 이 파일을 기준으로 작동한다.

**저장 위치:**
- `~/.repo-orbit/<group>/<project>/<VIEW>.json` (view별 독립 파일)
- `~/.repo-orbit/<group>/<project>/result.json` (마지막 실행 상세)
- 환경변수 `REPO_ORBIT_HOME`을 설정하면 기본 경로(`~/.repo-orbit`)를 오버라이드한다.
- 첫 실행 시 디렉토리가 없으면 자동 생성한다. view 파일이 없으면 아래 초기값으로 생성한다.

**인증 설정:**
- `~/.repo-orbit/auth.json`에 토큰을 저장한다. 스킬 폴더 안에 두지 않는다.
- 우선순위: 환경변수 → `auth.json` → 없으면 실행 전 사용자에게 입력 요청.

```json
// ~/.repo-orbit/auth.json
{
  "github_token": "ghp_...",
  "gitlab_token": "glpat-...",
  "gitlab_base_url": "https://gitlab.example.com"
}
```

- `gitlab_base_url`은 자체 호스팅 GitLab일 때만 설정한다. 생략 시 `https://gitlab.com` 기본값.
- 환경변수는 `GITHUB_TOKEN` / `GITLAB_TOKEN`을 인식한다.

---

## view 메모리 파일 스키마

`~/.repo-orbit/<group>/<project>/BUILD.json` 예시:

```json
{
  "view_id": "BUILD",
  "last_scan_commit": "abc1234f",
  "explored_files": [
    {
      "path": ".gitlab-ci.yml",
      "depth": "thorough",
      "last_explored": "2026-04-07"
    },
    {
      "path": "package.json",
      "depth": "thorough",
      "last_explored": "2026-04-07"
    },
    {
      "path": "Dockerfile",
      "depth": "surface",
      "last_explored": "2026-04-01"
    }
  ],
  "known_findings": {
    "pipeline:fe1/repo:BUILD:E1": {
      "status": "open",
      "first_seen": "2026-04-01",
      "last_seen": "2026-04-07",
      "claim_summary": "CI Node.js 버전 불일치"
    },
    "pipeline:fe1/repo:BUILD:E2": {
      "status": "closed",
      "first_seen": "2026-03-25",
      "last_seen": "2026-03-25",
      "claim_summary": "lockfile 없음"
    }
  },
  "run_history": [
    {
      "run_at": "2026-04-07T09:00:00+09:00",
      "commit": "abc1234f",
      "diff_base": "def5678a",
      "changed_files": [".gitlab-ci.yml"],
      "observations_collected": 4,
      "findings_after_merge": 2,
      "triage_passed": 1,
      "issued": 1
    }
  ]
}
```

---

## 필드 정의

### 최상위 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `view_id` | string | 이 파일이 담당하는 view (SAFE/ARCH/DEP/BUILD/DATA/OPS/DOC) |
| `last_scan_commit` | string | 마지막으로 분석한 HEAD 커밋 해시. 다음 실행의 diff 기준점. |
| `explored_files` | object[] | 지금까지 탐색한 파일 목록. 탐색 나침반의 핵심 데이터. |
| `known_findings` | object | fingerprint → finding 상태 맵. 재발행 억제에 사용. |
| `run_history` | object[] | 실행 이력. 최근 10개만 보관, 오래된 것은 제거. |

### explored_files 항목

| 필드 | 타입 | 설명 |
|------|------|------|
| `path` | string | 레포 루트 기준 파일 경로 |
| `depth` | string | `thorough`(전체 정독) / `surface`(트리만 확인) |
| `last_explored` | string | 마지막 탐색 날짜 (YYYY-MM-DD) |

### known_findings 항목

| 필드 | 타입 | 설명 |
|------|------|------|
| `status` | string | `open` / `closed` / `suppressed` |
| `first_seen` | string | 처음 발견 날짜 |
| `last_seen` | string | 마지막으로 확인된 날짜 |
| `claim_summary` | string | finding 내용 한 줄 요약 |

`suppressed`: 사용자가 "이건 알고 있음, 더 이상 보고하지 마" 처리한 finding.

### run_history 항목

| 필드 | 타입 | 설명 |
|------|------|------|
| `run_at` | ISO 8601 | 실행 시작 시각 |
| `commit` | string | 실행 시점 HEAD 커밋 |
| `diff_base` | string | diff 기준 커밋 (이전 `last_scan_commit`) |
| `changed_files` | string[] | diff에서 감지된 변경 파일 목록 |
| `observations_collected` | int | 수집된 raw 관찰 수 |
| `findings_after_merge` | int | 병합 후 finding 수 |
| `triage_passed` | int | triage 통과 수 |
| `issued` | int | 이슈 발행 성공 수 (`skipped_closed` 미포함) |

---

## 탐색 나침반 작동 원리

Orchestrator는 Step 2에서 이 파일을 읽어 에이전트에게 탐색 우선순위를 전달한다.

```
Priority 1 — 변경된 파일 (diff에서 감지)
  → 지금까지 탐색했든 안 했든 반드시 분석

Priority 2 — 아직 탐색하지 않은 파일 (explored_files에 없음)
  → 이 view에 관련된 파일 중 안 가본 곳

Priority 3 — 오래 전 surface 탐색만 된 파일
  → depth=surface + last_explored 오래된 것

Skip — 최근 thorough 탐색 완료 + 변경 없음
  → explored_files에 있고 depth=thorough + last_scan_commit 이후 변경 없음
```

매 실행마다 새 영역을 커버하므로, 시간이 지나면 레포 전체가 점진적으로 탐색된다.

---

## 메모리 업데이트 규칙

실행 완료 후 Orchestrator가 view 파일을 갱신한다.

1. `last_scan_commit` → 현재 HEAD로 업데이트
2. `explored_files` → 이번에 분석한 파일 추가/갱신
3. `known_findings` → 새 finding 추가, 코드가 바뀐 영역의 closed finding은 status 재검토
4. `run_history` → 새 entry prepend, 11번째 이상은 제거

---

## 재검토 트리거 계산 기준

triage-rules.md의 재검토 트리거는 `run_history` 최근 N개 entry로 판단한다.
전체 실행 기준이 아니라 view별로 독립 집계한다.

| 트리거 조건 | 판단 기준 |
|------------|----------|
| findings_issued = 0 연속 N회 | `issued == 0` 연속 |
| triage 전량 통과 연속 N회 | `triage_passed == findings_after_merge` 연속 |
| findings_issued >= 4 연속 N회 | `issued >= 4` 연속 |

---

## 에이전트 실패 기록

**`agents_skipped`와 `agent_errors`의 구분:**
- `agents_skipped`: Step 2에서 스킵 조건에 의해 애초에 spawn하지 않은 에이전트. 정상 흐름.
- `agent_errors`: spawn됐으나 timeout 또는 오류로 결과를 반환하지 못한 경우. result.json에 기록.

```json
"agent_errors": [
  {
    "agent": "B",
    "reason": "timeout",
    "fallback": "partial_results_used"
  }
]
```

`fallback` 값:
- `partial_results_used` — 나머지 에이전트 결과로 계속 진행
- `step_aborted` — 해당 실행 중단
