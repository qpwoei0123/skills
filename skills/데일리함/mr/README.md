# mr

`version: 1.0.1`

요청한 작업을 push하고 저장소 관례에 맞는 GitHub Draft PR 또는 GitLab Draft MR을 만듭니다.

## Quick Start

```text
$mr 현재 작업을 Draft PR로 올려줘.
$mr 기존 커밋만 MR로 올려줘.
$mr 생성하지 말고 제목과 본문만 준비해줘.
```

`$mr`, `/mr`은 기본적으로 제출까지 수행하고 `--go`, `-go`도 지원합니다. "계획만" 같은 명시적 제한이 우선합니다.

현재 작업의 미커밋 변경을 포함하는 요청이면 `commit`을 거쳐 제출합니다. 기존 커밋만 지정하면 남은 변경을 포함하지 않습니다. 범위가 명확하면 A/B 선택을 다시 묻지 않습니다.

인증된 gh/glab과 HTTPS 경로를 우선합니다. 같은 source/head의 열린 요청은 중복 생성하지 않고 URL을 보고하며, 기존 Draft 본문 갱신은 `won-ship`이 맡습니다.

## Structure

```text
mr/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── agents/openai.yaml
├── evals/trigger-eval.json
├── references/branch-conventions.md
├── references/review-format.md
└── scripts/preflight.sh
```

## Scripts

대상 git 저장소에서 읽기 전용 사전 점검을 실행합니다.

```bash
bash <스킬 디렉터리>/scripts/preflight.sh
```

## Test

```bash
python3 scripts/validate_skills.py --skill mr
```
