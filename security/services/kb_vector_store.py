# -*- coding: utf-8 -*-
"""pgvector store for static KB index aladdin_kb_v1."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from security.services.kb_embedding_client import KB_EMBEDDING_DIM

logger = logging.getLogger(__name__)

KB_INDEX_NAME = "aladdin_kb_v1"
_SCHEMA_READY = False


def _engine():
    from app.database.database import engine  # type: ignore

    return engine


def ensure_schema() -> None:
    global _SCHEMA_READY
    if _SCHEMA_READY:
        return
    ddl = f"""
    CREATE TABLE IF NOT EXISTS aladdin_kb_chunks (
        chunk_id VARCHAR(160) PRIMARY KEY,
        parent_id VARCHAR(160) NOT NULL,
        kb_version VARCHAR(32) NOT NULL DEFAULT 'kb_v1',
        locale VARCHAR(8) NOT NULL,
        topic VARCHAR(64) NOT NULL,
        title TEXT,
        chunk_text TEXT NOT NULL,
        source VARCHAR(64),
        embedding vector({KB_EMBEDDING_DIM}),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    CREATE INDEX IF NOT EXISTS idx_aladdin_kb_chunks_locale_topic
        ON aladdin_kb_chunks (locale, topic);
    CREATE INDEX IF NOT EXISTS idx_aladdin_kb_chunks_kb_version
        ON aladdin_kb_chunks (kb_version);
    """
    with _engine().begin() as conn:
        conn.execute(text(ddl))
        # HNSW index — may already exist
        conn.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_aladdin_kb_chunks_embedding_hnsw
                ON aladdin_kb_chunks
                USING hnsw (embedding vector_cosine_ops)
                """
            )
        )
    _SCHEMA_READY = True
    logger.info("kb_vector_store schema ready index=%s", KB_INDEX_NAME)


def _vector_literal(vec: List[float]) -> str:
    return "[" + ",".join(f"{x:.8f}" for x in vec) + "]"


def upsert_chunk(
    *,
    chunk_id: str,
    parent_id: str,
    locale: str,
    topic: str,
    title: str,
    chunk_text: str,
    embedding: Optional[List[float]] = None,
    source: str = "",
    kb_version: str = "kb_v1",
) -> None:
    ensure_schema()
    if embedding is not None:
        sql = text(
            """
            INSERT INTO aladdin_kb_chunks (
                chunk_id, parent_id, kb_version, locale, topic, title, chunk_text, source, embedding, updated_at
            ) VALUES (
                :chunk_id, :parent_id, :kb_version, :locale, :topic, :title, :chunk_text, :source,
                CAST(:embedding AS vector), NOW()
            )
            ON CONFLICT (chunk_id) DO UPDATE SET
                parent_id = EXCLUDED.parent_id,
                kb_version = EXCLUDED.kb_version,
                locale = EXCLUDED.locale,
                topic = EXCLUDED.topic,
                title = EXCLUDED.title,
                chunk_text = EXCLUDED.chunk_text,
                source = EXCLUDED.source,
                embedding = EXCLUDED.embedding,
                updated_at = NOW()
            """
        )
        params = {
            "chunk_id": chunk_id,
            "parent_id": parent_id,
            "kb_version": kb_version,
            "locale": locale,
            "topic": topic,
            "title": title,
            "chunk_text": chunk_text,
            "source": source,
            "embedding": _vector_literal(embedding),
        }
    else:
        sql = text(
            """
            INSERT INTO aladdin_kb_chunks (
                chunk_id, parent_id, kb_version, locale, topic, title, chunk_text, source, embedding, updated_at
            ) VALUES (
                :chunk_id, :parent_id, :kb_version, :locale, :topic, :title, :chunk_text, :source,
                NULL, NOW()
            )
            ON CONFLICT (chunk_id) DO UPDATE SET
                parent_id = EXCLUDED.parent_id,
                kb_version = EXCLUDED.kb_version,
                locale = EXCLUDED.locale,
                topic = EXCLUDED.topic,
                title = EXCLUDED.title,
                chunk_text = EXCLUDED.chunk_text,
                source = EXCLUDED.source,
                embedding = NULL,
                updated_at = NOW()
            """
        )
        params = {
            "chunk_id": chunk_id,
            "parent_id": parent_id,
            "kb_version": kb_version,
            "locale": locale,
            "topic": topic,
            "title": title,
            "chunk_text": chunk_text,
            "source": source,
        }
    with _engine().begin() as conn:
        conn.execute(sql, params)


def count_chunks(*, kb_version: str = "kb_v1", locale: Optional[str] = None) -> int:
    ensure_schema()
    clauses = ["kb_version = :kb_version", "embedding IS NOT NULL"]
    params: Dict[str, Any] = {"kb_version": kb_version}
    if locale:
        clauses.append("locale = :locale")
        params["locale"] = locale
    sql = text(f"SELECT COUNT(*) FROM aladdin_kb_chunks WHERE {' AND '.join(clauses)}")
    with _engine().connect() as conn:
        return int(conn.execute(sql, params).scalar() or 0)


def search(
    query_embedding: List[float],
    *,
    locale: str,
    top_k: int = 5,
    topic: Optional[str] = None,
    kb_version: str = "kb_v1",
) -> List[Dict[str, Any]]:
    ensure_schema()
    filters = ["kb_version = :kb_version", "locale = :locale", "embedding IS NOT NULL"]
    params: Dict[str, Any] = {
        "kb_version": kb_version,
        "locale": locale,
        "embedding": _vector_literal(query_embedding),
        "top_k": top_k,
    }
    if topic:
        filters.append("topic = :topic")
        params["topic"] = topic
    where_sql = " AND ".join(filters)
    sql = text(
        f"""
        SELECT
            chunk_id,
            parent_id,
            topic,
            title,
            chunk_text,
            source,
            1 - (embedding <=> CAST(:embedding AS vector)) AS score
        FROM aladdin_kb_chunks
        WHERE {where_sql}
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :top_k
        """
    )
    rows: List[Dict[str, Any]] = []
    with _engine().connect() as conn:
        result = conn.execute(sql, params)
        for row in result.mappings():
            rows.append(
                {
                    "chunk_id": row["chunk_id"],
                    "parent_id": row["parent_id"],
                    "topic": row["topic"],
                    "title": row["title"],
                    "text": row["chunk_text"],
                    "source": row["source"],
                    "score": float(row["score"] or 0),
                }
            )
    return rows


def search_lexical_fallback(
    query: str,
    *,
    locale: str,
    top_k: int = 5,
    kb_version: str = "kb_v1",
) -> List[Dict[str, Any]]:
    """Used when embeddings API unavailable (dev / credits)."""
    ensure_schema()
    q = f"%{query.strip()[:200]}%"
    sql = text(
        """
        SELECT chunk_id, parent_id, topic, title, chunk_text, source, 0.5 AS score
        FROM aladdin_kb_chunks
        WHERE kb_version = :kb_version AND locale = :locale
          AND (chunk_text ILIKE :q OR title ILIKE :q)
        LIMIT :top_k
        """
    )
    rows: List[Dict[str, Any]] = []
    with _engine().connect() as conn:
        result = conn.execute(
            sql, {"kb_version": kb_version, "locale": locale, "q": q, "top_k": top_k}
        )
        for row in result.mappings():
            rows.append(
                {
                    "chunk_id": row["chunk_id"],
                    "parent_id": row["parent_id"],
                    "topic": row["topic"],
                    "title": row["title"],
                    "text": row["chunk_text"],
                    "source": row["source"],
                    "score": float(row["score"] or 0),
                }
            )
    return rows
