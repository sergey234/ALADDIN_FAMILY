#!/usr/bin/env python3
"""Chunk kb_v1 documents (~300-800 tokens) for RAG ingest."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs" / "kb" / "kb_v1" / "documents"
OUT_PATH = ROOT / "docs" / "kb" / "kb_v1" / "chunks.jsonl"

# ~4 chars per token (ru/en mixed heuristic)
MIN_CHARS = 300 * 4
MAX_CHARS = 800 * 4
TARGET_CHARS = 500 * 4


def split_paragraphs(text: str) -> list[str]:
    parts = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    if parts:
        return parts
    return [text.strip()] if text.strip() else []


def chunk_body(doc_id: str, body: str) -> list[str]:
    paragraphs = split_paragraphs(body)
    chunks: list[str] = []
    buf: list[str] = []
    buf_len = 0

    def flush() -> None:
        nonlocal buf, buf_len
        if buf:
            chunks.append("\n\n".join(buf))
            buf = []
            buf_len = 0

    for para in paragraphs:
        plen = len(para)
        if plen > MAX_CHARS:
            flush()
            for i in range(0, plen, TARGET_CHARS):
                chunks.append(para[i : i + TARGET_CHARS])
            continue
        if buf_len + plen + 2 > MAX_CHARS and buf:
            flush()
        buf.append(para)
        buf_len += plen + 2
        if buf_len >= TARGET_CHARS:
            flush()

    flush()
    if not chunks and body.strip():
        chunks = [body.strip()]
    return chunks


def main() -> int:
    if not DOCS_DIR.is_dir():
        print(f"FAIL: missing {DOCS_DIR}", file=sys.stderr)
        return 1

    rows: list[dict] = []
    for path in sorted(DOCS_DIR.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        parts = chunk_body(doc["id"], doc.get("body", ""))
        for idx, text in enumerate(parts):
            if len(text) < 40:
                continue
            rows.append(
                {
                    "chunk_id": f"{doc['id']}__c{idx:02d}",
                    "parent_id": doc["id"],
                    "locale": doc["locale"],
                    "topic": doc["topic"],
                    "title": doc.get("title", ""),
                    "text": text,
                    "kb_version": doc.get("kb_version", "kb_v1"),
                    "source": doc.get("source", ""),
                }
            )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"OK: {len(rows)} chunks -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
