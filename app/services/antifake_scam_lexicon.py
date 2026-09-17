"""Shared RU/EN scam lexicon for antifake text heuristics + agents (afhub-p0-02).

Family optimum lexicon_v2: both **single words** and **multi-word phrases** (RU+EN).
SSOT — do not duplicate in antifake_service / FakeNewsDetectionAgent.

Tags: urgency | scam | sensationalism | no_source
Weak singles (деньги/карта/код/банк) alone do not force likely_fake — need a partner signal.
"""
from __future__ import annotations

from typing import Dict, List, Sequence, Set, Tuple

LEXICON_VERSION = "lexicon_v2"

# Ambiguous singles: match as scam, but scoring needs urgency / 2nd intent / strong phrase.
WEAK_SCAM_SINGLES: Set[str] = {
    # money / card / code (generic)
    "деньги",
    "средства",
    "карта",
    "карты",
    "карту",
    "код",
    "коды",
    "банк",
    "банка",
    "перевод",
    "перевода",
    "комиссия",
    "штраф",
    "money",
    "funds",
    "card",
    "cards",
    "code",
    "codes",
    "bank",
    "transfer",
    "payment",
    "account",
    "prize",
    "приз",
    "смс",
    "sms",
    "wire",
    # brand / operator / agency names alone ≠ scam SMS
    "сбер",
    "сбербанк",
    "тинькофф",
    "тбанк",
    "втб",
    "альфа",
    "газпромбанк",
    "открытие",
    "совкомбанк",
    "райффайзен",
    "россельхозбанк",
    "мвд",
    "фсб",
    "полиция",
    "налоговая",
    "госуслуги",
    "мтс",
    "билайн",
    "мегафон",
    "теле2",
    "beeline",
    "megafon",
    "tele2",
    "chase",
    "paypal",
    "irs",
    "подтвердите",
    "развод",
}

