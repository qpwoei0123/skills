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
python3 scripts/validate_skills.py --skill won-orbit
python3 scripts/validate_skills.py --skill good
```

자동 검증:

- [scripts/validate_skills.py](scripts/validate_skills.py)
- [scripts/normalize_skill.py](scripts/normalize_skill.py)
- [.github/workflows/validate-skills.yml](.github/workflows/validate-skills.yml)

형식 검사와 함께 운영 코드 회귀 테스트를 실행합니다.

```bash
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 -m unittest discover -s 'skills/살짝무거움/won-orbit/scripts' -p 'test_*.py' -v
python3 -m unittest discover -s 'skills/살짝무거움/won-soul-extractor/scripts' -p 'test_*.py' -v
(cd 'skills/살짝무거움/won-code-to-figma' && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm ci && npm test && npm run smoke)
```

자동 수정 가능한 항목은 로컬에서 먼저 정규화할 수 있습니다.

```bash
python3 scripts/normalize_skill.py --skill good --check
python3 scripts/normalize_skill.py --skill good --write
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
python3 scripts/deploy_skills.py --skill good
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
    │   ├── good/                   # 동작 보존 코드 정리와 필요한 맥락 주석
    │   └── wow/                    # 설계 관점 재구상 스킬
    └── 살짝무거움/                 # 멀티스텝 워크플로
        ├── won-code-visualizer/        # 코드·아키텍처를 단일 HTML로 설명하는 시각화 스킬
        ├── won-context-review/         # 큰 PR/MR에서 고맥락 질문을 추리는 리뷰 스킬
        ├── won-ship/                   # 새 Draft 생성·기존 Draft 갱신까지 잇는 출항 워크플로
        ├── won-orbit/                  # 레포 점검/이슈 발행 워크플로 스킬
        ├── won-soul-extractor/         # 허가된 문체 지문 추출/변환 스킬
        └── won-code-to-figma/          # 웹 화면 → Figma 변환 스킬
