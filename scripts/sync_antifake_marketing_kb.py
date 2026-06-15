#!/usr/bin/env python3
"""G-02 — sync antifake marketing copy to kb_v1 + landing cms."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LM = ROOT / "Core/Localization/LocalizationManager.swift"
KB = ROOT / "docs/kb/kb_v1/documents"
LANDING_FAQ = ROOT / "landing/cms/faq.json"
COPY_MD = ROOT / "docs/marketing/ANTIFAKE_LANDING_COPY.md"


def _parse_loc() -> tuple[dict[str, str], dict[str, str]]:
    text = LM.read_text(encoding="utf-8")
    out: dict[str, dict[str, str]] = {}

    def slice_block(marker: str, nxt: str | None) -> str:
        anchor = text.find("var translations:")
        m = re.search(rf"{re.escape(marker)}:\s*\[", text[anchor:])
        if not m:
            raise RuntimeError(marker)
        start = anchor + m.end()
        if nxt:
            n = re.search(rf"{re.escape(nxt)}:\s*\[", text[start:])
            end = start + n.start() if n else len(text)
        else:
            end = len(text)
        return text[start:end]

    for marker, nxt in ((".russian", ".english"), (".english", ".chinese")):
        chunk = slice_block(marker, nxt)
        d: dict[str, str] = {}
        for km in re.finditer(r'"([^"]+)":\s*"((?:\\.|[^"\\])*)"', chunk):
            d[km.group(1)] = bytes(km.group(2), "utf-8").decode("unicode_escape")
        out[marker] = d
    return out[".russian"], out[".english"]


def _write_kb(doc_id: str, locale: str, title: str, body: str, keywords: list[str]) -> None:
    KB.mkdir(parents=True, exist_ok=True)
    path = KB / f"{doc_id}_{locale}.json"
    data = {
        "id": f"{doc_id}_{locale}",
        "locale": locale,
        "topic": "antifake_marketing",
        "title": title,
        "body": body,
        "source": "sync_antifake_marketing_kb",
        "keywords": keywords,
        "kb_version": "kb_v1",
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"updated {path.name}")


def main() -> None:
    ru, en = _parse_loc()
    scope = (ROOT / "docs/ANTIFAKE_CALLS_PRODUCT_SCOPE.md").read_text(encoding="utf-8")
    copy_md = COPY_MD.read_text(encoding="utf-8") if COPY_MD.is_file() else ""

    for locale, loc in ("ru", ru), ("en", en):
        title = loc.get("antifake_hub_title", "Antifake")
        body = "\n\n".join(
            [
                loc.get("antifake_hub_subtitle", ""),
                loc.get("antifake_premium_gate_honest_body", ""),
                loc.get("antifake_premium_gate_bullet_1", ""),
                loc.get("antifake_premium_gate_bullet_2", ""),
                loc.get("antifake_premium_gate_bullet_3", ""),
                loc.get("privacy_policy_section_antifake_content_5", ""),
                "---",
                scope[:1200],
            ]
        )
        _write_kb(
            "antifake_marketing_honest",
            locale,
            title,
            body,
            ["antifake", "звонки" if locale == "ru" else "calls", "call directory"],
        )

    _write_kb(
        "antifake_landing_copy",
        "ru",
        "Antifake landing copy",
        copy_md,
        ["landing", "marketing", "antifake"],
    )
    _write_kb(
        "antifake_landing_copy",
        "en",
        "Antifake landing copy",
        copy_md,
        ["landing", "marketing", "antifake"],
    )

    faq_entries = []
    if LANDING_FAQ.is_file():
        faq_entries = json.loads(LANDING_FAQ.read_text(encoding="utf-8"))

    new_entries = [
        {
            "question": "Слушает ли ALADDIN все мои звонки?",
            "answer": (
                "Нет. iOS не даёт доступ к разговору по SIM. Вы сами загружаете запись после звонка "
                "или включаете метки Call Directory по синхронизированному списку номеров."
            ),
        },
        {
            "question": "Чем Antifake отличается от Truecaller?",
            "answer": (
                "Мы не собираем глобальную телефонную книгу. Семейная проверка контента по вашему "
                "запросу и метки из базы ALADDIN — без сбора контактов."
            ),
        },
    ]
    existing_q = {e.get("question") for e in faq_entries}
    for entry in new_entries:
        if entry["question"] not in existing_q:
            faq_entries.append(entry)
            print(f"landing faq + {entry['question'][:40]}...")
    LANDING_FAQ.write_text(json.dumps(faq_entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
