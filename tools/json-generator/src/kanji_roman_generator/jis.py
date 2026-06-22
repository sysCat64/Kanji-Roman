from __future__ import annotations

from typing import Any

JIS_STANDARD = "JIS X 0208"
JIS_KANJI_KU_START = 16
JIS_KANJI_KU_END = 84
JIS_TEN_START = 1
JIS_TEN_END = 94
JIS_LEVEL_ONE_LAST_KU = 47


def enumerate_jis_x0208_kanji() -> list[dict[str, Any]]:
    """Enumerate JIS X 0208 level 1 and 2 kanji in kuten order."""
    items: list[dict[str, Any]] = []

    for ku in range(JIS_KANJI_KU_START, JIS_KANJI_KU_END + 1):
        for ten in range(JIS_TEN_START, JIS_TEN_END + 1):
            try:
                char = bytes([ku + 0xA0, ten + 0xA0]).decode("euc_jp")
            except UnicodeDecodeError:
                continue

            code_point = f"{ord(char):04X}"
            items.append(
                {
                    "char": char,
                    "unicode": f"U+{code_point}",
                    "codePoint": code_point,
                    "jis": {
                        "standard": JIS_STANDARD,
                        "level": 1 if ku <= JIS_LEVEL_ONE_LAST_KU else 2,
                        "kuten": f"{ku:02d}-{ten:02d}",
                    },
                }
            )

    return items
