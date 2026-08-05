# Changelog

## 0.2.0

### Added
- 현재 branch에 열린 Draft가 있으면 새 요청 생성을 생략하고 기존 본문 갱신 계획을 보여주는 흐름 추가
- push 뒤 Draft 상태와 원격 본문을 재확인해 다른 사람의 수정을 덮지 않는 보호 규칙 추가
- 생성 본문에 관리 marker를 두고 이후 출항에서 해당 블록만 교체하는 사용자 작성 내용 보호 규칙 추가

### Changed
- 기존 Draft 제목·상태·리뷰어·라벨과 사용자 작성 본문을 보존하도록 `--go` 승인 경계 명확화

## 0.1.0

### Added
- `trim`, `annotate`, `commit`, `mr`을 한 번의 승인으로 잇는 출항 흐름 추가
- dirty worktree와 base 대비 기존 커밋을 함께 다루는 리뷰 범위 판정 추가
- 저가치 신규 테스트 판정, 제출 전 셀프 리뷰, 제목·본문 사전 보고 계약 추가
- Draft 강제, branch rename·force push·일반 PR/MR fallback 금지 경계 추가
