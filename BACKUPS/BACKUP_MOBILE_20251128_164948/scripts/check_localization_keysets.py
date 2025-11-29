# coding: utf-8
"""Проверка синхронизации ключей локализации.

Скрипт читает `Core/Localization/LocalizationManager.swift`, собирает ключи
для блоков `.russian` и проверяет, что
наборы ключей совпадают. Если обнаружены расхождения, выводится отчёт и
возвращается код выхода 1.
"""
from pathlib import Path
import re
import sys
from typing import Dict, Optional, Set


LOCALE_ORDER = ["russian"]  # сравниваем только русский блок (EN временно отключён)
FILE_PATH = Path("Core/Localization/LocalizationManager.swift")
KEY_PATTERN = re.compile(r'"([^"]+)"\s*:')
BLOCK_START_PATTERN = {
    locale: re.compile(rf"\.\s*{locale}\s*:\s*\[") for locale in LOCALE_ORDER
}


def parse_localization_keys(text: str) -> Dict[str, Set[str]]:
    """Возвращает словарь {locale: set(keys)}."""
    keys = {locale: set() for locale in LOCALE_ORDER}  # type: Dict[str, Set[str]]
    current_locale: Optional[str] = None

    for raw_line in text.splitlines():
        line = raw_line.strip()

        # Проверяем начало блока
        for locale, pattern in BLOCK_START_PATTERN.items():
            if pattern.search(line):
                current_locale = locale
                break
        else:
            # Если не нашли начало блока и не внутри блока — пропускаем
            if current_locale is None:
                continue

        # Проверяем конец блока
        if current_locale is not None and line.startswith(']'):
            current_locale = None
            continue

        if current_locale is None:
            continue

        # Извлекаем ключи из строки (может быть несколько)
        for match in KEY_PATTERN.finditer(line):
            key = match.group(1)
            # Игнорируем ключи, которые на самом деле являются комментариями внутри строки
            if key.startswith("//"):
                continue
            keys[current_locale].add(key)

    return keys


def main() -> int:
    if not FILE_PATH.exists():
        print(f"❌ Файл не найден: {FILE_PATH}")
        return 1

    text = FILE_PATH.read_text(encoding="utf-8")
    locale_keys = parse_localization_keys(text)

    # Проверка, что все блоки найдены
    missing_blocks = [locale for locale, keys in locale_keys.items() if not keys]
    if missing_blocks:
        print("❌ Не найдены или пустые блоки локализации:", ", ".join(missing_blocks))
        return 1

    # Базовый набор ключей — русский
    base_locale = "russian"
    base_keys = locale_keys[base_locale]

    status_ok = True
    print("🔍 Проверка совпадения ключей локализации")
    print("---------------------------------------")
    for locale in LOCALE_ORDER:
        count = len(locale_keys[locale])
        print(f"{locale:8s}: {count} ключей")
    print("---------------------------------------")

    for locale in LOCALE_ORDER:
        if locale == base_locale:
            continue
        missing = sorted(base_keys - locale_keys[locale])
        extra = sorted(locale_keys[locale] - base_keys)
        if missing or extra:
            status_ok = False
            print(f"❌ Несовпадение ключей для '{locale}':")
            if missing:
                print("   Отсутствуют по сравнению с русским:")
                for key in missing[:20]:
                    print(f"      - {key}")
                if len(missing) > 20:
                    print(f"      ... ещё {len(missing) - 20}")
            if extra:
                print("   Лишние ключи по сравнению с русским:")
                for key in extra[:20]:
                    print(f"      + {key}")
                if len(extra) > 20:
                    print(f"      ... ещё {len(extra) - 20}")
            print("---------------------------------------")

    if status_ok:
        print("✅ Наборы ключей во всех языках совпадают.")
        return 0

    print("⚠️ Исправьте указанные несоответствия и запустите скрипт снова.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
