# Changelog

## 1.7.0

### 메모리 & 탐색

- **per-view 메모리 도입**: 단일 `coverage-log.json` 대신 view별 독립 파일 (`~/.orbit/<group>/<project>/<VIEW>.json`)로 전환
- **diff 기반 분석**: `git diff last_scan_commit..HEAD`로 변경 파일을 파악해 full scan 반복 제거
- **탐색 나침반**: `explored_files` + `changed_files`를 조합한 Priority 1/2/3/Skip 우선순위 시스템으로 매 실행마다 새 영역을 탐색
- **조기 종료 조건**: 변경 없음 + 미탐색 파일 없음이면 에이전트 spawn 없이 즉시 종료. 조기 종료 시 `run_history` 기록 값과 `last_scan_commit` 미갱신 규칙 명시
- **cross-view 중복 방지**: Step 2에서 전체 7개 view 메모리의 open `claim_summary`를 컨텍스트에 보관, triage 시 이미 추적 중인 문제는 발행 생략
- **`--suppress` 옵션**: 특정 fingerprint를 `suppressed`로 변경해 이후 실행에서 이슈화 대상에서 제외

### 에이전트 & 도메인 지식

- `agent-playbook.md`에 **선언 경로 vs 도구 실제 경로 교차 확인** 패턴 추가: 전체 view 공통. pnpm/npm/pip/Gradle/Docker buildx 등 대표 사례 포함
- `coverage-log-schema.md` 전면 재작성: per-view 스키마, 탐색 나침반 작동 원리, 메모리 업데이트 규칙, 재검토 트리거 계산 기준

### 파이프라인 규칙

- `SKILL.md` Step 1에 메모리 로드 절 추가, Step 2에 diff 계산 + 탐색 우선순위 계산 절 추가
- `orchestrator.md` 실행 순서 확장(11단계), 탐색 나침반 절 신규, 메모리 갱신 규칙 절 신규, suppressed 처리 절 신규
- `triage-rules.md` 재검토 트리거 기준을 `run_history` 최근 3개 entry, view별 독립 집계로 명확화

### 단순화

- `output-templates.md` 분석 히스토리를 조건부 적용 (반박·재조사·이의 있을 때만 작성)
- `output-templates.md` 최종 보고에 탐색 나침반 결과와 `이미 추적 중` 항목 추가, 조기 종료 보고 형식 추가
- `orchestrator.md` confidence 판정 규칙에서 SKILL.md 중복 요약 제거, 경계 케이스만 유지

## 1.6.0

- 이슈 템플릿 UI/UX 개선: 역피라미드 구조로 재편 (`## 조치`를 `## 문제`보다 먼저 배치)
- 분석 히스토리 · 이슈화 근거를 `<details>` 접기 블록으로 전환 (기본 접힘)
- 심각도 배지 추가: 🔴 CRITICAL / 🟠 HIGH / 🟡 MEDIUM (impact·urgency 기준)
- 이슈 상단 첫 줄에 배지 + impact_surface 핵심 요약 한 줄 표시
- `format_version` 을 `orbit/v2.0.1` → `orbit/v2.1`로 올림
- footer 형식 변경: 두 줄 → `format_version · fingerprint` 한 줄
- output-templates.md 마이그레이션 규칙 표 추가 (v2.0.1 이하 → 전체 재작성)

## 1.5.0

- closed 이슈 정책 통일: triage-rules.md, orchestrator.md, README.md를 SKILL.md와 일치 (`skipped_closed`, 재오픈 없음)
- 테스트 수정: `test_gitlab_closed_issue_reopens_on_update` → `test_gitlab_closed_issue_returns_skipped_closed`
- 테스트 수정: `test_github_update_reapplies_labels` state 파라미터를 `None`으로 정정
- 에이전트 timeout SLA 명시 (1라운드 5분, 2라운드 2분, 3/4.5라운드 1~2분)
- Python 3.10+ 최소 버전 명시 (SKILL.md, README.md)
- `scripts/test_pipeline.py` 신규: Step 1~5 파이프라인 로직 17개 단위 테스트
- `INDEX.md` 신규: 전체 문서 진입점 (빠른 시작, 파일 역할, 테스트 실행 방법)
- 전체 테스트: 7 (publish) + 17 (pipeline) = **24/24 통과**

## 1.4.0

- 에이전트 주도 이의 제기 라운드 추가 (Step 4.5)
- orchestrator.md 이의 처리 절차·제한·판정 기록 형식 추가
- output-templates.md 이의 제기/판정 렌더링 블록 + 예시 추가
- SKILL.md frontmatter에 `version` 필드 추가
- output-templates.md에 `format_version` 마이그레이션 규칙 명시
- CHANGELOG.md 신규 생성

## 1.3.0

- 이슈 출력 포맷 전면 개편: GitHub alerts (`[!WARNING]`, `[!TIP]`) + `diff` 블록
- `<details>` 접기 제거, `---` + 볼드 인용 구분선 방식으로 전환
- 출력 예시 전면 재작성 (npm install → npm ci 시나리오)

## 1.2.0

- orchestrator.md confidence 판정 모순 수정 (source 파일 2개 필수 조건 제거)
- view별 스킵/대체 분석 위임 규칙 명시 (ARCH FSD 없는 레포, DATA 백엔드 레포)

## 1.1.0

- SKILL.md Step 3 observation/rebuttal/query_response 스키마 인라이닝
- publish_issue.py 네트워크 retry + exponential backoff (429/5xx, 최대 3회)
- Retry-After 헤더 지원

## 1.0.0

- 초기 릴리스: 7개 view (SAFE/ARCH/DEP/BUILD/DATA/OPS/DOC)
- view당 Agent A/B/C 3인 구조 + Orchestrator 병합·채점·triage
- 4-criteria triage (impact≥4, urgency≥3, confidence≠low, actionability≥3)
- fingerprint 기반 중복 방지
- publish_issue.py GitHub/GitLab 이슈 발행 + dry-run 지원
