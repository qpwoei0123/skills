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
- `description`은 `(vx.y.z)` 버전 접두사로 시작하며, README 표기와 함께 normalize가 SSOT에 동기화

표준 문서:

- [docs/SKILL-STANDARD.md](docs/SKILL-STANDARD.md)

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
- `evals/`
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

- [scripts/validate_skills.py](scripts/validate_skills.py)
- [scripts/normalize_skill.py](scripts/normalize_skill.py)
- [.github/workflows/validate-skills.yml](.github/workflows/validate-skills.yml)

자동 수정 가능한 항목은 로컬에서 먼저 정규화할 수 있습니다.

```bash
python3 scripts/normalize_skill.py --skill ghostwriter --check
python3 scripts/normalize_skill.py --skill ghostwriter --write
```

기본 운영 흐름은 `main` push 기준입니다.

- 사람이 스킬을 `main`에 푸시한다.
- CI가 형식을 검사한다.
- 자동 수정 가능한 오류만 있으면 스킬 이름 기준 normalize 브랜치를 만들고 PR을 올린다.
- 사용자는 normalize PR만 머지하면 된다.

## Repository Structure

```text
skills/
├── docs/
│   └── SKILL-STANDARD.md           # 저장소 공통 스킬 표준
├── scripts/
│   └── validate_skills.py          # accepted 스킬 형식 검증 스크립트
├── templates/
│   └── skill/                      # README/CHANGELOG 생성 템플릿
├── .github/
│   └── workflows/
│       └── validate-skills.yml     # 스킬 형식 자동 검증 CI
├── commit/                         # git diff 기반 커밋 계획/실행 스킬
├── mr/                             # draft MR/PR 계획/생성 스킬
├── annotate/                       # 작업 관련 로직 주석 정리 스킬
├── trim/                           # diff 기반 코드 단순화 스킬
├── weave/                          # 분산된 코드 응집 스킬
├── wow/                            # 설계 관점 재구상 스킬
├── orbit/                          # 레포 점검/이슈 발행 워크플로 스킬
└── soul-extractor/                 # 허가된 문체 지문 추출/변환 스킬
```

## Accepted Skills

- `commit`: 현재 git diff를 분석해 적절한 커밋 단위와 한글 Conventional Commits 메시지로 커밋하는 스킬
- `mr`: 현재 브랜치의 커밋과 diff를 분석해 draft MR/PR을 계획하거나 생성하는 스킬
- `annotate`: 현재 작업과 관련된 로직을 짧은 한글 주석으로 정리하는 스킬
- `trim`: 이미 구현된 diff의 동작을 유지하면서 코드량과 불필요한 복잡도를 줄이는 스킬
- `weave`: 흩어진 코드와 패턴을 같은 이유로 변하는 단위로 엮는 스킬
- `wow`: 구현된 변경을 새 관점으로 다시 설계해 우아한 단순화안을 제안하는 스킬
- `orbit 🪐`: 레포를 요일별 관점으로 분석하고 finding을 이슈로 발행하는 워크플로 스킬
- `soul-extractor`: 허가된 글 샘플에서 문체 지문을 추출하고 스타일 일치도를 점검하는 스킬

## Next Step

이 레포에서 다음으로 이어질 작업은 보통 아래 순서입니다.

1. 새 스킬 초안을 밖에서 만든다.
2. 이 저장소로 가져와 표준 형식에 맞춘다.
3. `main`에 푸시한다.
4. CI가 실패하면 자동 normalize PR이 생성될 수 있다.
5. normalize PR을 머지한다.
6. `validate_skills.py`가 다시 통과하는지 확인한다.
