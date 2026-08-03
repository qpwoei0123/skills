# Changelog

## 0.3.1

### Added
- `scripts/test_score.py` 회귀 테스트 추가
- OpenAI 스킬 메타데이터 `agents/openai.yaml` 추가

### Fixed
- `scripts/score.py`가 완성도 5개·일치도 6개 항목 개수와 각 항목의 0~배점 범위를 검증하도록 수정

## 0.3.0

### Added
- `scripts/setup.sh` 추가: 런타임 데이터 디렉터리 부트스트랩
- `scripts/score.py` 추가: 점수 합산·등급 계산

## 0.2.0

### Added
- 완성도/일치도 점수표 각 항목에 채점 신호 기준 한 줄 추가
- 트리거 eval에 회고 작성(true), 블로그 구조 잡기(false) 경계 케이스 추가

### Changed
- description을 트리거 예시와 blogging 경계 안내 포함해 보강
- 점수표 항목/배점 정의 단일 출처를 `references/profile-template.md`로 위임
- README Test 명령에 "레포 루트에서 실행" 한정 명시

### Removed
- 본문 어디서도 쓰이지 않던 데이터 경로의 `outputs/` 항목 제거

## 0.1.0

### Added
- 허가된 문체 지문 추출, 프로필 완성도, 스타일 일치도 리포트 흐름 추가
- 사칭 방지와 위험한 대리 발화 중단 조건 추가
- 프로필 템플릿과 트리거 eval 정의 추가
