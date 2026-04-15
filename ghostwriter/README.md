# ghostwriter

`version: 0.1.1`

사용자의 글쓰기 샘플을 분석해 문체와 사고 흐름을 프로필로 만들고, 그 프로필에 맞춰 새 글 초안을 작성하는 스킬입니다.

## Quick Start

```text
# 샘플 분석부터 시작
$ghostwriter

# 이미 프로필이 있으면 새 주제로 바로 작성
$ghostwriter "Redis 장애 회고 초안 써줘"
```

런타임 데이터는 스킬 폴더가 아니라 `~/.ghostwriter/` 아래에 저장합니다.

## Structure

```text
ghostwriter/
├── SKILL.md                         # 스킬 메인 규칙과 단계별 작성 흐름
├── README.md                        # 사용자용 빠른 시작 안내
├── CHANGELOG.md                     # 버전별 변경 이력
└── references/
    └── profile-template.md          # 글쓴이 프로필 작성 템플릿
```

## 검증 방법

자동 테스트 스크립트는 아직 없습니다.
대신 아래 순서로 수동 검증합니다.

1. 샘플 3개 이상으로 프로필 생성이 되는지 확인합니다.
2. `~/.ghostwriter/writer-profile.md`가 생성되는지 확인합니다.
3. 새 주제를 넣었을 때 프로필 기반 초안이 생성되는지 확인합니다.
4. 결과가 `~/.ghostwriter/outputs/` 아래에 저장되는지 확인합니다.
