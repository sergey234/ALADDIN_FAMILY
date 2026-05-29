# -*- coding: utf-8 -*-
"""Grounded ai_assistant_chat responses for SFM HTTP worker (no prod stub phrases)."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional


def _aggregates(params: Dict[str, Any]) -> Dict[str, Any]:
    raw = params.get("sfm_aggregates")
    return raw if isinstance(raw, dict) else {}


def _try_simple_math(message: str) -> Optional[str]:
    """Безопасный ответ на элементарную арифметику (1+1, 2*3), когда LLM недоступен."""
    m = re.search(r"(?i)(\d{1,6})\s*([+\-*/×÷])\s*(\d{1,6})", message)
    if not m:
        return None
    a = int(m.group(1))
    op_raw = m.group(2)
    b = int(m.group(3))
    op = {"+": "+", "-": "-", "*": "*", "/": "/", "×": "*", "÷": "/"}[op_raw]
    if op == "+" and a + b > 1_000_000:
        return None
    if op == "-" and a - b < -1_000_000:
        return None
    if op == "*":
        result = a * b
    elif op == "/":
        if b == 0:
            return "Деление на ноль невозможно. Я помощник ALADDIN — спросите про защиту семьи, VPN или чат."
        result = a // b if a % b == 0 else round(a / b, 4)
    elif op == "-":
        result = a - b
    else:
        result = a + b
    return (
        f"{a} {op_raw} {b} = {result}. "
        "Я AI-помощник ALADDIN: могу подробнее рассказать про защиту семьи, угрозы, VPN, семейный чат и тарифы."
    )


def _off_topic_guidance(aggregates: Dict[str, Any], message: str) -> str:
    topic = message.strip()
    if len(topic) > 120:
        topic = topic[:117] + "…"
    lead = (
        f"По теме «{topic}» у меня нет отдельной базы знаний — я помощник ALADDIN по кибербезопасности семьи. "
        if topic
        else "Этот вопрос вне моей специализации — я помощник ALADDIN по кибербезопасности семьи. "
    )
    return (
        lead
        + "Могу помочь с защитой семьи, VPN, родительским контролем, семейным чатом, угрозами и тарифами. "
        + _status_line(aggregates)
    )


def _status_line(aggregates: Dict[str, Any]) -> str:
    status = aggregates.get("protection_status") or "ACTIVE"
    healthy = aggregates.get("healthy_components")
    total = aggregates.get("total_components")
    threats = aggregates.get("threats_blocked")
    parts = [f"Статус защиты ALADDIN: {status}."]
    if healthy is not None and total is not None:
        parts.append(f" Активных модулей: {healthy} из {total}.")
    if isinstance(threats, int):
        parts.append(f" Заблокировано угроз за период: {threats}.")
    return "".join(parts)


def _companion_life_first_fallback(
    message: str, aggregates: Dict[str, Any], params: Dict[str, Any]
) -> Dict[str, Any]:
    """Companion SFM path when Hermes/LLM unavailable — life-first, not security keyword router."""
    msg_lower = message.lower()
    if "привет" in msg_lower or "здравств" in msg_lower or "hello" in msg_lower:
        response_text = (
            "Привет! Я рядом — расскажи, как день, или спроси что угодно. "
            "Если понадобится помощь с безопасностью ALADDIN — подскажу."
        )
    elif any(w in msg_lower for w in ("груст", "одинок", "скуч", "страш", "боюсь")):
        response_text = (
            "Слышу тебя. Так бывает — важно, что ты делишься. "
            "Хочешь поговорить подробнее или найти, чем заняться? "
            "Если что-то серьёзное — лучше рассказать взрослому, которому доверяешь."
        )
    elif any(w in msg_lower for w in ("школ", "урок", "учит", "домашк")):
        response_text = (
            "Про школу могу помочь разобраться: что задали, как спланировать время, "
            "как спокойнее готовиться. О чём именно хочешь поговорить?"
        )
    elif any(w in msg_lower for w in ("друг", "общен", "ссор")):
        response_text = (
            "Дружба бывает разной — иногда сложно. Расскажи, что случилось, "
            "и вместе подумаем, что можно сделать."
        )
    else:
        response_text = (
            "Я пока отвечаю в упрощённом режиме — но я здесь и слушаю. "
            "Расскажи подробнее, о чём хочешь поговорить?"
        )
    return {
        "response": response_text,
        "confidence": 0.72,
        "timestamp": datetime.utcnow().isoformat(),
        "suggestions": [],
        "follow_up_questions": [],
        "llm_context_policy": params.get("llm_context_policy", "aggregates_only_v1"),
        "sfm_context_sources": list(params.get("sfm_context_sources") or []),
        "grounded": False,
    }


def build_ai_assistant_chat_result(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ответ только из whitelisted aggregates + FAQ-style product copy.
    Без фраз «1074 функций» / «реальный AI» — prod-safe.
    """
    message = (params.get("message") or "").strip()
    msg_lower = message.lower()
    context = (params.get("context") or "general").strip() or "general"
    aggregates = _aggregates(params)
    sources: List[str] = list(params.get("sfm_context_sources") or [])

    if context == "companion":
        return _companion_life_first_fallback(message, aggregates, params)

    meta = _match_meta(msg_lower)
    math_answer = _try_simple_math(message)
    if meta:
        response_text = meta
        grounded = False
    elif math_answer:
        response_text = math_answer
        grounded = False
    elif "привет" in msg_lower or "здравств" in msg_lower or "hello" in msg_lower:
        response_text = (
            "Здравствуйте! Я AI-помощник ALADDIN — помогаю с защитой семьи, VPN, "
            "родительским контролем и семейным чатом. " + _status_line(aggregates)
        )
        grounded = bool(sources)
    elif any(w in msg_lower for w in ("защит", "статус", "модул", "включ")):
        response_text = _status_line(aggregates)
        grounded = bool(sources)
    elif any(w in msg_lower for w in ("угроз", "блок", "аналит")):
        threats = aggregates.get("threats_blocked")
        if isinstance(threats, int):
            response_text = (
                f"За выбранный период система ALADDIN заблокировала {threats} угроз. "
                + _status_line(aggregates)
            )
        else:
            response_text = (
                "Мониторинг угроз активен. Откройте раздел «Аналитика» для деталей. "
                + _status_line(aggregates)
            )
        grounded = bool(sources)
    elif any(w in msg_lower for w in ("vpn", "сеть", "wi-fi", "wifi")):
        response_text = (
            "Сетевую защиту и VPN можно проверить в разделе «Защита сети». "
            + _status_line(aggregates)
        )
        grounded = bool(sources)
    elif any(w in msg_lower for w in ("семь", "чат", "e2ee", "шифр")):
        response_text = (
            "Семейный чат с E2EE доступен в приложении ALADDIN: пригласите участников, "
            "дождитесь настройки ключей на устройствах семьи, затем отправляйте сообщения. "
            + _status_line(aggregates)
        )
        grounded = bool(sources)
    elif any(w in msg_lower for w in ("тариф", "подписк", "premium")):
        response_text = (
            "Тарифы и лимиты смотрите в разделе «Тарифы». Trial даёт базовую защиту и AI-помощник."
        )
        grounded = False
    else:
        response_text = _off_topic_guidance(aggregates, message)
        grounded = bool(sources)

    lang = (params.get("response_language") or "").lower()
    if lang.startswith("en") and response_text:
        response_text = _english_hint(response_text, msg_lower)

    return {
        "response": response_text,
        "confidence": 0.88 if grounded else 0.72,
        "timestamp": datetime.utcnow().isoformat(),
        "suggestions": ["Статус защиты", "Семейный чат", "Тарифы"],
        "follow_up_questions": ["Что проверить в первую очередь?"],
        "llm_context_policy": params.get("llm_context_policy", "aggregates_only_v1"),
        "sfm_context_sources": sources,
        "grounded": grounded,
    }


