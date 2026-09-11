# Changelog

## 3.1.0

### Changed

- 역할에 맞는 공통 판단 모듈을 스킬 본문에 포함하고, 겹치는 개별 지침을 공통 원본으로 통합

## 3.0.0

### Changed

- 목록 설명에서 버전·호출 예시를 빼고 공백 포함 30자 이내의 행동 설명으로 축약

- 데일리 도구를 `⚡`로 구분하는 닷 접두사 적용

- `mr`과 `won-ship`을 데일리함의 `.⚡ship`으로 통합
- 기본 완료점을 필요한 커밋과 PR/MR 제목·본문안으로 정하고, 요청받은 push·Draft 생성·갱신까지 이어감
- 무관하거나 애매한 diff를 남길 수 있도록 하고 제출 범위의 독립성과 검증 근거를 확인
- 필수 코드 정리·테스트 정리 단계를 제거하고 기존 Draft의 본문 보존·동시 변경 확인 절차를 통합
- 실제 제출 범위와 주변 관례를 기준으로 본문을 작성하고, 본문만 원격 갱신할 때는 원격 head 기준 사용

## 1.0.1

### Fixed

- 기존 Draft 갱신 담당 스킬 참조를 `won-ship`으로 변경

## 1.0.0

### Changed
- 기본 호출을 Draft 제출로 변경하고 명시적인 준비·계획 요청은 읽기 전용으로 처리
- 현재 작업의 미커밋 변경을 포함하는 요청은 commit부터 이어가며 고정 A/B 재승인 제거
- 인증된 gh/glab과 HTTPS 경로 우선, 원격 추적 branch를 base 후보에서 제외
- 브랜치 관례를 필수 rename 근거로 추정하는 규칙과 사전 점검의 상시 이력 수집 제거
- 본문을 실제 문제·변화·필요한 검증 중심으로 줄이고 빈 리스크·검증 체크박스 기본값 제거

## 0.7.0

### Added
- 브랜치명 판정과 제목·본문 규칙을 필요할 때 읽는 `references/branch-conventions.md`, `references/review-format.md` 추가
- 커밋과 PR/MR을 함께 요청하면 mr이 전체 흐름을 소유하고 commit을 선행하는 연계 계약과 트리거 평가 추가

### Changed
- SKILL.md를 핵심 안전 계약·분기·실행 순서 중심으로 경량화하고 세부 판정표를 references로 분리

## 0.6.1

### Added
- Codex 스킬 목록에 표시할 이름·설명·기본 프롬프트 메타데이터 추가

### Fixed
- 스킬 디렉터리 기준 `preflight.sh` 실행 경로 수정

## 0.6.0

### Added
- 레포 기여 문서 확인 단계 추가: CONTRIBUTING(루트·.github/·docs/)의 브랜치명·제목·본문 규칙을 스킬 기본값보다 우선 적용하고, 계획에 참고한 기여 문서를 보고
- 브랜치명 컨벤션 점검: push 전에 기여 문서와 최근 머지된 MR/PR의 브랜치명에서 컨벤션을 추정하고, 벗어나면 rename을 제안 (rename은 사용자 동의 없이 하지 않음, 이미 원격에 push된 브랜치는 제안 대상에서 제외)
- dirty worktree 분기: 중단 대신 commit 스킬을 호출해 diff 제외(A안)와 커밋 포함(B안) 두 MR 계획을 나란히 제시하고 선택받는 흐름 추가
- `preflight.sh`에 기여 문서 후보와 merge 커밋 기반 최근 머지 브랜치명 후보 섹션 추가 (squash 머지 레포는 gh/glab 확인으로 보완)

### Changed
- dirty worktree를 중단 조건에서 분기 조건으로 변경. B안을 선택받았을 때만 commit 스킬 절차로 커밋
- `--go`에서도 A안/B안 선택과 rename 여부는 질문 1회 후 진행 (둘 다 필요하면 한 번에 묶어 질문)
- 제목 규칙을 "기여 문서 규칙이 있으면 그것이 최우선, 없으면 Conventional Commits"로 조정

## 0.5.1

### Fixed
- `preflight.sh` 플랫폼 추정을 3값(GitHub/GitLab/판단 불가)으로 수정: URL에 gitlab이 없으면 무조건 GitHub으로 찍혀 자체 호스팅 GitLab에서 gh 오실행을 유도하던 버그 제거

### Changed
- description을 "PR/MR을 새로 만들자는 말"로 좁히고 code-review·review 경계 명시 ("리뷰해줘" 오발동 차단)
- `--go` 검증 단계를 "레포에 정의된 test/lint 중 리뷰 범위 관련만 실행"으로 구체화
- "커밋하고 PR까지" 복합 요청 시 commit 스킬 절차를 먼저 잇는 연동 규칙 추가
- trigger-eval에 code-review·review·머지 경계 케이스 5건 보강

## 0.5.0

### Added
- `scripts/preflight.sh` 추가: git 읽기 전용 사전 점검(worktree 상태, 브랜치/remote, base 후보, 플랫폼 추정)을 한 번에 출력

## 0.4.0

### Added
- 트리거 동작을 검증하는 `evals/trigger-eval.json` 추가

### Changed
- 불변 규칙의 draft 강제, 일반 MR/PR fallback 금지, draft 미보장 중단 항목에 의도 근거를 한 줄씩 명시

## 0.3.2

### Changed
- MR/PR 생성 승인과 `--go`가 다음 사용자 요청으로 이월되지 않도록 세션 경계 규칙 추가
- MR/PR 생성 완료 후 자동 push/MR intent를 종료하고 후속 작업에서는 명시 요청을 다시 받도록 명시

## 0.3.1

### Changed
- GitHub/GitLab 모두 목록 확인과 본문 구조 확인을 별도 단계로 분리
- GitLab에서 `glab mr list`와 별도로 최근 MR 2~3개의 본문을 `glab mr view <iid> --comments=false`로 확인하도록 명시
- 로컬 템플릿이 없을 때 주변 MR/PR 본문 구조 확인과 fallback 보고를 강화
- MR 계획에 참고한 주변 MR/PR과 채택한 본문 구조를 보고하도록 추가

## 0.3.0

### Added
- 본문 판단 기준 추가: 접근 이유와 버린 대안, 리뷰 포인트 명시, 기계적 변경 묶기
- 셀프 리뷰 단계 추가: 생성 전 리뷰어 시점 재검토, 발견 문제 공개, 대형 diff 분할 제안

## 0.2.0

### Changed
- description에 자연어 트리거 문구 추가
- 분석 단계에 기존 열린 MR/PR 확인 추가, 중복 생성 방지를 중단 조건에 포함
- 본문 임시 파일을 고정 경로 대신 `mktemp`로 생성

## 0.1.0

### Added
- `/mr` 계획 모드와 `--go` 즉시 실행 모드 정의
- GitHub PR과 GitLab MR을 모두 draft로 생성하는 실행 계약 추가
- Conventional 형식 제목, 주변 MR/PR 스타일 참고, 레포 템플릿 기반 본문 규칙 추가
- dirty worktree와 draft 미보장 상황의 중단 조건 문서화
