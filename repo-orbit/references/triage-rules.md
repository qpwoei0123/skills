# Triage Rules (override & 재검토용)

일반 실행에서는 SKILL.md Step 5의 인라인 기준만으로 충분하다.
이 파일은 **기준 override, 예외 처리, 재검토 트리거** 상황에서만 읽는다.

---

## Override 옵션

프롬프트에 명시적으로 지정하면 인라인 기준을 override한다.

| 옵션 | 기본값 | 예시 |
|------|--------|------|
| `--triage-min-impact` | 4 | `--triage-min-impact 3` |
| `--triage-min-urgency` | 3 | `--triage-min-urgency 2` |
| `--triage-min-score` | 3 | `--triage-min-score 2` |
| `--triage-allow-low-confidence` | false | `--triage-allow-low-confidence` |

override 사용 시 coverage-log에 `"triage_override": true`를 기록한다.

---

## 기준 재검토 트리거

아래 패턴이 3회 이상 반복되면 기준 재검토를 권고한다.

**기준이 너무 엄격한 방향 (이슈가 너무 적게 올라올 때):**
- **findings_issued = 0** 이 연속 3회: `min_impact` 또는 `min_urgency`를 낮추는 것을 검토
- **findings_skipped(low_actionability) > 50%** 가 연속 3회: next_step 품질 점검

**기준이 너무 관대한 방향 (이슈가 너무 많이 올라올 때):**
- **triage 스킵 없이 전량 통과** 가 연속 3회: `min_impact`를 높이거나 `min_urgency`를 높이는 것을 검토
- **findings_issued >= 4** 가 연속 3회: 동일 view에서 반복 발행되는 패턴인지 확인 후 `min_impact` 상향 검토

재검토는 coverage-log.json의 최근 실행 기록을 기준으로 판단한다.
기준 변경 시 coverage-log에 `"triage_calibration": "<방향>/<이유>"` 를 기록한다.

---

## 스킵 처리 상세 정책

### fingerprint update
- open 이슈의 fingerprint가 일치해도 triage 스킵하지 않는다.
- Step 6에서 제목/본문/automation label을 최신 `format_version`으로 update한다.
- closed 이슈도 reopen + update한다.
- 같은 `format_version`이어도 claim, evidence, next_step이 달라졌으면 최신 본문으로 갱신한다.

### low_confidence
- confidence == "low"이면 무조건 스킵한다.
- `--triage-allow-low-confidence` 옵션이 있을 때만 예외.
- low confidence finding은 result.json에 남기되 이슈화하지 않는다.

### low_actionability
- score 계산은 SKILL.md 채점 공식을 그대로 따른다. 재량 채점 없음.
- score 2점 이하 finding은 result.json에 남기되 이슈화하지 않는다.
