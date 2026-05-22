#!/usr/bin/env python3
"""Ingest kb_v1 chunks.jsonl into pgvector (aladdin_kb_v1)."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
CHUNKS_DEFAULT = BACKEND_ROOT / "docs" / "kb" / "kb_v1" / "chunks.jsonl"


def load_chunks(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunks", type=Path, default=CHUNKS_DEFAULT)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lexical-only", action="store_true", help="Skip embeddings API")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.chunks.is_file():
        print(f"FAIL: missing {args.chunks}", file=sys.stderr)
        return 1

    sys.path.insert(0, str(BACKEND_ROOT))
    from security.services import kb_embedding_client, kb_vector_store  # noqa: WPS433
    from security.services.kb_search_service import kb_search  # noqa: WPS433

    chunks = load_chunks(args.chunks)
    print(f"loaded {len(chunks)} chunks from {args.chunks}")

    if args.dry_run:
        return 0

    kb_vector_store.ensure_schema()
    embedded = 0
    lexical_only = args.lexical_only

    for i in range(0, len(chunks), args.batch_size):
        batch = chunks[i : i + args.batch_size]
        texts = [
            f"{c.get('title', '')}\n{c.get('text', '')}".strip() for c in batch
        ]
        vectors: list[list[float]] = []
        if not lexical_only:
            try:
                vectors = kb_embedding_client.embed_texts(texts)
            except Exception as exc:
                print(f"WARN: embeddings batch {i}: {exc}")
                if embedded == 0 and i == 0:
                    print("Falling back to lexical-only ingest (no vectors)")
                    lexical_only = True
                vectors = []

        for idx, chunk in enumerate(batch):
            vec = vectors[idx] if idx < len(vectors) else None
            if vec:
                kb_vector_store.upsert_chunk(
                    chunk_id=chunk["chunk_id"],
                    parent_id=chunk["parent_id"],
                    locale=chunk["locale"],
                    topic=chunk["topic"],
                    title=chunk.get("title", ""),
                    chunk_text=chunk.get("text", ""),
                    embedding=vec,
                    source=chunk.get("source", ""),
                    kb_version=chunk.get("kb_version", "kb_v1"),
                )
                embedded += 1
            else:
                kb_vector_store.upsert_chunk(
                    chunk_id=chunk["chunk_id"],
                    parent_id=chunk["parent_id"],
                    locale=chunk["locale"],
                    topic=chunk["topic"],
                    title=chunk.get("title", ""),
                    chunk_text=chunk.get("text", ""),
                    embedding=None,
                    source=chunk.get("source", ""),
                    kb_version=chunk.get("kb_version", "kb_v1"),
                )
                embedded += 1
        time.sleep(0.2)
        print(f"progress {min(i + args.batch_size, len(chunks))}/{len(chunks)}")

    total = kb_vector_store.count_chunks()
    with_vec = kb_vector_store.count_chunks()  # counts non-null embedding
    print(f"index aladdin_kb_v1 rows={total}")

    # Smoke retrieval
    for q, loc in [("Как работает AI-помощник?", "ru"), ("family chat E2EE", "en")]:
        hits = kb_search(q, locale=loc, top_k=3)
        print(f"kb_search({loc!r}) q={q[:40]!r} -> {len(hits)} hits")
        if hits:
            print(f"  top: {hits[0]['chunk_id']} score={hits[0]['score']:.3f}")

    return 0 if total > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