def _match_meta(msg_lower: str) -> Optional[str]:
    if re.search(r"учишь|обуча|обучен|learn|training", msg_lower):
        return (
            "Я не «учусь» на телефоне и не запоминаю ваши сообщения для обучения модели. "
            "Отвечаю по справочнику ALADDIN и по актуальным агрегатам защиты с сервера "
            "(статус модулей, угрозы, семья). Включите «Облачный AI-помощник» в настройках."
        )
    # Не ловим «что ты знаешь о …» — только явные вопросы о роли помощника.
    if re.search(
        r"(^|\s)(кто ты|ты кто|что ты такое|what are you|who are you)(\s|$|[?!.])",
        msg_lower,
    ):
        return (
            "Я AI-помощник приложения ALADDIN: безопасность семьи, VPN, родительский контроль, "
            "семейный чат и подсказки по настройкам."
        )
    if re.search(r"что ты умеешь|что ты можешь|что умеешь|что можешь|возможност", msg_lower):
        return (
            "Могу объяснить статус защиты, угрозы, настройки семьи и VPN, E2EE в чате, тарифы — "
            "на основе данных ALADDIN, без выдуманных цифр."
        )
    return None


def _english_hint(ru_text: str, msg_lower: str) -> str:
    if "learn" in msg_lower or "train" in msg_lower:
        return (
            "I do not train on your device. I answer using ALADDIN knowledge base and "
            "live protection aggregates from the server."
        )
    return ru_text + " (Enable Russian in app language for full localized answers.)"
