# View Rotation (편중 경고 & 복수 view 실행)

일반 실행에서는 SKILL.md Step 2의 기본 순서로 충분하다.
이 파일은 **편중 감지, 복수 view 실행, 강제 지정 세부 동작** 상황에서만 읽는다.

---

## 편중 경고 기준

coverage-log를 집계해 아래 조건이 감지되면 경고를 출력한다. 실행은 멈추지 않는다.

| 조건 | 경고 메시지 |
|------|-------------|
| 특정 view가 전체 실행의 40% 이상 | `[warn] view 편중: {view_id} {n}회 ({pct}%)` |
| 어떤 view가 14일 이상 미사용 | `[warn] view 미사용: {view_id} 마지막 사용 {n}일 전` |
| 7회 연속 동일 view | `[warn] view 고착: {view_id} 연속 {n}회` |

---

## 복수 View 실행

`--multi-view 3` 처럼 지정하면 한 번 실행에 여러 view를 순서대로 처리한다.

**view 선택 순서:** coverage-log 기준 가장 오래 실행되지 않은 view부터 N개 선택 (LRU 순).
요일 기반 자동 배정과 무관하다. `--multi-view SAFE,DEP,OPS` 처럼 명시 지정도 가능하다.

- 각 view는 독립적으로 Step 3~6을 실행한다.
- coverage-log에는 각 view를 별도 entry로 기록한다.
- triage 기준은 view마다 동일하게 적용한다.
- 발행 실패가 있어도 나머지 view는 계속 진행한다.

---

## 강제 지정 세부 동작

`--focus-view OPS` 또는 `--focus-view "운영 관측성"` 으로 지정.

- 강제 지정이 있으면 요일 기반 자동 배정을 무시하고 지정된 view를 사용한다.
- Step 1은 날짜·요일 확인만 하고 view 선택은 강제 지정값을 그대로 쓴다. 요일과 view가 다르더라도 오류가 아니다.
- coverage-log에 `"forced": true`로 기록한다.
- 강제 지정이 연속 3회 이상이면 `[warn] 강제 지정 반복: 자동 로테이션을 확인하세요` 경고.

---

## View별 우선순위 가중치 (선택적)

기본은 순수 LRU(가장 오래된 view 우선)이지만, 아래 가중치를 coverage-log에 명시하면 선택에 반영된다.

```json
"view_weights": {
  "SAFE":  1.2,
  "ARCH":  1.0,
  "DEP":   1.0,
  "BUILD": 1.0,
  "DATA":  1.0,
  "OPS":   1.0,
  "DOC":   0.8
}
```

가중치 > 1.0 이면 해당 view가 동률일 때 우선 선택된다.
가중치 < 1.0 이면 동률일 때 후순위로 밀린다.
기본값은 모두 1.0.
