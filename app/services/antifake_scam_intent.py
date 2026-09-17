"""afhub-p1-01 — scam-intent layer (money/card/OTP/SBP/authority), separate from fake-news.

Produces fine-grained tags for scoring / reasons. Lexicon (P0) stays the phrase SSOT;
this module classifies intent buckets so news sensationalism ≠ payment scam.

Family optimum: each bucket has **single words** + **multi-word phrases** (RU+EN).
"""
from __future__ import annotations

from typing import List, Sequence, Set, Tuple

# (intent_tag, phrases) — substring match, case-insensitive.
_INTENT_PHRASES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    (
        "intent_money_transfer",
        (
            # words
            "переведи",
            "переведите",
            "перевод",
            "скинь",
            "скиньте",
            "wire",
            "venmo",
            "zelle",
            # phrases
            "перевести деньги",
            "скинь деньги",
            "скиньте деньги",
            "перевод средств",
            "отправь деньги",
            "отправьте деньги",
            "send money",
            "send me money",
            "transfer money",
            "transfer now",
            "wire me",
            "wire money",
            "cash app",
        ),
    ),
    (
        "intent_card",
        (
            # words
            "карта",
            "карту",
            "cvv",
            "cvc",
            "card",
            # phrases
            "на карту",
            "на мою карту",
            "реквизиты карты",
            "номер карты",
            "данные карты",
            "полный номер карты",
            "to my card",
            "card number",
            "card details",
            "send card details",
        ),
    ),
    (
        "intent_otp",
        (
            # words
            "otp",
            "смс",
            # phrases (avoid bare "код" alone — too noisy for intent)
            "код из смс",
            "код из sms",
            "одноразовый код",
            "код подтверждения",
            "назовите код",
            "продиктуйте код",
            "скажите код",
            "никому не сообщайте код",
            "никому не говорите код",
            "verification code",
            "one-time code",
            "one time code",
            "don't share the code",
            "do not share the code",
            "read me the code",
            "tell me the code",
        ),
    ),
    (
        "intent_sbp",
        (
            "сбп",
            "сбп перевод",
            "перевод по сбп",
            "быстрый платёж",
            "быстрый платеж",
            "faster payments",
            "instant transfer",
        ),
    ),
    (
        "intent_authority",
        (
            # words — banks / agencies / operators
            "сбер",
            "сбербанк",
            "тинькофф",
            "тбанк",
            "втб",
            "альфа",
            "мвд",
            "фсб",
            "полиция",
            "налоговая",
            "госуслуги",
            "мтс",
            "билайн",
            "мегафон",
            "теле2",
            "paypal",
            "irs",
            "chase",
            # phrases
            "служба безопасности",
            "служба безопасност",
            "служба безопасности банка",
            "сотрудник банка",
            "оператор банка",
            "банк безопасности",
            "bank security",
            "fraud department",
            "security department",
            "apple support",
            "microsoft support",
            "amazon support",
            "tax office",
            "your account is blocked",
            "account locked",
            "account suspended",
            "ваш счёт заблокирован",
            "ваш счет заблокирован",
            "счет заблокирован",
            "счёт заблокирован",
            "verify your account",
        ),
    ),
    (
        "intent_prize",
        (
            "приз",
            "prize",
            "наследство",
            "inheritance",
            "выиграли приз",
            "вы выиграли",
            "you won",
            "you have won",
            "claim your prize",
            "переведите комиссию",
            "оплатите пошлин",
            "advance fee",
        ),
    ),
)

_NEWS_ONLY_TAGS: Set[str] = {
    "sensationalism",
    "no_source",
    "no_sources",
    "conspiracy",
    "emotional_manipulation",
}

PAYMENT_INTENT_TAGS: Set[str] = {
    "intent_money_transfer",
    "intent_card",
    "intent_otp",
    "intent_sbp",
    "intent_authority",
    "intent_prize",
}

# Authority/brand alone is a hint — not enough to mark coarse `scam` / hard floor.
HARD_PAYMENT_INTENT_TAGS: Set[str] = {
    "intent_money_transfer",
    "intent_card",
    "intent_otp",
    "intent_sbp",
    "intent_prize",
}


def intent_stats() -> dict:
    words = phrases = total = 0
    by: dict = {}
    for tag, pats in _INTENT_PHRASES:
        by[tag] = len(pats)
        for p in pats:
            total += 1
            if " " in p.strip():
                phrases += 1
            else:
                words += 1
    return {
        "total": total,
        "single_words": words,
        "multiword_phrases": phrases,
        "by_tag": by,
    }


def classify_scam_intent(text: str) -> List[str]:
    """Return ordered unique intent_* tags found in text."""
    lowered = (text or "").lower().strip()
    if not lowered:
        return []
    hits: List[str] = []
    seen: Set[str] = set()
    for tag, phrases in _INTENT_PHRASES:
        for phrase in phrases:
            if phrase.lower() in lowered and tag not in seen:
                hits.append(tag)
                seen.add(tag)
                break
    return hits


def has_payment_scam_intent(tags: Sequence[str]) -> bool:
    return bool(set(tags) & PAYMENT_INTENT_TAGS)


def is_news_only_signal(tags: Sequence[str]) -> bool:
    """True when hits are only sensationalism/conspiracy — not payment scam."""
    s = set(tags)
    if not s:
        return False
    if s & PAYMENT_INTENT_TAGS:
        return False
    if "scam" in s or "urgency" in s:
        return False
    return bool(s) and s <= _NEWS_ONLY_TAGS


def merge_intent_into_hits(hits: Sequence[str], intent_tags: Sequence[str]) -> List[str]:
    """Append intent tags; hard payment intents → coarse `scam` for P0 floors.

    Brand/authority alone does not add `scam` (avoids «иду в сбер» → likely_fake).
    """
    out: List[str] = []
    seen: Set[str] = set()
    for h in list(hits) + list(intent_tags):
        if h and h not in seen:
            out.append(h)
            seen.add(h)
    if (set(out) & HARD_PAYMENT_INTENT_TAGS) and "scam" not in seen:
        out.append("scam")
        seen.add("scam")
    return out
