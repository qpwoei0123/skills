# ship

`version: 1.0.0`

현재 작업을 다듬고 커밋한 뒤 새 Draft PR/MR을 만들거나 기존 Draft 본문을 갱신합니다. Codex 표시 이름은 **출항**입니다.

## Quick Start

```text
$ship
$ship 수정하지 말고 출항 계획만 보여줘.
$ship 기존 Draft에 이번 작업을 이어서 반영해줘.
```

기본 호출은 `good → commit → Draft 생성/갱신`을 완료합니다. 계획 요청이면 읽기 전용으로 제안합니다. `/ship`, `--go`, `-go`도 지원하며, 명시된 계획·범위 제한이 우선합니다.

정리할 코드나 새로 커밋할 변경이 없으면 해당 단계를 생략합니다. worktree가 깨끗해도 base보다 앞선 커밋이 있으면 리뷰 범위를 다듬고 필요한 경우에만 후속 커밋을 만듭니다.

현재 branch에 열린 Draft가 정확히 하나 있으면 기존 제목과 사용자 작성 본문을 보존하며 관리 블록만 갱신합니다. 진행 중 대상이나 원격 본문이 달라지면 덮어쓰지 않습니다.

## Structure

```text
ship/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── agents/openai.yaml
└── references/draft-update.md
```

`good`, `commit`, `mr`이 필요합니다. 기존 Draft 갱신 절차는 그 경로에서만 reference를 읽습니다.

## Test

```bash
python3 scripts/validate_skills.py --skill ship
```
