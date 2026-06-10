# Changelog

## 1.11.0

### Added
- `evals/` 디렉터리 추가: 시나리오 eval 정의(evals.json)와 트리거 eval 케이스(trigger-eval.json) 편입

## 1.10.2

- 리뷰어 이모지를 단일 코드포인트로 교체해 GitHub·GitLab에서 ZWJ 조합이 분리되는 문제를 없앴습니다: `[🧭 리드 리뷰어]`, `[🔄 변경 리뷰어]`, `[🧪 커버리지 리뷰어]`, `[😈 위험 리뷰어]`.
- 본문 내 리뷰어 태그도 라벨 **앞** 이모지 형식으로 통일해, `## 선택지` 항목과 시각 정렬을 맞췄습니다.

## 1.10.1

- 이슈 본문에서 리뷰어를 가리킬 때 역할 이모지 태그를 쓰도록 했습니다: `[리드 리뷰어 🧑‍🏫]`, `[변경 리뷰어 🕵️]`, `[커버리지 리뷰어 🧑‍💻]`, `[위험 리뷰어 👮]`.
- `## 선택지` 항목에도 라벨 앞 이모지를 고정했습니다: ✨ 정리한다 / 🙈 보류한다 / 👾 예외로 둔다 / 🚧 바로 막는다 / 🔧 고친다 / 🤦 오탐으로 닫는다 / 🔍 확인한다 / 🛡️ 예방한다.
- `format_version`은 `orbit/v2.3` 그대로 유지합니다. 본문 구조 변경이 아닌 표기 컨벤션이라 마이그레이션을 트리거하지 않습니다. 새 이슈와 점수·근거가 바뀌어 재작성되는 기존 이슈부터 적용됩니다.

## 1.10.0

- 이슈 본문 양식을 `orbit/v2.3`으로 올렸습니다.
- 첫 섹션을 `결론`에서 `결정할 것`으로 바꿔, 읽는 사람이 내려야 할 판단을 먼저 보게 했습니다.
- `알아야 할 개념` 섹션을 추가해 도메인명, 레이어명, 내부 약어처럼 판단에 필요한 굵직한 개념을 짧게 설명하도록 했습니다.
- `선택지`는 severity-aware 메뉴로 바꿨습니다. 구조 리스크에는 보류/예외 선택지를 허용하지만, 재현되는 결함·보안·데이터 손상·빌드 차단 이슈에는 보류 선택지를 쓰지 않습니다.
- 치명적 이슈는 `바로 막는다`, `고친다`, `오탐으로 닫는다`처럼 사고 대응에 맞는 선택지만 제시합니다.
- 접힌 상세 영역을 `orbit 정보`에서 `🧠 브레인스토밍 과정`으로 바꿔, 관찰에서 선택지 도출까지의 판단 흐름을 검증 가능한 요약으로 남기도록 했습니다.

## 1.9.0

- 이슈 본문 양식을 `orbit/v2.2`로 올렸습니다.
- 새 양식은 작업 지시가 아니라 사용자가 채택 여부를 판단하는 간결한 검토 제안으로 씁니다.
- 본문 상단은 `결론 → 왜 봤나요 → 어떻게 찾았나요 → 확인한 근거 → 다른 리뷰어 의견 → 왜 보고했나요 → 선택지` 순서로 고정했습니다.
- `## 조치`, `## 완료 기준` 같은 강제 작업 느낌의 섹션은 쓰지 않고, 가능한 대응은 `## 선택지`에 정리합니다.
- 발행 스크립트 호환을 위해 제목의 `[view: <VIEW>]` 접두어와 HTML comment fingerprint footer는 유지합니다.

## 1.8.0

- 같은 문제를 다시 발견했을 때 기존 이슈를 더 잘 찾아가도록 고쳤습니다. 분석 순서가 바뀌어도 문제 ID가 쉽게 바뀌지 않습니다.
- 이슈 본문 아래에 숨겨 두는 추적 표시를 `<!-- orbit-fingerprint: ... -->` 형식으로 통일했습니다.
- 예전 형식(`fingerprint:`)으로 남아 있는 기존 이슈와 명시적으로 전달된 과거 fingerprint alias도 계속 찾아냅니다. 그래서 업데이트 후 같은 문제가 새 이슈로 한 번 더 생길 가능성이 줄었습니다.
- 예전 `fingerprint:` 매칭은 footer 형태로 제한했습니다. 일반 설명 문장에 들어간 추적 ID를 기존 orbit 이슈로 오인하지 않습니다.
- `legacy-fingerprint`는 같은 repo/view의 ID 마이그레이션에만 쓰고, 다른 view에서 이미 추적 중인 동일 문제는 기존 이슈를 덮어쓰지 않고 보고서에만 표시합니다.
- 새로 만드는 이슈는 새 추적 표시 형식만 허용합니다. 형식이 틀리면 자동 발행하지 않고 수동 발행 안내로 돌려, 잘못된 이슈 생성을 막습니다.
- 사용자에게 보이는 역할 이름을 `리드 리뷰어`, `변경 리뷰어`, `커버리지 리뷰어`, `위험 리뷰어`로 정리했습니다. 내부 JSON 키와 파일명은 호환성을 위해 유지합니다.
- `$orbit`처럼 사용자가 직접 부를 때만 orbit이 실행된다는 점을 설명에 명확히 적었습니다.
- 관련 테스트를 추가했고, README의 버전과 테스트 명령도 최신 상태로 맞췄습니다.

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
