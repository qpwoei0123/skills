# 조사 메모리

정기 발행 실행에서 이전 조사 범위와 원격 발행 결과를 이어받기 위한 기록이다. 분석·dry-run은 이 메모리를 읽을 수 있지만 탐색 완료 표시나 발행 상태를 변경하지 않는다. 임시 결과는 workspace의 `.context`나 임시 디렉터리에 저장한다.

## 위치와 초기값

- 기본: `~/.orbit/<group>/<project>/<VIEW>.json`
- `REPO_ORBIT_HOME`이 있으면 `~/.orbit` 대신 해당 경로를 사용한다.
- 기록할 첫 실행에 디렉터리를 생성한다. 기존 메모리가 없으면 `last_scan_commit: null`, `explored_files: []`, `known_findings: {}`, `run_history: []`로 시작한다.
- 발행 결과와 payload는 같은 저장소 메모리 아래 `runs/<run-id>/`에 둔다. 기존 `<group>/<project>/result.json`은 과거 결과 참조로 읽을 수 있다.

기존 경로에는 host 구분이 없으므로 같은 namespace/project가 여러 host에 있으면 섞일 수 있다. 새 기록에는 정규화한 `repo_url`을 남긴다. 다른 host의 기록이 확인되면 별도 `REPO_ORBIT_HOME`으로 분리한다. 출처를 확인하지 못한 기존 기록을 다른 대상에 갱신 근거로 사용하지 않는다.

## view 파일 예시

```json
{
  "view_id": "BUILD",
  "repo_url": "https://github.com/owner/repo",
  "last_scan_commit": "abc1234f",
  "explored_files": [
    {"path": "package.json", "depth": "thorough", "last_explored": "2026-09-10"}
  ],
  "known_findings": {
    "pipeline:owner/repo:BUILD:f-12345678": {
      "status": "open",
      "first_seen": "2026-09-10",
      "last_seen": "2026-09-10",
      "claim_summary": "확인된 문제",
      "issue_url": "https://github.com/owner/repo/issues/123"
    }
  },
  "pending_findings": {},
  "run_history": [
    {
      "run_at": "2026-09-10T09:00:00+09:00",
      "commit": "abc1234f",
      "diff_base": null,
      "changed_files": [],
      "observations_collected": 2,
      "findings_after_merge": 1,
      "triage_passed": 1,
      "issued": 1
    }
  ]
}
```

추가 필드가 없는 기존 메모리는 그대로 읽는다. `pending_findings`가 없으면 빈 맵으로 취급한다. 단순 포맷 정리를 위해 과거 기록을 새로 추정해 채우지 않는다.

## 탐색 범위

`last_scan_commit`은 실제 조사 기준인 `scan_sha`이며 현재 작업 branch의 HEAD가 아니다. `last_scan_commit..scan_sha`의 변경을 읽고, 기준 object가 없거나 이력이 갈라졌으면 필요한 범위만 가져오거나 새 조사로 전환한다. 빈 diff라고 가정하지 않는다.

우선순위는 변경된 관련 경로 → 미탐색 → 오래된 surface → 현재 판단에 필요한 재확인이다. `thorough`는 해당 관점의 내용과 연결 경로를 확인했다는 뜻이고 `surface`는 구조·일부 내용만 확인한 상태다. 단순 파일 목록 조회를 thorough로 기록하지 않는다.

최근 thorough·미변경 파일은 주 탐색에서 우선순위를 낮출 수 있지만 현재 claim의 증명·반례를 위해 다시 읽을 수 있다. 변경·미탐색·재확인 대상과 pending 발행이 모두 없을 때만 조기 종료한다. 동적 환경을 확인하지 않은 코드 조사 결과를 현재 운영 상태 확인으로 확대하지 않는다.

## known_findings 상태

| 상태 | 의미 | 변경 근거 |
|---|---|---|
| open | 원격에서 추적 중 | create/update 성공 또는 원격 상태 조회 |
| closed | 원격에서 닫힘 | 원격 확인 또는 publisher의 skipped_closed |
| suppressed | 사용자가 이후 발행을 억제 | 명시적인 suppress 요청 |

새 분석 결과나 실패한 발행을 open으로 기록하지 않는다. closed는 코드 변경·재분석만으로 open이 되지 않는다. suppressed는 사용자의 해제 요청 없이 변경하지 않는다. 원격에서 이미 재오픈된 사실이 확인되면 그 사실을 기록할 수 있지만 Orbit이 자동 재오픈하지 않는다.

다른 view의 같은 문제는 소유 view를 유지한다. 같은 view의 과거 ID라면 현재 ID와 연결할 근거를 남기고 legacy alias로 조회한다. `first_seen`은 유지하고 실제 재확인한 경우에만 `last_seen`을 갱신한다.

## 발행 실패와 부분 조사

발행에 실패한 후보는 `pending_findings[fingerprint]`에 `scan_sha`, claim 요약, 저장한 payload 경로와 실패 사유를 남긴다. 다음 발행 실행은 코드 변경이 없어도 pending을 확인한다. 이전 SHA의 결과를 무조건 발행하지 말고 현재 근거와 원격 중복 상태를 다시 확인한다.

create/update 성공 또는 확인된 closed/suppressed이면 해당 pending을 제거한다. 재확인 결과 claim을 철회한 경우도 사유와 함께 제거한다. 원격 결과가 불분명하면 성공으로 지우지 않는다.

조사가 부분 완료면 실패 범위를 남기고 `last_scan_commit`을 전진시키지 않는다. 실제 확인한 파일만 갱신하며, 다음 실행에서 남은 변경 경로를 다시 확인한다. 조사 자체가 완료됐다면 발행 실패와 별개로 scan 기준을 갱신할 수 있지만 실패 후보는 pending으로 유지해야 한다.

## 기록 쓰기

실제 발행 실행의 완료 시점에 view 메모리를 갱신한다. `run_history`는 새 항목을 앞에 넣고 최근 10개를 유지한다. `issued`에는 created·updated만 포함하고, closed·manual_required·실패·미검토 범위는 별도로 기록한다.

파일을 쓰기 전에 다시 읽어 동시 실행의 변경 여부를 확인하고 임시 파일 후 교체하는 방식으로 부분 기록을 피한다. 같은 view의 다른 revision 기록과 안전하게 합칠 수 없으면 실행별 결과를 보존하고 충돌을 보고한다. 더 최신의 기록을 조용히 덮어쓰지 않는다.

## 인증 설정

publisher의 인증은 `GITHUB_TOKEN` / `GITLAB_TOKEN` → `~/.orbit/auth.json` 순서다. `REPO_ORBIT_HOME`은 조사 메모리 위치만 바꾸며 현재 publisher의 인증 파일 경로는 바꾸지 않는다.

`auth.json`은 선택적으로 `github_token`, `gitlab_token`, `gitlab_base_url`을 가진다. GitLab API base는 설정값이 있으면 이를, 없으면 대상 URL의 scheme·host를 사용한다. 대상 host와 설정이 맞는지 확인한다. token을 스킬 폴더·저장소·대화에 저장하거나 출력하지 않는다. 인증이 없으면 수동 payload와 현재 환경에서 필요한 인증 설정만 안내한다.
