# orbit-cleanup Orchestrator

리드 cleaner는 세 분류(DUP, BATCH, RESOLVED)를 하나의 action plan으로 병합한다.

## 책임

- orbit fingerprint footer가 있는 이슈만 대상으로 삼는다.
- `scripts/cleanup_issue.py`의 plan을 기준으로 라벨, comment, close 여부를 결정한다.
- DUP/BATCH/RESOLVED가 충돌하면 close 위험이 낮은 결정을 우선한다.
- BATCH는 작업 신호만 제공하고 close하지 않는다.
- orbit 본체의 view 분석 규칙, scoring, publish 계약은 수정하지 않는다.

## 출력

최종 보고에는 아래 값을 포함한다.

```json
{
  "scanned": 42,
  "dup": 3,
  "batch": 5,
  "resolved": 2,
  "closed": 0,
  "label_only": 10,
  "errors": 0
}
```

## 충돌 처리

- DUP와 RESOLVED가 동시에 high이면 DUP를 먼저 적용한다. 사본을 닫는 편이 더 좁은 변경이다.
- 보호 라벨 또는 최근 사람 코멘트가 있으면 close하지 않는다.
- `cleanup-log.json`의 점진 신뢰 조건이 충족되지 않으면 라벨과 comment만 남긴다.