# (tag, phrase) — substring, case-insensitive. Prefer both word + phrase forms.
SCAM_LEXICON_PATTERNS: Tuple[Tuple[str, str], ...] = (
    # ========== URGENCY — words ==========
    ("urgency", "срочно"),
    ("urgency", "немедленно"),
    ("urgency", "моментально"),
    ("urgency", "сейчас же"),
    ("urgency", "безотлагательно"),
    ("urgency", "urgent"),
    ("urgency", "urgently"),
    ("urgency", "immediately"),
    ("urgency", "asap"),
    # ========== URGENCY — phrases ==========
    ("urgency", "сегодня до"),
    ("urgency", "через час"),
    ("urgency", "в течение часа"),
    ("urgency", "действуй сейчас"),
    ("urgency", "действуйте сейчас"),
    ("urgency", "действуйте немедленно"),
    ("urgency", "не жди"),
    ("urgency", "не ждите"),
    ("urgency", "ограниченное время"),
    ("urgency", "последний шанс"),
    ("urgency", "пока не поздно"),
    ("urgency", "act now"),
    ("urgency", "act within"),
    ("urgency", "right now"),
    ("urgency", "within an hour"),
    ("urgency", "within 10 minutes"),
    ("urgency", "не говорите никому"),
    ("urgency", "limited time"),
    ("urgency", "don't wait"),
    ("urgency", "do not wait"),
    ("urgency", "last chance"),
    ("urgency", "before it's too late"),
    ("urgency", "expires today"),
    # ========== MONEY — words ==========
    ("scam", "деньги"),
    ("scam", "средства"),
    ("scam", "перевод"),
    ("scam", "переведи"),
    ("scam", "переведите"),
    ("scam", "скинь"),
    ("scam", "скиньте"),
    ("scam", "money"),
    ("scam", "funds"),
    ("scam", "transfer"),
    ("scam", "wire"),
    # ========== MONEY — phrases ==========
    ("scam", "переведи мне деньги"),
    ("scam", "переведите деньги"),
    ("scam", "переведите средства"),
    ("scam", "переведите комиссию"),
    ("scam", "перевести деньги"),
    ("scam", "скинь деньги"),
    ("scam", "скиньте деньги"),
    ("scam", "перевод средств"),
    ("scam", "отправь деньги"),
    ("scam", "отправьте деньги"),
    ("scam", "send money"),
    ("scam", "send me money"),
    ("scam", "transfer money"),
    ("scam", "transfer now"),
    ("scam", "wire me"),
    ("scam", "wire money"),
    ("scam", "cash app"),
    ("scam", "venmo"),
    ("scam", "zelle"),
    ("scam", "western union"),
    # ========== CARD — words ==========
    ("scam", "карта"),
    ("scam", "карты"),
    ("scam", "карту"),
    ("scam", "cvv"),
    ("scam", "cvc"),
    ("scam", "card"),
    # ========== CARD — phrases ==========
    ("scam", "на карту"),
    ("scam", "на мою карту"),
    ("scam", "деньги на карту"),
    ("scam", "перевод на карту"),
    ("scam", "реквизиты карты"),
    ("scam", "номер карты"),
    ("scam", "данные карты"),
    ("scam", "полный номер карты"),
    ("scam", "срок действия карты"),
    ("scam", "to my card"),
    ("scam", "card number"),
    ("scam", "card details"),
    ("scam", "send card details"),
    # ========== SBP / instant pay ==========
    ("scam", "сбп"),
    ("scam", "сбп перевод"),
    ("scam", "перевод по сбп"),
    ("scam", "быстрый платёж"),
    ("scam", "быстрый платеж"),
    ("scam", "faster payments"),
    ("scam", "instant transfer"),
    # ========== OTP — words ==========
    ("scam", "код"),
    ("scam", "otp"),
    ("scam", "смс"),
    ("scam", "sms"),
    # ========== OTP — phrases ==========
    ("scam", "код из смс"),
    ("scam", "код из sms"),
    ("scam", "код из сms"),
    ("scam", "кодом из смс"),
    ("scam", "кодом из sms"),
    ("scam", "оплату кодом"),
    ("scam", "одноразовый код"),
    ("scam", "код подтверждения"),
    ("scam", "назовите код"),
    ("scam", "продиктуйте код"),
    ("scam", "скажите код"),
    ("scam", "никому не сообщайте код"),
    ("scam", "никому не говорите код"),
    ("scam", "не сообщайте код"),
    ("scam", "не говорите никому"),
    ("scam", "verification code"),
    ("scam", "one-time code"),
    ("scam", "one time code"),
    ("scam", "sms code"),
    ("scam", "safe account"),
    ("scam", "remaining balance"),
    ("scam", "don't share the code"),
    ("scam", "do not share the code"),
    ("scam", "read me the code"),
    ("scam", "tell me the code"),
    # ========== FRAUD labels — words ==========
    ("scam", "скамер"),
    ("scam", "мошенник"),
    ("scam", "мошенничество"),
    ("scam", "развод"),
    ("scam", "scammer"),
    ("scam", "fraud"),
    ("scam", "phishing"),
    # ========== FRAUD — phrases ==========
    ("scam", "это развод"),
    ("scam", "это мошенничество"),
    ("scam", "it's a scam"),
    ("scam", "this is a scam"),
    ("scam", "advance fee"),
    # ========== LOCK / ACCOUNT — words ==========
    ("scam", "заблокирован"),
    ("scam", "заблокирована"),
    ("scam", "разблокировк"),
    ("scam", "банк"),
    ("scam", "account"),
    # ========== LOCK / ACCOUNT — phrases ==========
    ("scam", "ваш счёт заблокирован"),
    ("scam", "ваш счет заблокирован"),
    ("scam", "счет заблокирован"),
    ("scam", "счёт заблокирован"),
    ("scam", "безопасный счет"),
    ("scam", "безопасный счёт"),
    ("scam", "резервный счет"),
    ("scam", "резервный счёт"),
    ("scam", "арест счета"),
    ("scam", "арест счёта"),
    ("scam", "блокировка карт"),
    ("scam", "блокировка карты"),
    ("scam", "списать деньги"),
    ("scam", "возбуждено дело"),
    ("scam", "оплатите штраф"),
    ("scam", "оплатите пошлин"),
    ("scam", "оплатите немедленн"),
    ("scam", "внесите оплату"),
    ("scam", "подтвердите оплату"),
    ("scam", "оплату картой"),
    ("scam", "подтвердите перевод"),
    ("scam", "подтвердите"),
    ("scam", "your account is blocked"),
    ("scam", "account locked"),
    ("scam", "account suspended"),
    ("scam", "verify your account"),
    ("scam", "unlock your account"),
    ("scam", "send money immediately"),
    # ========== AUTHORITY / BANKS RU — words ==========
    ("scam", "сбер"),
    ("scam", "сбербанк"),
    ("scam", "тинькофф"),
    ("scam", "тбанк"),
    ("scam", "втб"),
    ("scam", "альфа"),
    ("scam", "газпромбанк"),
    ("scam", "открытие"),
    ("scam", "совкомбанк"),
    ("scam", "райффайзен"),
    ("scam", "россельхозбанк"),
    ("scam", "мвд"),
    ("scam", "фсб"),
    ("scam", "полиция"),
    ("scam", "налоговая"),
    ("scam", "госуслуги"),
    # ========== AUTHORITY / BANKS RU — phrases ==========
    ("scam", "служба безопасности"),
    ("scam", "служба безопасност"),
    ("scam", "служба безопасности банка"),
    ("scam", "сотрудник банка"),
    ("scam", "оператор банка"),
    ("scam", "безопасность сбера"),
    ("scam", "безопасность тинькофф"),
    ("scam", "банк безопасности"),
    # ========== OPERATORS RU ==========
    ("scam", "мтс"),
    ("scam", "билайн"),
    ("scam", "мегафон"),
    ("scam", "теле2"),
    ("scam", "beeline"),
    ("scam", "megafon"),
    ("scam", "tele2"),
    ("scam", "служба поддержки мтс"),
    ("scam", "поддержка билайн"),
    # ========== AUTHORITY / BANKS EN — words + phrases ==========
    ("scam", "chase"),
    ("scam", "wells fargo"),
    ("scam", "bank of america"),
    ("scam", "paypal"),
    ("scam", "apple id"),
    ("scam", "apple support"),
    ("scam", "microsoft support"),
    ("scam", "amazon support"),
    ("scam", "irs"),
    ("scam", "tax office"),
    ("scam", "bank security"),
    ("scam", "fraud department"),
    ("scam", "security department"),
    ("scam", "police department"),
    # ========== PRIZE / FEE ==========
    ("scam", "приз"),
    ("scam", "prize"),
    ("scam", "выиграли приз"),
    ("scam", "вы выиграли"),
    ("scam", "you won"),
    ("scam", "you have won"),
    ("scam", "claim your prize"),
    ("scam", "inheritance"),
    ("scam", "наследство"),
    # ========== NEWS (keep separate from payment floors) ==========
    ("sensationalism", "шокирующая правда"),
    ("sensationalism", "врачи в шоке"),
    ("sensationalism", "they don't want you to know"),
    ("sensationalism", "doctors hate this"),
    ("sensationalism", "shocking truth"),
    ("no_source", "анонимных источников"),
    ("no_source", "anonymous sources"),
    ("no_source", "insiders say"),
)

