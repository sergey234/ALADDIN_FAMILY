#!/usr/bin/env python3
"""Patch child_study_*_page_2 — semantic journey stops (study.N → stop N)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "Core/Localization/LocalizationManager.swift"

# subject slug → study id (semantic stop)
SUBJECT_STOP: list[tuple[str, int, str, str]] = [
    ("russian", 1, "гигантская буква А танцует на словаре", "a giant letter A dances on a dictionary"),
    ("math", 2, "числа прыгают по кубикам-ступенькам", "numbers hop on cube steps"),
    ("world", 3, "глобус с зверями вокруг экватора", "a globe with animals around the equator"),
    ("history", 4, "рыцарь с факелом у старинной карты", "a knight with a torch by an old map"),
    ("geography", 5, "компас указывает на гору с флагом", "a compass points to a mountain with a flag"),
    ("biology", 6, "лист с каплей росы и жуком", "a leaf with dew and a beetle"),
    ("physics", 7, "маятник из светящихся шаров", "a pendulum of glowing balls"),
    ("chemistry", 8, "колбы с цветным паром в форме сердца", "flasks with colored steam shaped like a heart"),
    ("literature", 9, "книга открывается театральной сценой", "a book opens into a theater stage"),
    ("art", 10, "палитра превращается в радугу-крыло", "a palette turns into a rainbow wing"),
    ("sport", 11, "кроссовки оставляют след-звезду", "sneakers leave a star trail"),
    ("labor", 12, "молоток и гаечный ключ танцуют", "a hammer and wrench dance together"),
    ("social", 13, "рукопожатие на мосту дружбы", "a handshake on a friendship bridge"),
    ("ecology", 14, "дерево с птицами и синим небом внутри", "a tree with birds and blue sky inside"),
    ("traffic", 15, "светофор с улыбающимся пешеходом", "a traffic light with a smiling pedestrian"),
    ("health", 16, "зубная щётка как супергерой", "a toothbrush superhero"),
    ("finance", 17, "копилка-единорог с монетами", "a unicorn piggy bank with coins"),
    ("informatics", 18, "ноутбук с пиксельным замком", "a laptop with a pixel lock"),
    ("language", 19, "слова как воздушные шары разных языков", "words as balloons in many languages"),
    ("creativity", 20, "идея-лампочка рисует крылья", "a lightbulb idea paints wings"),
    ("project", 21, "пазл собирается в ракету", "puzzle pieces form a rocket"),
    ("research", 22, "лупа над записной книжкой со звёздами", "a magnifier over a starry notebook"),
    ("groupwork", 23, "команда муравьёв несёт мост", "ants carry a bridge together"),
    ("selfwork", 24, "будильник и чек-лист с галочками", "an alarm clock and checklist with ticks"),
    ("exams", 25, "календарь с мишенью на дате", "a calendar with a target on a date"),
    ("practice", 28, "ступени ведут к финишной ленте", "steps lead to a finish ribbon"),
    ("lab", 27, "пробирки светятся как фонарики", "test tubes glow like lanterns"),
    ("creative_project", 29, "мольберт с живым рисунком", "an easel with a living drawing"),
    ("portfolio", 30, "папка с сияющими работами", "a folder with shining works"),
]


def ru_line(stop: int, image: str) -> str:
    return f"Образ: {image}. Остановка {stop}. Повтор: сегодня, +1, +3, +7 дней."


def en_line(stop: int, image: str) -> str:
    return f"Image: {image}. Stop {stop}. Review: today, +1, +3, +7 days."


def patch_key(text: str, key: str, value: str, start: int = 0) -> tuple[str, bool]:
    needle = f'"{key}":'
    idx = text.find(needle, start)
    if idx == -1:
        return text, False
    line_end = text.find("\n", idx)
    text = text[:idx] + f'"{key}": "{value}",' + text[line_end:]
    return text, True


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    en_anchor = text.find('"child_mnemo_label_songs_kids": "Memory Songs"')
    if en_anchor == -1:
        raise SystemExit("EN anchor not found")

    for subject, stop, ru_img, en_img in SUBJECT_STOP:
        key = f"child_study_{subject}_page_2"
        text, ok = patch_key(text, key, ru_line(stop, ru_img), 0)
        if not ok:
            raise SystemExit(f"Missing RU key: {key}")

    head = text[:en_anchor]
    tail = text[en_anchor:]
    for subject, stop, ru_img, en_img in SUBJECT_STOP:
        key = f"child_study_{subject}_page_2"
        tail, ok = patch_key(tail, key, en_line(stop, en_img), 0)
        if not ok:
            raise SystemExit(f"Missing EN key: {key}")
    text = head + tail

    TARGET.write_text(text, encoding="utf-8")
    print(f"Patched {len(SUBJECT_STOP)} study page_2 keys with semantic stops (RU+EN)")


if __name__ == "__main__":
    main()
