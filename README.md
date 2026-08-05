```
                                    █████    ████     
    ███   █      ███               ██   █  ███  █     
 ████ ██  █       █                   █               
 █        █   ██  █   █       ██      ███████         
 █        █ ██    █   █       ██                ███   
 ██████   ██      █   █       █     ██████      █ ████
      ██  ███     █   █       █     █           █    █
       █  █  ██   █   █       █     ██████      ██████
█      █  █    █  █   █       █          █            
███████   █      ███  ██████  ████████████                             
```

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

- `agents/` (`openai.yaml` 제품 메타데이터 포함)
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
python3 scripts/validate_skills.py --skill trim
```

자동 검증:

- [scripts/validate_skills.py](scripts/validate_skills.py)
- [scripts/normalize_skill.py](scripts/normalize_skill.py)
- [.github/workflows/validate-skills.yml](.github/workflows/validate-skills.yml)

형식 검사와 함께 운영 코드 회귀 테스트를 실행합니다.

```bash
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 -m unittest discover -s 'skills/살짝무거움/orbit/scripts' -p 'test_*.py' -v
python3 -m unittest discover -s 'skills/살짝무거움/soul-extractor/scripts' -p 'test_*.py' -v
(cd 'skills/살짝무거움/code-to-figma' && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm ci && npm test && npm run smoke)
```

자동 수정 가능한 항목은 로컬에서 먼저 정규화할 수 있습니다.

```bash
python3 scripts/normalize_skill.py --skill trim --check
python3 scripts/normalize_skill.py --skill trim --write
```

기본 운영 흐름은 `main` push 기준입니다.

- 사람이 스킬을 `main`에 푸시한다.
- CI가 형식을 검사한다.
- 자동 수정 가능한 오류만 있으면 스킬 이름 기준 normalize 브랜치를 만들고 PR을 올린다.
- 사용자는 normalize PR만 머지하면 된다.

## Deploy

실제 세션이 로드하는 것은 레포가 아니라 배포 디렉터리(`~/.agents/skills`)입니다.
스킬을 고친 뒤 동기화하지 않으면 개선이 세션에 반영되지 않습니다.

```bash
python3 scripts/deploy_skills.py             # validate 통과 시 전체 동기화
python3 scripts/deploy_skills.py --skill trim
python3 scripts/deploy_skills.py --check     # 버전과 실제 파일 내용 차이 확인
```

배포는 먼저 임시 디렉터리에 복사·검증한 뒤 교체하므로, 복사나 검증이 실패해도 기존 설치본을 유지합니다.

## Repository Structure

```text
.
├── docs/
│   └── SKILL-STANDARD.md           # 저장소 공통 스킬 표준
├── scripts/
│   ├── validate_skills.py          # accepted 스킬 형식 검증 스크립트
│   └── deploy_skills.py            # 설치본 검증·동기화 스크립트
├── templates/
│   └── skill/                      # README/CHANGELOG 생성 템플릿
├── .github/
│   └── workflows/
│       └── validate-skills.yml     # 스킬 형식 자동 검증 CI
└── skills/                         # 정식 스킬 (사용 무게 기준 카테고리)
    ├── 데일리함/                   # 가벼운 일상 도구
    │   ├── commit/                 # git diff 기반 커밋 계획/실행 스킬
    │   ├── mr/                     # draft MR/PR 계획/생성 스킬
    │   ├── annotate/               # 작업 관련 로직 주석 정리 스킬
    │   ├── trim/                   # diff 군더더기 축소·중복 엮기 스킬 (weave 흡수)
    │   └── wow/                    # 설계 관점 재구상 스킬
    └── 살짝무거움/                 # 멀티스텝 워크플로
        ├── context-review/         # 큰 PR/MR에서 고맥락 질문을 추리는 리뷰 스킬
        ├── ship/                   # 정리부터 Draft PR/MR까지 잇는 출항 워크플로
        ├── orbit/                  # 레포 점검/이슈 발행 워크플로 스킬
        ├── soul-extractor/         # 허가된 문체 지문 추출/변환 스킬
        └── code-to-figma/          # 웹 화면 → Figma 변환 스킬