```

## Accepted Skills

- `commit`: 현재 git diff를 분석해 적절한 커밋 단위와 한글 Conventional Commits 메시지로 커밋하는 스킬
- `mr`: 현재 브랜치의 커밋과 diff를 분석해 draft MR/PR을 계획하거나 생성하는 스킬
- `good`: 동작을 유지하면서 코드를 읽고 수정하기 쉽게 정리하고 필요한 맥락 주석을 남기는 스킬 (trim·annotate 통합)
- `wow`: 구현된 변경을 새 관점으로 다시 설계해 우아한 단순화안을 제안하는 스킬
- `won-orbit 🪐`: 요청한 관점으로 레포를 분석하고, 발행 요청이 있으면 근거가 확인된 기술 이슈를 생성·갱신하는 스킬
- `won-soul-extractor`: 문체 지문을 추출해 글을 작성·변환하고 요청하면 일치도를 점검하는 스킬
- `won-code-to-figma`: 구현된 웹 화면을 요청한 편집 구조와 디자인 시스템 연결에 맞춰 Figma로 옮기는 스킬
- `won-ship`: 현재 작업을 다듬고 주석·검증·커밋한 뒤 새 Draft를 만들거나 기존 Draft 본문을 갱신하는 출항 워크플로
- `won-context-review`: 큰 PR/MR과 관련 자료에서 사람이 답해야 할 고맥락 리뷰 질문만 근거와 함께 추리는 스킬
- `won-code-visualizer`: 코드·diff의 아키텍처와 실행·데이터·상태 흐름을 근거가 연결된 단일 HTML로 보여주는 스킬

## 추천 사용 흐름

필요한 작업을 골라 맡깁니다. 모든 단계를 거칠 필요는 없습니다.

```text
wow? → good? → commit? → mr?
재설계   코드·맥락 정리   로컬 이력   Draft 제출
```

```text
$wow 이 구조를 처음부터 다시 본다면 어떤 모델이 더 단순할까?
$good 현재 변경의 동작을 유지하면서 읽고 수정하기 쉽게 다듬어줘.
$good 이 분기가 필요한 이유만 주석으로 남겨줘. 코드는 그대로 둬.
$commit 변경분을 의미 단위로 나눠 커밋해줘.
$mr 현재 작업을 Draft PR/MR로 올려줘.
$won-ship 다듬고 커밋해 새 Draft를 만들거나 기존 Draft를 갱신해줘.
$won-context-review <PR/MR URL> 사람이 답해야 할 고맥락 질문만 추려줘.
$won-code-visualizer 이 기능의 요청부터 저장까지를 HTML로 보여줘.
$won-orbit . --view BUILD --dry-run
$won-orbit . --view SAFE --publish
$won-code-to-figma 현재 화면들을 새 Figma 파일에 편집 가능한 레이어로 옮겨줘.
$won-soul-extractor 이 글을 내 샘플의 문체로 다듬어줘.
```

`wow`는 기본 제안, `good`·`commit`·`mr`·`won-ship`은 기본 실행입니다. "계획만", "주석만", "기존 커밋만" 같은 제한을 우선합니다. 기존 `--go`, `-go`도 실행 표기로 지원하지만 실행을 위해 반드시 붙일 필요는 없습니다.

- "다듬고 필요한 주석도 남겨줘" → `good`이 코드와 맥락을 한 흐름에서 정리합니다.
- "커밋하고 PR까지 올려줘" → `mr`이 필요한 `commit`을 거쳐 Draft를 생성합니다.
- "출항해줘" → `won-ship`이 `good → commit`을 거쳐 새 Draft 생성 또는 기존 Draft 본문 갱신까지 이어갑니다.

## 데일리 스킬 1.0 전환

`trim`과 `annotate`를 `good`으로 통합했습니다. 기존 명시 호출은 `$good`과 `$good 주석만`으로 바꿉니다. 옛 이름의 호출 별칭은 제공하지 않습니다.

기본 호출의 계획·실행 의미가 달라졌으므로 미리보기는 "계획만"으로 명시합니다. `wow`에서 선택과 구현도 맡기면 같은 요청 안에서 구현을 이어갑니다.

기존 설치를 갱신할 때는 `good`, `wow`, `commit`, `mr`, `won-ship`을 함께 동기화합니다. `deploy_skills.py`는 저장소에서 사라진 이름을 자동 삭제하지 않습니다. 기존 설치본이 이 저장소의 trim·annotate인지 확인하고, 별도 수정이 있으면 보존한 뒤 스킬 탐색 경로 밖에 백업해 중복 선택을 막습니다. 다른 출처의 스킬은 이관 대상으로 삼지 않습니다.

## 워크플로 스킬 전환

`won-orbit`은 3.0, 나머지 `won-` 스킬은 2.0입니다. 근거·완료 조건은 유지하고 고정 인원·질문 수·화면 수별 모드·샘플 수·필수 점수표를 줄였습니다.

기본 `$won-orbit <repo>`는 분석입니다. 이슈 발행 자동화는 `--publish` 또는 발행 의도를 명시합니다. 기존 작업의 발행 권한은 유지하고 `--dry-run`은 payload만 준비하며 지속 메모리를 변경하지 않습니다. Codex UI 기본 프롬프트에는 발행 요청이 들어 있습니다. 본문은 `orbit/v2.4`를 사용하고 기존 fingerprint와 닫힌 이슈 처리 계약은 유지합니다.

Figma 변환은 화면 수와 관계없이 요청한 편집·DS 기준을 따릅니다. `won-soul-extractor`는 글을 먼저 완성하고 프로필 저장과 채점은 요청할 때 수행합니다. 각 스킬의 README에 실행 예시와 변경 이력이 있습니다.

## 무거운 스킬 이름

`살짝무거움`의 스킬은 호출명과 목록 표시명에 `won-`을 붙입니다. `won-`으로 검색하면 이 스킬들을 함께 찾을 수 있습니다. 데일리 스킬 이름은 그대로 사용합니다.

| 이전 호출명 | 현재 호출명 |
|---|---|
| `$ship` | `$won-ship` |
| `$orbit` | `$won-orbit` |
| `$context-review` | `$won-context-review` |
| `$code-visualizer` | `$won-code-visualizer` |
| `$code-to-figma` | `$won-code-to-figma` |
| `$soul-extractor` | `$won-soul-extractor` |

기존 명시 호출과 자동화 프롬프트는 새 이름으로 바꿉니다. 자연어 트리거와 실제 작업 범위는 유지합니다. `~/.orbit`의 조사·인증 기록, `~/.soul-extractor`의 프로필, 기존 HTML 저장 경로, 이슈 fingerprint와 Draft 본문 관리 표식은 이름 변경의 영향을 받지 않습니다.

설치할 때는 새 이름을 배포한 뒤 이 저장소에서 설치한 옛 이름을 스킬 탐색 경로 밖에 백업해 중복 노출을 막습니다. `deploy_skills.py`는 옛 이름을 자동 삭제하지 않습니다. 기존 설치를 가리키는 심볼릭 링크가 있으면 새 호출명과 목적지로 함께 갱신합니다.

## Release Flow

1. 새 스킬 초안을 저장소 밖에서 만든다.
2. 이 저장소로 가져와 표준 형식과 테스트를 맞춘다.
3. validator·unit test·`deploy_skills.py --check`를 실행한다.
4. `main`에 푸시한다.
5. CI를 통과한 소스를 `deploy_skills.py`로 설치본에 동기화한다.
