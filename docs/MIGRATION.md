# 이전 이름에서 업데이트하기

| 이전 이름 | 현재 호출명 |
|---|---|
| `good` (`trim`·`annotate` 통합), `.good` | `$.⚡good` |
| `wow`, `.wow` | `$.⚡wow` |
| `commit`, `.commit` | `$.⚡commit` |
| `context-review`, `won-context-review`, `.review` | `$.⚡review` |
| `mr`, `ship`, `won-ship`, `.ship` | `$.⚡ship` |
| `orbit`, `won-orbit`, `.orbit` | `$.🌈orbit` |
| `code-to-figma`, `won-code-to-figma`, `.code-to-figma` | `$.🌈code-to-figma` |
| `soul-extractor`, `won-soul-extractor`, `.soul-extractor` | `$.🌈soul-extractor` |

`won-code-visualizer`는 제거했습니다. `.⚡review`와 통합된 `.⚡ship`은 데일리함에 둡니다.

기존 설치에서는 새 이름을 배포한 뒤 이 저장소의 옛 설치본을 스킬 탐색 경로 밖에 백업해 중복 노출을 막습니다. 배포 스크립트는 저장소에서 사라진 스킬을 자동 삭제하지 않습니다. 별도 수정과 다른 출처의 스킬은 보존하고, 기존 심볼릭 링크는 새 저장 폴더를 가리키도록 갱신합니다.

이름 변경 후에도 `~/.orbit`의 조사·인증 기록, `~/.soul-extractor`의 프로필, `orbit/v2.4` 이슈 본문·fingerprint와 `ship:managed` 본문 표식은 유지합니다.

[README로 돌아가기](../README.md)
