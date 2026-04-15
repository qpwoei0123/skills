# skills

**주인장의 스킬을 표준화하고 운영하는 저장소**입니다.

이 레포의 기본 원칙은 간단합니다.

- 창작은 자유롭게 한다.
- 편입은 엄격하게 한다.
- 정식 스킬은 공통 형식을 맞춘다.
- 형식 검사는 사람이 아니라 레포가 수행한다.

## Install

```bash
npx skills add qpwoei0123/skills
```

## How This Repo Works

이 저장소에 들어오는 정식 스킬은 아래 기준을 따릅니다.

- `SKILL.md`는 실행 계약의 기준 문서
- `README.md`는 사람용 사용 설명서
- `CHANGELOG.md`는 버전별 변경 이력
- 버전의 `SSOT(단일 기준 원천)`는 `SKILL.md.metadata.version`

표준 문서:

- [docs/SKILL-STANDARD.md](/Users/han-won-yeong/Documents/project/skills/docs/SKILL-STANDARD.md)

## Admission Rule

보통 스킬은 밖에서 초안으로 만들고, 마음에 들면 이 저장소로 가져옵니다.
이 저장소에 편입되는 순간부터는 `accepted(정식 편입 상태)`로 보고 표준을 충족해야 합니다.

최소 필수 파일:

```text
skill-name/
├── SKILL.md
├── README.md
└── CHANGELOG.md
```

선택 구조:

- `agents/`
- `references/`
- `scripts/`
- `assets/`
- `INDEX.md`

## Validate

정식 스킬은 아래 스크립트로 검사합니다.

```bash
python3 scripts/validate_skills.py
```

특정 스킬만 검사할 수도 있습니다.

```bash
python3 scripts/validate_skills.py --skill orbit
python3 scripts/validate_skills.py --skill ghostwriter
```

자동 검증:

- [scripts/validate_skills.py](/Users/han-won-yeong/Documents/project/skills/scripts/validate_skills.py)
- [.github/workflows/validate-skills.yml](/Users/han-won-yeong/Documents/project/skills/.github/workflows/validate-skills.yml)

## Repository Structure

```text
skills/
├── docs/
│   └── SKILL-STANDARD.md           # 저장소 공통 스킬 표준
├── scripts/
│   └── validate_skills.py          # accepted 스킬 형식 검증 스크립트
├── .github/
│   └── workflows/
│       └── validate-skills.yml     # 스킬 형식 자동 검증 CI
├── orbit/                          # 레포 점검/이슈 발행 워크플로 스킬
└── ghostwriter/                    # 사용자 문체 기반 글쓰기 스킬
```

## Accepted Skills

- `orbit 🪐`: 레포를 요일별 관점으로 분석하고 finding을 이슈로 발행하는 워크플로 스킬
- `ghostwriter 👻`: 사용자 문체를 분석해 그 사람처럼 글을 써주는 글쓰기 스킬

## Next Step

이 레포에서 다음으로 이어질 작업은 보통 아래 순서입니다.

1. 새 스킬 초안을 밖에서 만든다.
2. 이 저장소로 가져와 표준 형식에 맞춘다.
3. `validate_skills.py`를 통과시킨다.
4. changelog를 갱신하고 커밋한다.
