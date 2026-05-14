# Action Matrix

| Category | Confidence | Labels | Comment | Close |
|---|---|---|---|---|
| DUP | high | `cleanup:duplicate` | 정본 링크와 중복 사유 | 사본만 조건부 close |
| DUP | medium | `cleanup:duplicate-candidate` | 사람 확인 요청 | no |
| BATCH | high | `cleanup:batch:<module>` | 묶음 목록과 공유 파일 | no |
| BATCH | medium | `cleanup:batch-candidate` | 가능성 및 공유 신호 | no |
| BATCH | low | `cleanup:batch:<module>` | 묶음 신호 | no |
| RESOLVED | high | `cleanup:auto-resolved` | 코드/PR 근거 | 조건부 close |
| RESOLVED | medium | `cleanup:likely-resolved` | 가능성 및 확인 요청 | no |
| RESOLVED | low | none | 로그만 | no |

## 라벨 색상

cleanup 계열 라벨은 회색 `cccccc`를 사용한다. orbit 발행 라벨의 파란색과 시각적으로 구분하기 위해서다.
