#!/usr/bin/env python3
"""Fail if the knowledge base can again answer with UI status strings."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "docs" / "kb" / "kb_v1"
DOCS = KB / "documents"
CURATED = KB / "curated"
CHUNKS = KB / "chunks.jsonl"

LOC_KEY_HEADING = re.compile(r"(?m)^#{1,6}\s*[a-z][a-z0-9_]{2,80}\s*$")
UI_MARKERS = (
    "could not decrypt",
    "message protection is still setting up",
    "secure chat is not set up",
    "setting up message protection",
    "setting up end-to-end encryption",
    "не удалось расшифровать",
    "защита сообщений ещё настраивается",
    "настраиваем защиту сообщений",
    "настраивается сквозное шифрование",
)
FORBIDDEN_PARENTS = (
    "family_chat_legacy_e2ee_en",
    "family_chat_legacy_e2ee_ru",
)


def main() -> int:
    errors: list[str] = []
    if not CHUNKS.is_file():
        print(f"FAIL: missing {CHUNKS}", file=sys.stderr)
        return 1

    chunks = []
    for line in CHUNKS.read_text(encoding="utf-8").split("\n"):
        if line.strip():
            chunks.append(json.loads(line))

    parents = {row["parent_id"] for row in chunks}
    for row in chunks:
        text = row.get("text") or ""
        if LOC_KEY_HEADING.search(text):
            errors.append(f"loc key heading in {row['chunk_id']}")
        low = text.lower()
        for marker in UI_MARKERS:
            if marker in low:
                errors.append(f"ui chrome {marker!r} in {row['chunk_id']}")
                break
        if row["parent_id"] in FORBIDDEN_PARENTS:
            errors.append(f"forbidden parent {row['parent_id']}")

    if not CURATED.is_dir():
        errors.append("missing curated/")
    else:
        for path in sorted(CURATED.glob("*.json")):
            doc = json.loads(path.read_text(encoding="utf-8"))
            doc_id = doc["id"]
            if doc_id not in parents:
                errors.append(f"curated {doc_id} missing from chunks")
                continue
            joined = "\n\n".join(
                row["text"] for row in chunks if row["parent_id"] == doc_id
            )
            if doc["body"].strip() not in joined and joined.strip() != doc["body"].strip():
                errors.append(f"curated {doc_id} body drifted from chunks")

    doc_ids = {p.stem for p in DOCS.glob("*.json")} if DOCS.is_dir() else set()
    missing_docs = parents - doc_ids
    if missing_docs:
        errors.append(f"chunks without documents: {sorted(missing_docs)[:5]}")

    if errors:
        print("FAIL")
        for err in errors:
            print(f" - {err}")
        return 1
    print(f"OK: {len(chunks)} chunks, curated synced, no UI chrome")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