# Agent-facing aliases (FakeNewsDetectionAgent pattern categories).
AGENT_URGENCY_PHRASES: Tuple[str, ...] = tuple(
    p for t, p in SCAM_LEXICON_PATTERNS if t == "urgency"
)
AGENT_FINANCIAL_PHRASES: Tuple[str, ...] = tuple(
    p for t, p in SCAM_LEXICON_PATTERNS if t == "scam"
)


def lexicon_stats() -> Dict[str, int]:
    """Counts for plan / QA — words vs phrases (space in pattern)."""
    by_tag: Dict[str, int] = {}
    words = 0
    phrases = 0
    seen: Set[str] = set()
    for tag, pat in SCAM_LEXICON_PATTERNS:
        by_tag[tag] = by_tag.get(tag, 0) + 1
        key = pat.lower()
        if key in seen:
            continue
        seen.add(key)
        if " " in pat.strip():
            phrases += 1
        else:
            words += 1
    return {
        "version": 2,
        "total_entries": len(SCAM_LEXICON_PATTERNS),
        "unique": len(seen),
        "single_words": words,
        "multiword_phrases": phrases,
        "urgency": by_tag.get("urgency", 0),
        "scam": by_tag.get("scam", 0),
        "newsish": by_tag.get("sensationalism", 0) + by_tag.get("no_source", 0),
    }

MANIPULATION_REASON_TAILS: Set[str] = {
    "urgency",
    "urgency_manipulation",
    "scam",
    "financial_scam",
    "scam_self",
}


def match_lexicon_tags(text: str) -> List[str]:
    """Return ordered unique heuristic tags found in text."""
    lowered = (text or "").lower().strip()
    if not lowered:
        return []
    hits: List[str] = []
    seen: Set[str] = set()
    for tag, pattern in SCAM_LEXICON_PATTERNS:
        if pattern.lower() in lowered and tag not in seen:
            hits.append(tag)
            seen.add(tag)
    return hits


