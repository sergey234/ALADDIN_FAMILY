# -*- coding: utf-8 -*-
"""RAG v1: static KB chunks → grounded answers (kb_rag_v1 policy)."""
from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from typing import List, Optional

from security.services.ai_intent_router import KB_ONLY_INTENTS
from security.services.hermes_client import chat_once as hermes_chat_once, hermes_available
from security.services.kb_search_service import kb_search

logger = logging.getLogger(__name__)

LLM_CONTEXT_POLICY_KB_RAG_V1 = "kb_rag_v1"
RAG_ELIGIBLE_INTENTS = KB_ONLY_INTENTS | frozenset({"general", "app_help"})
MIN_SCORE = float(os.getenv("AI_RAG_MIN_SCORE", "0.38"))
TOP_K = int(os.getenv("AI_RAG_TOP_K", "4"))


def rag_enabled() -> bool:
    return os.getenv("AI_RAG_ENABLED", "1").strip().lower() in ("1", "true", "yes", "on")


def intent_rag_eligible(intent_id: str, kb_only: bool) -> bool:
    if kb_only:
        return True
    return intent_id in RAG_ELIGIBLE_INTENTS


def resolve_locale(response_language: Optional[str], message: str) -> str:
    if response_language:
        code = response_language.strip().lower()[:2]
        if code in ("ru", "en"):
            return code
    if re.search(r"[а-яё]", (message or "").lower()):
        return "ru"
    return "en"


@dataclass(frozen=True)
class KBRagResult:
    response_text: str
    sources: List[str]
    tools_used: List[str]
    confidence: float = 0.86

    @property
    def grounded(self) -> bool:
        return True


def _topic_for_intent(intent_id: str) -> Optional[str]:
    mapping = {
        "tariff_explain": "tariff",
        "e2ee_howto": "e2ee",
        "parental_howto": "parental",
        "app_help": "app_help",
    }
    return mapping.get(intent_id)


def _build_rag_prompt(question: str, hits: List[dict], locale: str) -> str:
    header_ru = (
        "Ты AI-помощник ALADDIN по безопасности семьи. "
        "Отвечай ТОЛЬКО на основе фрагментов базы знаний ниже. "
        "Не выдумывай факты. Если в фрагментах нет ответа — скажи коротко, "
        "что по этой теме в справочнике ALADDIN нет данных, и предложи спросить про защиту, VPN, семью или тарифы."
    )
    header_en = (
        "You are the ALADDIN family security assistant. "
        "Answer ONLY using the knowledge base excerpts below. "
        "Do not invent facts. If excerpts do not contain the answer, say so briefly "
        "and suggest asking about protection, VPN, family, or tariffs."
    )
    header = header_ru if locale == "ru" else header_en
    blocks = []
    for i, hit in enumerate(hits[:TOP_K], start=1):
        sid = hit.get("parent_id") or hit.get("chunk_id", f"chunk_{i}")
        title = (hit.get("title") or "").strip()
        text = (hit.get("text") or "").strip()
        if len(text) > 2400:
            text = text[:2397] + "…"
        blocks.append(f"[{sid}]\n{title}\n{text}")
    kb_body = "\n\n---\n\n".join(blocks)
    q_label = "Вопрос" if locale == "ru" else "Question"
    return f"{header}\n\n## База знаний ALADDIN\n\n{kb_body}\n\n## {q_label}\n{question.strip()}"


def _extractive_answer(hits: List[dict], locale: str) -> str:
    """Fallback: ответ из лучшего чанка без LLM."""
    top = hits[0]
    body = (top.get("text") or "").strip()
    if len(body) > 1800:
        body = body[:1797] + "…"
    if locale == "ru":
        lead = "По справочнику ALADDIN:\n\n"
        tail = "\n\n(Ответ на основе базы знаний приложения.)"
    else:
        lead = "From the ALADDIN knowledge base:\n\n"
        tail = "\n\n(Based on the in-app knowledge base.)"
    return f"{lead}{body}{tail}"


def _source_ids(hits: List[dict]) -> List[str]:
    seen: List[str] = []
    for hit in hits[:TOP_K]:
        sid = str(hit.get("parent_id") or hit.get("chunk_id") or "").strip()
        if sid and sid not in seen:
            seen.append(sid)
    return seen


def try_kb_rag_answer(
    *,
    question: str,
    intent_id: str,
    kb_only: bool,
    locale: str,
) -> Optional[KBRagResult]:
    """
    R2.1–R2.3: search chunks → Hermes with kb_rag_v1 prompt → else extractive → None (caller falls back).
    """
    if not rag_enabled() or not intent_rag_eligible(intent_id, kb_only):
        return None

    topic = _topic_for_intent(intent_id)
    hits = kb_search(question, locale=locale, top_k=TOP_K, topic=topic)
    if not hits:
        logger.info("kb_rag: no hits intent=%s locale=%s", intent_id, locale)
        return None
    if float(hits[0].get("score") or 0) < MIN_SCORE:
        logger.info(
            "kb_rag: low score %.3f intent=%s",
            float(hits[0].get("score") or 0),
            intent_id,
        )
        return None

    sources = _source_ids(hits)
    tools = [f"kb_rag_v1:{LLM_CONTEXT_POLICY_KB_RAG_V1}"]

    if hermes_available():
        prompt = _build_rag_prompt(question, hits, locale)
        ok, text, err = hermes_chat_once(prompt, skill="aladdin-security-kb")
        if ok and text.strip():
            logger.info(
                "kb_rag: hermes ok intent=%s sources=%s",
                intent_id,
                sources[:3],
            )
            tools.append("hermes:aladdin-security-kb")
            return KBRagResult(
                response_text=text.strip(),
                sources=sources,
                tools_used=tools,
            )
        logger.warning("kb_rag: hermes failed intent=%s err=%s", intent_id, err)

    text = _extractive_answer(hits, locale)
    tools.append("kb_rag_v1:extractive")
    logger.info("kb_rag: extractive intent=%s sources=%s", intent_id, sources[:3])
    return KBRagResult(
        response_text=text,
        sources=sources,
        tools_used=tools,
        confidence=0.82,
    )
