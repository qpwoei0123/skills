# coverage-log.json 스키마

coverage-log.json은 매 실행마다 Orchestrator가 entry 하나를 append한다.
triage-rules.md의 재검토 트리거와 실행 이력 집계가 이 파일을 기준으로 작동한다.

**저장 위치:**
- `~/.repo-orbit/<group>/<project>/coverage-log.json` (기본값)
- `~/.repo-orbit/<group>/<project>/result.json` (동일 디렉토리에 함께 저장)
- 환경변수 `REPO_ORBIT_HOME`을 설정하면 기본 경로(`~/.repo-orbit`)를 오버라이드한다.
- 첫 실행 시 디렉토리가 없으면 자동 생성한다. coverage-log.json이 없으면 빈 배열 `[]`로 초기화한다.

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

## Entry 스키마

```json
{
  "run_at": "2026-04-01T06:13:56+09:00",
  "view_id": "DEP",
  "repo": "fe1/dbat",
  "branch": "main",
  "agents_ran": ["A", "B", "C"],
  "agents_skipped": [],
  "observations_collected": 5,
  "findings_after_merge": 3,
  "triage": {
    "passed": 3,
    "skipped": 0,
    "skip_breakdown": {
      "low_confidence": 0,
      "low_actionability": 0,
      "low_impact": 0,
      "low_urgency": 0
    }
  },
  "issued": 3,
  "issue_failed": 0,
  "triage_override": false,
  "triage_calibration": null,
  "rebuttals_received": 0,
  "rebuttals_with_evidence": 0,
  "queries_issued": 0,
  "queries_withdrawn": 0,
  "reexaminations_triggered": 0,
  "reexam_refined": 0,
  "reexam_withdrawn": 0,
  "reexam_upheld": 0
}
```

---

## 필드 정의

| 필드 | 타입 | 설명 |
|------|------|------|
| `run_at` | ISO 8601 | 실행 시작 시각. 로컬 타임존 포함. |
| `view_id` | string | 실행된 view (SAFE/ARCH/DEP/BUILD/DATA/OPS/DOC) |
| `repo` | string | `group/project` 형식 |
| `branch` | string | 분석 시점의 브랜치명 |
| `agents_ran` | string[] | 실제 실행된 에이전트 목록 |
| `agents_skipped` | string[] | 스킵 조건에 의해 실행되지 않은 에이전트 목록 |
| `observations_collected` | int | 1라운드에서 수집된 raw 관찰 합계 |
| `findings_after_merge` | int | 중복 병합 후 최종 finding 수 |
| `triage.passed` | int | triage 통과 finding 수 |
| `triage.skipped` | int | triage 스킵 finding 수 |
| `triage.skip_breakdown` | object | 스킵 사유별 건수 |
| `issued` | int | 실제 발행 성공한 이슈 수. create/update/reopen_update를 모두 포함한다. |
| `issue_failed` | int | 발행 실패한 이슈 수. 실패 상세는 result.json에 기록. |
| `triage_override` | bool | triage 기준 override 옵션 사용 여부 |
| `triage_calibration` | string\|null | 기준 변경 시 `"방향/이유"` 기록. 변경 없으면 null. |
| `rebuttals_received` | int | 2라운드에서 접수된 반박 총 건수 |
| `rebuttals_with_evidence` | int | 그 중 evidence를 포함한 반박 건수 |
| `queries_issued` | int | 3라운드 Orchestrator 질의 발생 건수 |
| `queries_withdrawn` | int | 질의 결과 claim이 철회된 finding 수 |
| `reexaminations_triggered` | int | Step 4.5 Orchestrator 반박으로 재조사가 발동된 건수 |
| `reexam_refined` | int | 재조사 결과 claim이 정교화된 finding 수 |
| `reexam_withdrawn` | int | 재조사 결과 claim이 철회된 finding 수 |
| `reexam_upheld` | int | 재조사 후 claim을 유지했으나 Orchestrator가 확정 스킵한 finding 수 |

---

## 재검토 트리거 계산 기준

triage-rules.md의 재검토 트리거는 아래 필드로 판단한다.

| 트리거 조건 | 참조 필드 |
|------------|----------|
| findings_issued = 0 연속 N회 | `issued == 0` |
| low_actionability > 50% 연속 N회 | `triage.skip_breakdown.low_actionability / findings_after_merge` |
| 전량 통과 연속 N회 | `triage.skipped == 0 AND triage.passed > 0` |
| findings_issued >= 4 연속 N회 | `issued >= 4` |

"연속 N회"는 **동일 view_id** 기준 최근 N개 entry를 본다.
전체 실행 기준이 아니라 view별로 독립 집계한다.

---

## 에이전트 실패 기록

**`agents_skipped`와 `agent_errors`의 구분:**
- `agents_skipped`: Step 2에서 스킵 조건(예: 컨테이너 없음, FSD 구조 없음)에 의해 **애초에 spawn하지 않은** 에이전트 목록. 정상 흐름이며 오류가 아니다.
- `agent_errors`: spawn됐으나 **timeout 또는 오류로 결과를 반환하지 못한** 경우. result.json의 `agent_errors` 배열에 별도 기록한다.

출력 보고의 "서브 에이전트" 줄에서 스킵은 `(B 스킵: 조건)`, 실패는 `(B 실패: timeout)` 으로 구분해 표기한다.

에이전트가 timeout 또는 오류로 실패한 경우 `agents_skipped`에 포함하지 않고,
result.json의 `agent_errors` 배열에 별도 기록한다.

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