```

## Accepted Skills

- `commit`: 현재 git diff를 분석해 적절한 커밋 단위와 한글 Conventional Commits 메시지로 커밋하는 스킬
- `mr`: 현재 브랜치의 커밋과 diff를 분석해 draft MR/PR을 계획하거나 생성하는 스킬
- `annotate`: 현재 작업과 관련된 로직을 짧은 한글 주석으로 정리하는 스킬
- `trim`: 이미 구현된 diff의 동작을 유지하면서 군더더기를 덜어내고 흩어진 중복·패턴을 엮는 스킬 (weave 흡수 통합)
- `wow`: 구현된 변경을 새 관점으로 다시 설계해 우아한 단순화안을 제안하는 스킬
- `orbit 🪐`: 레포를 요일별 관점으로 분석하고 finding을 이슈로 발행하는 워크플로 스킬
- `soul-extractor`: 허가된 글 샘플에서 문체 지문을 추출하고 스타일 일치도를 점검하는 스킬
- `code-to-figma`: 구현된 웹 화면(URL)을 Figma로 옮기는 스킬 — 단일 화면은 디자인 시스템 바인딩 편집 레이어, 여러 화면은 픽셀 캡처 그리드
- `ship`: 현재 작업을 다듬고 주석·검증·커밋한 뒤 Draft PR/MR까지 한 번에 만드는 출항 워크플로
- `context-review`: 큰 PR/MR과 관련 자료에서 사람이 답해야 할 고맥락 리뷰 질문만 근거와 함께 추리는 스킬

## 추천 사용 흐름

아래는 주인장의 추천 조합일 뿐 필수 파이프라인이 아닙니다. 필요한 스킬 하나만 쓰거나 중간 단계를 건너뛰어도 됩니다.

```text
wow? → trim? → annotate? → commit? → mr?
재구상   코드 정리   맥락 주석     로컬 이력    원격 리뷰
```

`?`는 필요할 때만 선택한다는 뜻입니다.

이렇게 요청하면 각 스킬의 역할이 선명합니다.

```text
/wow 이 구조를 처음부터 다시 설계한다면 어떤 모델이 더 단순할까?
/trim --go 현재 변경의 동작을 유지하면서 군더더기와 중복을 줄여줘
/annotate --go 최종 diff에서 코드만으로 안 보이는 이유만 주석으로 남겨줘
/commit --go 변경분을 의미 단위로 나눠 커밋해줘
/mr --go 현재 브랜치를 draft PR/MR로 올려줘
$ship --go 현재 작업을 다듬고 커밋해 Draft PR/MR까지 출항시켜줘
$context-review <PR/MR URL> 이 변경에서 사람이 답해야 할 고맥락 질문만 추려줘
```

복합 요청은 다음 스킬이 전체 흐름을 맡습니다.

- "변경분을 다듬고 필요한 주석도 남겨줘" → `trim`이 수정·검증한 뒤 `annotate`가 최종 diff에 주석을 남김
- "커밋하고 PR까지 올려줘" → `mr`이 전체 흐름을 맡고 `commit`을 먼저 실행한 뒤 push·draft 리뷰 요청을 이어감
- "다듬고 주석·커밋해서 Draft까지 한 번에 올려줘" → `ship`이 전체 흐름을 맡고 `trim → annotate → commit → mr`을 순서대로 실행함

## Release Flow

1. 새 스킬 초안을 저장소 밖에서 만든다.
2. 이 저장소로 가져와 표준 형식과 테스트를 맞춘다.
3. validator·unit test·`deploy_skills.py --check`를 실행한다.
4. `main`에 푸시한다.
5. CI를 통과한 소스를 `deploy_skills.py`로 설치본에 동기화한다.
