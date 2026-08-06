# code-visualizer

`version: 0.1.0`

코드와 diff를 직접 조사해 아키텍처·호출 흐름·상태·데이터·전후 변화를 한눈에 보는 단일 HTML로 만드는 스킬입니다. Codex 표시 이름은 **코드 한눈**입니다.

## Quick Start

```text
$code-visualizer로 방금 설명한 구조를 HTML로 한눈에 보여줘
$code-visualizer로 이 기능의 요청부터 DB 저장까지를 HTML로 보여줘
$code-visualizer로 현재 diff의 구조 전후를 한눈에 보여줘
```

기본 산출물은 git에서 무시되는 `.context/code-visualizer/<slug>.html`에 생성됩니다. 그런 경로가 없으면 `/tmp/codex-code-visualizer/`를 사용하며 application source는 수정하지 않습니다.

## Structure

```text
code-visualizer/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── agents/openai.yaml
├── assets/
│   ├── explainer-shell.html
│   └── patterns/              # 주 시각 문법 6종 복사 fragment
└── references/
    ├── artifact-contract.md
    └── visual-grammar.md
```

## Test

```bash
python3 scripts/validate_skills.py --skill code-visualizer
```
