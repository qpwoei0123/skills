# Comment Templates

스크립트는 아래 구조를 따르는 comment를 생성한다. 문구는 간결하게 유지한다.

## DUP

```text
orbit-cleanup: duplicate issue detected.
- issue: #<copy>
- canonical: #<canonical>
- confidence: high
- reason: <reason>
- action: label/comment/close
```

## BATCH

```text
orbit-cleanup: related issues can likely be handled as one batch.
- module: <module>
- related: #1, #2, #3
- shared files: <files>
- confidence: <confidence>
```

## RESOLVED

```text
orbit-cleanup: this issue appears to be resolved by current repository state.
- issue: #<number>
- confidence: high
- reason: <reason>
- action: label/comment/close
```

Close가 safety gate에 막히면 action은 `label/comment only`로 표시한다.
