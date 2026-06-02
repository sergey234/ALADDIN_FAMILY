# -*- coding: utf-8 -*-
"""PHQ-lite screening (5 items) — not a diagnosis (p1-06)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .wellness_age_policy import (
    can_use_phq_lite,
    can_use_full_assessments,
    can_use_mbi_lite,
)

DISCLAIMER_RU = "Это короткий скрининг, не диагноз. При сильных переживаниях обратись к специалисту или взрослому."
DISCLAIMER_EN = "This is a short screening, not a diagnosis. If you feel very low, talk to a professional or a trusted adult."

PHQ_LITE_QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": "q1",
        "key_ru": "wellness_phq_q1",
        "key_en": "wellness_phq_q1_en",
        "text_ru": "Мало интереса или удовольствия от дел?",
        "text_en": "Little interest or pleasure in doing things?",
    },
    {
        "id": "q2",
        "key_ru": "wellness_phq_q2",
        "key_en": "wellness_phq_q2_en",
        "text_ru": "Подавленное настроение, грусть или безнадёжность?",
        "text_en": "Feeling down, sad, or hopeless?",
    },
    {
        "id": "q3",
        "key_ru": "wellness_phq_q3",
        "key_en": "wellness_phq_q3_en",
        "text_ru": "Трудности со сном (мало или слишком много)?",
        "text_en": "Trouble sleeping (too little or too much)?",
    },
    {
        "id": "q4",
        "key_ru": "wellness_phq_q4",
        "key_en": "wellness_phq_q4_en",
        "text_ru": "Усталость или мало энергии?",
        "text_en": "Feeling tired or having little energy?",
    },
    {
        "id": "q5",
        "key_ru": "wellness_phq_q5",
        "key_en": "wellness_phq_q5_en",
        "text_ru": "Плохой аппетит или переедание?",
        "text_en": "Poor appetite or overeating?",
    },
]

ANSWER_OPTIONS = [
    {"value": 0, "key_ru": "wellness_assessment_answer_never", "key_en": "wellness_assessment_answer_never"},
    {"value": 1, "key_ru": "wellness_assessment_answer_severaldays", "key_en": "wellness_assessment_answer_severaldays"},
    {"value": 2, "key_ru": "wellness_assessment_answer_morehalf", "key_en": "wellness_assessment_answer_morehalf"},
    {"value": 3, "key_ru": "wellness_assessment_answer_daily", "key_en": "wellness_assessment_answer_daily"},
]


@dataclass(frozen=True)
class PhqLiteResult:
    score: int
    severity: str
    suggest_professional: bool
    disclaimer: str


def phq_lite_schema(*, locale: str = "ru") -> Dict[str, Any]:
    try:
        from .wellness_i18n_loader import phq_lite_schema_from_i18n

        loaded = phq_lite_schema_from_i18n(locale=locale)
        if loaded:
            return loaded
    except Exception:
        pass
    loc = (locale or "ru").lower()[:2]
    questions = []
    for q in PHQ_LITE_QUESTIONS:
        questions.append(
            {
                "id": q["id"],
                "text": q["text_en"] if loc == "en" else q["text_ru"],
            }
        )
    opts = []
    for o in ANSWER_OPTIONS:
        opts.append(
            {
                "value": o["value"],
                "label_key": o["key_en"] if loc == "en" else o["key_ru"],
            }
        )
    return {
        "assessment_type": "phq_lite",
        "disclaimer": DISCLAIMER_EN if loc == "en" else DISCLAIMER_RU,
        "questions": questions,
        "answer_options": opts,
        "max_score": 15,
    }


def score_phq_lite(answers: List[int], *, locale: str = "ru") -> PhqLiteResult:
    if len(answers) != 5:
        raise ValueError("phq_lite_requires_5_answers")
    for a in answers:
        if a not in (0, 1, 2, 3):
            raise ValueError("phq_lite_invalid_answer")
    total = sum(answers)
    if total >= 10:
        severity = "moderate"
        suggest = True
    elif total >= 5:
        severity = "mild"
        suggest = False
    else:
        severity = "minimal"
        suggest = False
    loc = (locale or "ru").lower()[:2]
    return PhqLiteResult(
        score=total,
        severity=severity,
        suggest_professional=suggest,
        disclaimer=DISCLAIMER_EN if loc == "en" else DISCLAIMER_RU,
    )


def assert_phq_allowed(age_band: str) -> None:
    if not can_use_phq_lite(age_band):
        raise PermissionError("phq_lite_blocked_for_age")


def assert_full_assessment_allowed(age_band: str) -> None:
    if not can_use_full_assessments(age_band):
        raise PermissionError("assessment_blocked_for_age")


# --- PHQ-9 (9 items, 0–3) — screening, not diagnosis (p2-03) ---

PHQ9_QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": "q1",
        "text_ru": "Мало интереса или удовольствия от дел?",
        "text_en": "Little interest or pleasure in doing things?",
    },
    {
        "id": "q2",
        "text_ru": "Подавленное настроение, грусть или безнадёжность?",
        "text_en": "Feeling down, depressed, or hopeless?",
    },
    {
        "id": "q3",
        "text_ru": "Трудности со сном: засыпание, сон или слишком много сна?",
        "text_en": "Trouble falling or staying asleep, or sleeping too much?",
    },
    {
        "id": "q4",
        "text_ru": "Усталость или мало энергии?",
        "text_en": "Feeling tired or having little energy?",
    },
    {
        "id": "q5",
        "text_ru": "Плохой аппетит или переедание?",
        "text_en": "Poor appetite or overeating?",
    },
    {
        "id": "q6",
        "text_ru": "Плохое мнение о себе — что подвёл или разочаровал семью?",
        "text_en": "Feeling bad about yourself — that you are a failure or have let your family down?",
    },
    {
        "id": "q7",
        "text_ru": "Трудности с концентрацией (чтение, ТВ)?",
        "text_en": "Trouble concentrating on things, such as reading or watching television?",
    },
    {
        "id": "q8",
        "text_ru": "Двигаешься или говоришь так медленно, что другие замечают? Или наоборот — не можешь усидеть?",
        "text_en": "Moving or speaking so slowly that others could notice? Or the opposite — being fidgety or restless?",
    },
    {
        "id": "q9",
        "text_ru": "Мысли, что лучше умереть или причинить себе вред?",
        "text_en": "Thoughts that you would be better off dead, or of hurting yourself in some way?",
    },
]

# --- GAD-7 (7 items, 0–3) ---

GAD7_QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": "q1",
        "text_ru": "Нервозность, тревога или напряжение?",
        "text_en": "Feeling nervous, anxious, or on edge?",
    },
    {
        "id": "q2",
        "text_ru": "Не получается перестать волноваться или контролировать это?",
        "text_en": "Not being able to stop or control worrying?",
    },
    {
        "id": "q3",
        "text_ru": "Слишком много беспокойства по разным поводам?",
        "text_en": "Worrying too much about different things?",
    },
    {
        "id": "q4",
        "text_ru": "Трудно расслабиться?",
        "text_en": "Trouble relaxing?",
    },
    {
        "id": "q5",
        "text_ru": "Такое беспокойство, что трудно усидеть на месте?",
        "text_en": "Being so restless that it is hard to sit still?",
    },
    {
        "id": "q6",
        "text_ru": "Раздражительность или вспыльчивость?",
        "text_en": "Becoming easily annoyed or irritable?",
    },
    {
        "id": "q7",
        "text_ru": "Страх, что может случиться что-то плохое?",
        "text_en": "Feeling afraid, as if something awful might happen?",
    },
]


@dataclass(frozen=True)
class AssessmentResult:
    score: int
    severity: str
    suggest_professional: bool
    disclaimer: str
    crisis_flag: bool = False


def _build_schema(
    assessment_type: str,
    questions: List[Dict[str, Any]],
    *,
    locale: str,
    max_score: int,
) -> Dict[str, Any]:
    loc = (locale or "ru").lower()[:2]
    qs = [
        {
            "id": q["id"],
            "text": q["text_en"] if loc == "en" else q["text_ru"],
        }
        for q in questions
    ]
    opts = [
        {
            "value": o["value"],
            "label_key": o["key_en"] if loc == "en" else o["key_ru"],
        }
        for o in ANSWER_OPTIONS
    ]
    return {
        "assessment_type": assessment_type,
        "disclaimer": DISCLAIMER_EN if loc == "en" else DISCLAIMER_RU,
        "questions": qs,
        "answer_options": opts,
        "max_score": max_score,
    }


def _validate_answers(answers: List[int], expected: int) -> None:
    if len(answers) != expected:
        raise ValueError(f"{expected}_answers_required")
    for a in answers:
        if a not in (0, 1, 2, 3):
            raise ValueError("invalid_answer_value")


def phq9_schema(*, locale: str = "ru") -> Dict[str, Any]:
    return _build_schema("phq9", PHQ9_QUESTIONS, locale=locale, max_score=27)


def gad7_schema(*, locale: str = "ru") -> Dict[str, Any]:
    return _build_schema("gad7", GAD7_QUESTIONS, locale=locale, max_score=21)


def score_phq9(answers: List[int], *, locale: str = "ru") -> AssessmentResult:
    _validate_answers(answers, 9)
    total = sum(answers)
    q9 = answers[8]
    crisis_flag = q9 >= 1
    if total >= 20:
        severity = "severe"
    elif total >= 15:
        severity = "moderately_severe"
    elif total >= 10:
        severity = "moderate"
    elif total >= 5:
        severity = "mild"
    else:
        severity = "minimal"
    suggest = total >= 10 or crisis_flag
    loc = (locale or "ru").lower()[:2]
    return AssessmentResult(
        score=total,
        severity=severity,
        suggest_professional=suggest,
        disclaimer=DISCLAIMER_EN if loc == "en" else DISCLAIMER_RU,
        crisis_flag=crisis_flag,
    )


def score_gad7(answers: List[int], *, locale: str = "ru") -> AssessmentResult:
    _validate_answers(answers, 7)
    total = sum(answers)
    if total >= 15:
        severity = "severe"
    elif total >= 10:
        severity = "moderate"
    elif total >= 5:
        severity = "mild"
    else:
        severity = "minimal"
    suggest = total >= 10
    loc = (locale or "ru").lower()[:2]
    return AssessmentResult(
        score=total,
        severity=severity,
        suggest_professional=suggest,
        disclaimer=DISCLAIMER_EN if loc == "en" else DISCLAIMER_RU,
        crisis_flag=False,
    )


# --- MBI-lite burnout (5 items, parent/senior) — p2-06 ---

MBI_LITE_QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": "q1",
        "text_ru": "Чувствую эмоциональное истощение из-за работы/забот?",
        "text_en": "I feel emotionally drained from work or caregiving?",
    },
    {
        "id": "q2",
        "text_ru": "К концу дня чувствую себя выжатым(ой)?",
        "text_en": "I feel worn out at the end of the day?",
    },
    {
        "id": "q3",
        "text_ru": "Утром трудно собраться с силами на дела?",
        "text_en": "It is hard to get going in the morning?",
    },
    {
        "id": "q4",
        "text_ru": "Стал(а) более циничным(ой) или отстранённым(ой)?",
        "text_en": "I have become more cynical or detached?",
    },
    {
        "id": "q5",
        "text_ru": "Чувствую, что не справляюсь с нагрузкой?",
        "text_en": "I feel I cannot cope with my load?",
    },
]

MBI_DISCLAIMER_RU = (
    "Это короткий скрининг выгорания, не диагноз. "
    "При сильной усталости — отдых и специалист при необходимости."
)
MBI_DISCLAIMER_EN = (
    "This is a short burnout screening, not a diagnosis. "
    "If exhaustion is severe, rest and professional support may help."
)


def assert_mbi_allowed(age_band: str) -> None:
    if not can_use_mbi_lite(age_band):
        raise PermissionError("mbi_lite_blocked_for_age")


def mbi_lite_schema(*, locale: str = "ru") -> Dict[str, Any]:
    return _build_schema("mbi_lite", MBI_LITE_QUESTIONS, locale=locale, max_score=15)


def score_mbi_lite(answers: List[int], *, locale: str = "ru") -> AssessmentResult:
    _validate_answers(answers, 5)
    total = sum(answers)
    if total >= 12:
        severity = "high_burnout_risk"
        suggest = True
    elif total >= 8:
        severity = "moderate"
        suggest = True
    elif total >= 4:
        severity = "mild"
        suggest = False
    else:
        severity = "minimal"
        suggest = False
    loc = (locale or "ru").lower()[:2]
    return AssessmentResult(
        score=total,
        severity=severity,
        suggest_professional=suggest,
        disclaimer=MBI_DISCLAIMER_EN if loc == "en" else MBI_DISCLAIMER_RU,
        crisis_flag=False,
    )
