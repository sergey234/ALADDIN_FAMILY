# -*- coding: utf-8 -*-
"""
E2.4 — PostgreSQL store: operational (7d redacted) + analytics (365d hash-only).
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from security.services.ai_history_retention import (
    ANALYTICS_RETENTION_DAYS,
    OPERATIONAL_RETENTION_DAYS,
    RETENTION_POLICY_ID,
    content_hash,
    user_id_hash,
)

logger = logging.getLogger(__name__)

_SCHEMA_READY = False


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _user_hash(user_id: Optional[str]) -> str:
    return user_id_hash(user_id)


def _content_hash(value: Optional[str]) -> Optional[str]:
    return content_hash(value)


def _get_engine():
    from app.database.database import engine  # type: ignore

    return engine


def ensure_tables() -> None:
    global _SCHEMA_READY
    if _SCHEMA_READY:
        return
    ddl = """
    CREATE TABLE IF NOT EXISTS ai_chat_operational (
        id UUID PRIMARY KEY,
        user_id_hash VARCHAR(64) NOT NULL,
        session_id VARCHAR(128),
        message_id VARCHAR(128),
        role VARCHAR(16) NOT NULL,
        content_redacted TEXT NOT NULL,
        ui_context VARCHAR(64) NOT NULL DEFAULT 'general',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    CREATE INDEX IF NOT EXISTS idx_ai_chat_operational_user_created
        ON ai_chat_operational (user_id_hash, created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_ai_chat_operational_created
        ON ai_chat_operational (created_at);

    CREATE TABLE IF NOT EXISTS ai_chat_analytics (
        id UUID PRIMARY KEY,
        user_id_hash VARCHAR(64),
        session_id VARCHAR(128),
        question_hash VARCHAR(64) NOT NULL,
        answer_hash VARCHAR(64),
        ui_context VARCHAR(64),
        rating SMALLINT,
        faq_id VARCHAR(128),
        resolved_by VARCHAR(64),
        sfm_aggregates_json TEXT,
        retention_policy VARCHAR(32) NOT NULL DEFAULT 'hybrid_d_v1',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    CREATE INDEX IF NOT EXISTS idx_ai_chat_analytics_created
        ON ai_chat_analytics (created_at);
    CREATE INDEX IF NOT EXISTS idx_ai_chat_analytics_user_created
        ON ai_chat_analytics (user_id_hash, created_at DESC);
    """
    engine = _get_engine()
    with engine.begin() as conn:
        for stmt in ddl.strip().split(";"):
            s = stmt.strip()
            if s:
                conn.execute(text(s))
    _SCHEMA_READY = True
    logger.info("AI history tables ensured (policy=%s)", RETENTION_POLICY_ID)


def purge_expired() -> Dict[str, int]:
    ensure_tables()
    op_cutoff = _utcnow() - timedelta(days=OPERATIONAL_RETENTION_DAYS)
    an_cutoff = _utcnow() - timedelta(days=ANALYTICS_RETENTION_DAYS)
    engine = _get_engine()
    with engine.begin() as conn:
        op_res = conn.execute(
            text("DELETE FROM ai_chat_operational WHERE created_at < :cutoff"),
            {"cutoff": op_cutoff},
        )
        an_res = conn.execute(
            text("DELETE FROM ai_chat_analytics WHERE created_at < :cutoff"),
            {"cutoff": an_cutoff},
        )
    deleted = {
        "operational": int(op_res.rowcount or 0),
        "analytics": int(an_res.rowcount or 0),
    }
    if deleted["operational"] or deleted["analytics"]:
        logger.info("AI history purge: %s", deleted)
    return deleted


def record_operational_turn(
    *,
    user_id: Optional[str],
    role: str,
    content_redacted: str,
    ui_context: str = "general",
    session_id: Optional[str] = None,
    message_id: Optional[str] = None,
) -> None:
    if not content_redacted or not content_redacted.strip():
        return
    ensure_tables()
    purge_expired()
    engine = _get_engine()
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO ai_chat_operational
                    (id, user_id_hash, session_id, message_id, role, content_redacted, ui_context, created_at)
                VALUES
                    (:id, :user_id_hash, :session_id, :message_id, :role, :content, :ui_context, :created_at)
                """
            ),
            {
                "id": str(uuid.uuid4()),
                "user_id_hash": _user_hash(user_id),
                "session_id": session_id,
                "message_id": message_id,
                "role": role[:16],
                "content": content_redacted[:4000],
                "ui_context": (ui_context or "general")[:64],
                "created_at": _utcnow(),
            },
        )


def record_chat_exchange(
    *,
    user_id: Optional[str],
    user_message_redacted: str,
    assistant_message: str,
    ui_context: str = "general",
    session_id: Optional[str] = None,
    message_id: Optional[str] = None,
    sfm_aggregates: Optional[Dict[str, Any]] = None,
) -> None:
    """Operational 7d + analytics hash-only."""
    record_operational_turn(
        user_id=user_id,
        role="user",
        content_redacted=user_message_redacted,
        ui_context=ui_context,
        session_id=session_id,
        message_id=message_id,
    )
    record_operational_turn(
        user_id=user_id,
        role="assistant",
        content_redacted=assistant_message[:4000],
        ui_context=ui_context,
        session_id=session_id,
        message_id=message_id,
    )
    record_analytics_event(
        user_id=user_id,
        question_redacted=user_message_redacted,
        answer_text=assistant_message,
        ui_context=ui_context,
        session_id=session_id,
        sfm_aggregates=sfm_aggregates,
    )


def record_analytics_event(
    *,
    user_id: Optional[str],
    question_redacted: Optional[str] = None,
    answer_text: Optional[str] = None,
    ui_context: Optional[str] = None,
    session_id: Optional[str] = None,
    rating: Optional[int] = None,
    faq_id: Optional[str] = None,
    resolved_by: Optional[str] = None,
    sfm_aggregates: Optional[Dict[str, Any]] = None,
) -> None:
    q_hash = _content_hash(question_redacted)
    if not q_hash:
        q_hash = _content_hash(f"event:{resolved_by}:{rating}:{faq_id}")
    if not q_hash:
        return

    ensure_tables()
    agg_json = None
    if sfm_aggregates:
        try:
            agg_json = json.dumps(sfm_aggregates, ensure_ascii=False)[:8000]
        except (TypeError, ValueError):
            agg_json = None

    engine = _get_engine()
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO ai_chat_analytics
                    (id, user_id_hash, session_id, question_hash, answer_hash, ui_context,
                     rating, faq_id, resolved_by, sfm_aggregates_json, retention_policy, created_at)
                VALUES
                    (:id, :user_id_hash, :session_id, :question_hash, :answer_hash, :ui_context,
                     :rating, :faq_id, :resolved_by, :sfm_aggregates_json, :policy, :created_at)
                """
            ),
            {
                "id": str(uuid.uuid4()),
                "user_id_hash": _user_hash(user_id),
                "session_id": session_id,
                "question_hash": q_hash,
                "answer_hash": _content_hash(answer_text),
                "ui_context": (ui_context or "")[:64] or None,
                "rating": rating,
                "faq_id": (faq_id or "")[:128] or None,
                "resolved_by": (resolved_by or "")[:64] or None,
                "sfm_aggregates_json": agg_json,
                "policy": RETENTION_POLICY_ID,
                "created_at": _utcnow(),
            },
        )


def list_conversation_summaries(
    user_id: Optional[str],
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Aggregated history for GET /history (no plaintext bodies)."""
    ensure_tables()
    engine = _get_engine()
    user_h = _user_hash(user_id)
    op_cutoff = _utcnow() - timedelta(days=OPERATIONAL_RETENTION_DAYS)
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT DATE(created_at AT TIME ZONE 'UTC') AS day,
                       COUNT(*) AS message_count,
                       ARRAY_AGG(DISTINCT ui_context) AS topics
                FROM ai_chat_operational
                WHERE user_id_hash = :user_hash AND created_at >= :cutoff
                GROUP BY day
                ORDER BY day DESC
                LIMIT :lim
                """
            ),
            {"user_hash": user_h, "cutoff": op_cutoff, "lim": limit},
        ).mappings().all()

    conversations: List[Dict[str, Any]] = []
    for row in rows:
        topics = row.get("topics") or []
        if isinstance(topics, str):
            topics = [topics]
        conversations.append(
            {
                "date": str(row["day"]),
                "messages": int(row["message_count"] or 0),
                "topics": [t for t in topics if t][:10],
                "retention_policy": RETENTION_POLICY_ID,
                "storage": "operational_redacted",
            }
        )
    return conversations
