#!/usr/bin/env python3
"""Export static KB v1 (ru+en) from UnifiedFAQCatalog + LocalizationManager."""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPPORT_SWIFT = ROOT / "Screens" / "13_SupportScreen.swift"
LOCALIZATION_SWIFT = ROOT / "Core" / "Localization" / "LocalizationManager.swift"
OUT_DIR = ROOT / "docs" / "kb" / "kb_v1" / "documents"

FAQ_ENTRY_RE = re.compile(
    r'UnifiedFAQEntry\(\s*id:\s*"([^"]+)"[^)]*questionKey:\s*"([^"]+)"[^)]*answerKey:\s*"([^"]+)"[^)]*keywords:\s*\[([^\]]*)\]',
    re.DOTALL,
)
KW_RE = re.compile(r'"([^"]+)"')
DICT_LINE_RE = re.compile(r'^\s+"([^"]+)":\s*"(.*)",\s*$')


def parse_swift_dict_block(lines: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in lines:
        m = DICT_LINE_RE.match(line)
        if not m:
            continue
        key, raw = m.group(1), m.group(2)
        value = (
            raw.replace("\\n", "\n")
            .replace("\\t", "\t")
            .replace('\\"', '"')
            .replace("\\\\", "\\")
        )
        out[key] = value
    return out


def load_translations() -> tuple[dict[str, str], dict[str, str]]:
    text = LOCALIZATION_SWIFT.read_text(encoding="utf-8").splitlines()
    ru_lines: list[str] = []
    en_lines: list[str] = []
    section: str | None = None
    for line in text:
        if ".russian:" in line and "[" in line:
            section = "ru"
            continue
        if ".english:" in line and "[" in line:
            section = "en"
            continue
        if ".chinese:" in line and "[" in line:
            section = None
            continue
        if section == "ru":
            ru_lines.append(line)
        elif section == "en":
            en_lines.append(line)
    return parse_swift_dict_block(ru_lines), parse_swift_dict_block(en_lines)


def parse_faq_catalog() -> list[dict]:
    raw = SUPPORT_SWIFT.read_text(encoding="utf-8")
    entries = []
    for m in FAQ_ENTRY_RE.finditer(raw):
        eid, qkey, akey, kw_blob = m.groups()
        keywords = KW_RE.findall(kw_blob)
        entries.append(
            {"id": eid, "question_key": qkey, "answer_key": akey, "keywords": keywords}
        )
    return entries


def topic_for_faq_id(faq_id: str) -> str:
    if faq_id.startswith("faq_ai"):
        return "app_help"
    if "parental" in faq_id or "children" in faq_id or "gaming" in faq_id:
        return "parental"
    if "subscription" in faq_id or "tariff" in faq_id:
        return "tariff"
    if "e2ee" in faq_id or "data_safe" in faq_id:
        return "e2ee"
    return "security_faq"


def make_doc(
    *,
    doc_id: str,
    locale: str,
    topic: str,
    title: str,
    body: str,
    source: str,
    keywords: list[str] | None = None,
) -> dict:
    return {
        "id": doc_id,
        "locale": locale,
        "topic": topic,
        "title": title.strip(),
        "body": body.strip(),
        "source": source,
        "keywords": keywords or [],
        "kb_version": "kb_v1",
    }


def export_faq_entries(ru: dict[str, str], en: dict[str, str], catalog: list[dict]) -> list[dict]:
    docs: list[dict] = []
    for entry in catalog:
        topic = topic_for_faq_id(entry["id"])
        for locale, table in (("ru", ru), ("en", en)):
            q = table.get(entry["question_key"], "")
            a = table.get(entry["answer_key"], "")
            if not q and not a:
                continue
            docs.append(
                make_doc(
                    doc_id=f"{entry['id']}_{locale}",
                    locale=locale,
                    topic=topic,
                    title=q or entry["id"],
                    body=f"{q}\n\n{a}".strip(),
                    source="UnifiedFAQCatalog",
                    keywords=entry["keywords"] if locale == "ru" else [],
                )
            )
    return docs


def export_key_groups(
    ru: dict[str, str],
    en: dict[str, str],
    *,
    prefix: str,
    topic: str,
    source: str,
    title_suffix: str = "",
) -> list[dict]:
    docs: list[dict] = []
    for locale, table in (("ru", ru), ("en", en)):
        keys = sorted(k for k in table if k.startswith(prefix))
        if not keys:
            continue
        parts = []
        for k in keys:
            v = table[k].strip()
            if v:
                parts.append(f"### {k}\n{v}")
        if not parts:
            continue
        title = f"{prefix.rstrip('_')} {title_suffix}".strip()
        docs.append(
            make_doc(
                doc_id=f"{prefix.rstrip('_')}_{topic}_{locale}",
                locale=locale,
                topic=topic,
                title=title,
                body="\n\n".join(parts),
                source=source,
            )
        )
    return docs


def main() -> int:
    if not SUPPORT_SWIFT.is_file() or not LOCALIZATION_SWIFT.is_file():
        print("FAIL: missing source files", file=sys.stderr)
        return 1

    ru, en = load_translations()
    catalog = parse_faq_catalog()
    if not catalog:
        print("FAIL: no FAQ catalog entries parsed", file=sys.stderr)
        return 1

    docs: list[dict] = []
    docs.extend(export_faq_entries(ru, en, catalog))
    docs.extend(
        export_key_groups(ru, en, prefix="onboarding_page", topic="onboarding", source="LocalizationManager")
    )
    docs.extend(
        export_key_groups(
            ru,
            en,
            prefix="tariffs_",
            topic="tariff",
            source="LocalizationManager",
            title_suffix="(overview)",
        )
    )
    docs.extend(
        export_key_groups(
            ru,
            en,
            prefix="family_chat_e2ee",
            topic="e2ee",
            source="LocalizationManager",
        )
    )
    docs.extend(
        export_key_groups(
            ru,
            en,
            prefix="family_chat_legacy",
            topic="e2ee",
            source="LocalizationManager",
        )
    )
    # AI app_help single keys
    for key in ("faq_ai_how_works", "ai_assistant_subtitle", "ai_error_consent_required"):
        for locale, table in (("ru", ru), ("en", en)):
            q = table.get(key, "")
            a = table.get(f"{key}_answer", "") if key.startswith("faq_") else ""
            body = f"{q}\n\n{a}".strip() if a else q
            if not body:
                continue
            docs.append(
                make_doc(
                    doc_id=f"{key}_{locale}",
                    locale=locale,
                    topic="app_help",
                    title=q or key,
                    body=body,
                    source="LocalizationManager",
                )
            )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("*.json"):
        old.unlink()

    for doc in docs:
        path = OUT_DIR / f"{doc['id']}.json"
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "kb_version": "kb_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "locales": ["ru", "en"],
        "document_count": len(docs),
        "sources": ["UnifiedFAQCatalog", "LocalizationManager"],
        "topics": sorted({d["topic"] for d in docs}),
    }
    (OUT_DIR.parent / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    by_locale = {}
    for d in docs:
        by_locale[d["locale"]] = by_locale.get(d["locale"], 0) + 1
    print(f"OK: {len(docs)} documents -> {OUT_DIR}")
    print("by_locale:", by_locale)
    print("topics:", manifest["topics"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
