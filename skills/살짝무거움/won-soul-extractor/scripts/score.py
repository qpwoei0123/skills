#!/usr/bin/env python3
"""문체 점수표 항목 점수를 받아 총점과 등급을 재현 가능하게 계산한다.

완성도 항목 합과 일치도 항목 합은 모두 100점 만점이라 총점이 곧 백분율이다.
사용 예:
  python3 score.py completeness 16 14 24 8 15
  python3 score.py match 17 16 18 17 8 8
"""
import sys

GRADE = [
    (90, "바로 변환 가능"),
    (75, "사용 가능, 일부 어색함 가능"),
    (60, "짧은 글만 권장"),
    (0, "샘플 추가 요청"),
]

SCORE_ITEMS = {
    "completeness": (
        ("샘플 양", 20),
        ("유형 다양성", 20),
        ("문체 지문 선명도", 30),
        ("금지 표현 근거", 15),
        ("최신성", 15),
    ),
    "match": (
        ("어휘", 20),
        ("문장 리듬", 20),
        ("구조", 20),
        ("사고 흐름", 20),
        ("금지 표현 회피", 10),
        ("자연스러움", 10),
    ),
}


def main(argv):
    if not argv or argv[0] not in SCORE_ITEMS:
        print("usage: score.py {completeness|match} <항목점수>...", file=sys.stderr)
        return 2
    kind = argv[0]
    items = SCORE_ITEMS[kind]
    if len(argv[1:]) != len(items):
        print(
            f"[error] {kind} 점수는 {len(items)}개가 필요합니다 "
            f"(받음: {len(argv[1:])}개).",
            file=sys.stderr,
        )
        return 2
    try:
        scores = [int(x) for x in argv[1:]]
    except ValueError:
        print("[error] 항목 점수는 정수여야 합니다.", file=sys.stderr)
        return 2

    for score, (name, cap) in zip(scores, items):
        if not 0 <= score <= cap:
            print(f"[error] {name} 점수는 0~{cap} 범위여야 합니다: {score}", file=sys.stderr)
            return 2

    total = sum(scores)
    if kind == "completeness":
        label = next(text for cut, text in GRADE if total >= cut)
        print(f"프로필 완성도: {total}% — {label}")
    else:
        print(f"스타일 일치도: {total}%")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
