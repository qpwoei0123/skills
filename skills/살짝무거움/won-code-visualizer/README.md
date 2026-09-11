# won-code-visualizer

`version: 2.0.0`

스킬 목록에서 `won-`으로 찾을 수 있습니다. 명시 호출도 새 이름을 사용합니다.

대화·코드·diff의 관계를 근거가 연결된 단일 HTML로 설명합니다. Codex 표시 이름은 **won-code-visualizer**입니다.

## Quick Start

```text
$won-code-visualizer 방금 설명한 구조를 HTML로 보여줘.
$won-code-visualizer 이 기능의 요청부터 DB 저장까지를 한눈에 보여줘.
$won-code-visualizer 현재 diff의 구조 전후를 시각화해줘.
```

질문에 맞는 그림이나 표를 선택하고 확인됨·추론·미확정을 구분합니다. 템플릿과 노드 수는 출발점이며 필수 형식이 아닙니다. 소스가 없으면 제공된 설명 범위에서 작성하고 코드 미검증 상태를 표시합니다.

이미 존재하고 gitignored인 `.context`가 있으면 `.context/code-visualizer/<slug>.html`, 그 외에는 `/tmp/codex-code-visualizer/`에 저장합니다. 후속 수정은 이번 작업의 HTML에 반영합니다. 결과는 오프라인에서 열리며 application source를 바꾸지 않습니다. 브라우저 확인을 수행하지 못했으면 그 사실을 결과에 명시합니다.

## Structure

```text
won-code-visualizer/
├── SKILL.md, README.md, CHANGELOG.md
├── agents/openai.yaml
├── assets/
│   ├── explainer-shell.html    # 선택 가능한 기본 shell
│   └── patterns/              # 시각 문법 6종 fragment
└── references/
    ├── artifact-contract.md   # 근거 표식·escaping·CSP·접근성
    └── visual-grammar.md      # 질문별 선택표·권장 가독성
```

## Test

저장소 루트에서 형식을 검사합니다. 생성 HTML은 별도로 구조·오프라인·근거 연결을 확인합니다.

```bash
python3 scripts/validate_skills.py --skill won-code-visualizer
```
