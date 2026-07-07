# Changelog

## 0.6.0

### Added
- 브랜치명 컨벤션 점검: push 전에 레포 문서와 최근 머지된 MR/PR의 브랜치명에서 컨벤션을 추정하고, 벗어나면 rename을 제안 (rename은 사용자 동의 없이 하지 않음, 이미 원격에 push된 브랜치는 제안 대상에서 제외)
- dirty worktree 분기: 중단 대신 commit 스킬을 호출해 diff 제외(A안)와 커밋 포함(B안) 두 MR 계획을 나란히 제시하고 선택받는 흐름 추가
- `preflight.sh`에 merge 커밋 기반 최근 머지 브랜치명 후보 섹션 추가 (squash 머지 레포는 gh/glab 확인으로 보완)

### Changed
- dirty worktree를 중단 조건에서 분기 조건으로 변경. B안을 선택받았을 때만 commit 스킬 절차로 커밋
- `--go`에서도 A안/B안 선택과 rename 여부는 질문 1회 후 진행 (둘 다 필요하면 한 번에 묶어 질문)

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