def matched_lexicon_phrases(text: str) -> List[str]:
    """All matching patterns (for weak/strong scoring)."""
    lowered = (text or "").lower().strip()
    if not lowered:
        return []
    out: List[str] = []
    seen: Set[str] = set()
    for _tag, pattern in SCAM_LEXICON_PATTERNS:
        p = pattern.lower()
        if p in lowered and p not in seen:
            out.append(p)
            seen.add(p)
    return out


def has_strong_scam_phrase(text: str) -> bool:
    """True if any non-weak scam pattern matched (phrase or strong single)."""
    for pat in matched_lexicon_phrases(text):
        if pat in WEAK_SCAM_SINGLES:
            continue
        # scam-tagged patterns only (urgency alone is not "strong scam")
        for tag, pattern in SCAM_LEXICON_PATTERNS:
            if pattern.lower() == pat and tag == "scam":
                return True
    return False


def has_urgency_and_money(tags: Sequence[str]) -> bool:
    s = set(tags)
    return "urgency" in s and "scam" in s


def reason_tails(reasons: Sequence[str]) -> Set[str]:
    out: Set[str] = set()
    for raw in reasons or []:
        code = str(raw or "").strip().lower()
        if not code:
            continue
        tail = code.split(":", 1)[-1].strip()
        out.add(tail)
        out.add(code)
    return out


def has_manipulation_reasons(reasons: Sequence[str]) -> bool:
    tails = reason_tails(reasons)
    return bool(tails & MANIPULATION_REASON_TAILS)


def apply_scam_score_floors(
    *,
    tags: Sequence[str],
    score: float,
    mode: str = "news",
    text: str = "",
) -> float:
    """Raise score for clear scam signals (afhub-p0-03 + p1-01 + lexicon_v2 weak singles)."""
    s = float(score)
    tag_set = set(tags)
    intent_hits = {t for t in tag_set if t.startswith("intent_")}
    strong = has_strong_scam_phrase(text) if text else True
    if has_urgency_and_money(tags):
        s = max(s, 0.85)
    # OTP + authority / money = classic vishing SMS
    if "intent_otp" in intent_hits and (
        "intent_authority" in intent_hits or "intent_money_transfer" in intent_hits
    ):
        s = max(s, 0.88)
    if len(intent_hits) >= 2:
        s = max(s, 0.78)
    elif "intent_otp" in intent_hits or "intent_sbp" in intent_hits:
        s = max(s, 0.70 if mode == "sms" else 0.62)
    if mode == "sms":
        hard_intent = bool(intent_hits & {"intent_money_transfer", "intent_card", "intent_otp", "intent_sbp", "intent_prize"})
        if has_urgency_and_money(tags) or len(intent_hits) >= 2 or (strong and hard_intent):
            s = max(s, 0.72 if "scam" in tag_set or hard_intent else s)
        if "intent_otp" in intent_hits or "intent_sbp" in intent_hits:
            s = max(s, 0.70)
        if "scam" in tag_set and strong and (hard_intent or "urgency" in tag_set or len(intent_hits) >= 2):
            s = max(s, 0.72)
        elif "scam" in tag_set and strong:
            # strong phrase without second signal (e.g. «мошенник» alone)
            s = max(s, 0.72)
        elif "scam" in tag_set:
            # weak singles only
            s = max(s, 0.42)
        elif "urgency" in tag_set and len(tag_set) >= 2:
            s = max(s, 0.66)
        elif "urgency" in tag_set:
            s = max(s, 0.45)
    elif "scam" in tag_set and "urgency" in tag_set:
        s = max(s, 0.85)
    elif "scam" in tag_set and (strong or len(tag_set) >= 2):
        s = max(s, 0.66)
    return min(s, 0.999)


def anti_green_verdict(verdict: str, reasons: Sequence[str], confidence: float) -> Tuple[str, float]:
    """Never return likely_real when manipulation reasons are present and score < 0.65."""
    if verdict == "likely_fake":
        return verdict, confidence
    if not has_manipulation_reasons(reasons):
        return verdict, confidence
    if confidence >= 0.65:
        return "likely_fake", max(confidence, 0.65)
    # Floor: uncertain, not green authentic
    return "uncertain", max(float(confidence), 0.40)


def agent_pattern_dict_overlay() -> Dict[str, Tuple[str, ...]]:
    """Extra phrases merged into FakeNewsDetectionAgent FAKE_PATTERNS."""
    return {
        "urgency_manipulation": AGENT_URGENCY_PHRASES,
        "financial_scam": AGENT_FINANCIAL_PHRASES,
    }
