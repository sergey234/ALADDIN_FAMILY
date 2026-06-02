# -*- coding: utf-8 -*-
"""Reflective prompt blocks — 4 age bands × sub-mode (p2-11)."""

from __future__ import annotations

from typing import Optional

from .wellness_age_policy import normalize_age_band
from .wellness_reflective_guards import ReflectiveGuardResult, assert_reflective_allowed
from .wellness_reflective_modes import ReflectiveMode


def _age_key(age_band: str) -> str:
    band = normalize_age_band(age_band)
    if band == "child":
        return "child"
    if band in ("parent", "senior", "adult_app"):
        return "adult"
    return "teen"


def _mode_instruction(mode: str, age_key: str, locale: str) -> str:
    loc = "en" if (locale or "ru").lower()[:2] == "en" else "ru"
    table = {
        ReflectiveMode.STRUCTURED_VIEW.value: {
            "ru": {
                "child": "Спроси, что точно случилось и что человек думает — без оценок.",
                "teen": "Отдели факт, догадку и чувство — один вопрос.",
                "adult": "Структура: факт → интерпретация → чувство; без диагноза.",
            },
            "en": {
                "child": "Ask what happened and what they think — no judging.",
                "teen": "Separate fact, guess, and feeling — one question.",
                "adult": "Structure: fact → interpretation → feeling; no diagnosis.",
            },
        },
        ReflectiveMode.BLIND_SPOTS.value: {
            "ru": {
                "teen": "Мягко назови возможный паттерн как гипотезу, не как истину.",
                "adult": "Гипотеза о паттерне + вопрос «замечаешь ли ты это?»",
            },
            "en": {
                "teen": "Gently name a possible pattern as a hypothesis, not truth.",
                "adult": "Pattern hypothesis + «do you notice this?»",
            },
        },
        ReflectiveMode.SINGLE_QUESTION.value: {
            "ru": {
                "child": "Только один короткий вопрос. Без советов.",
                "teen": "Ровно один вопрос. Без лекции.",
                "adult": "Exactly one question. No advice unless asked.",
            },
            "en": {
                "child": "Only one short question. No advice.",
                "teen": "Exactly one question. No lecture.",
                "adult": "Exactly one question. No advice unless asked.",
            },
        },
        ReflectiveMode.DEEP_EXPLORE.value: {
            "ru": {
                "teen": "Метафора или образ; один вопрос; без предсказаний и травмы.",
                "adult": "Символ как метафора; один шаг глубины; без мистики и диагноза.",
            },
            "en": {
                "teen": "Metaphor or image; one question; no predictions or trauma deep dive.",
                "adult": "Symbol as metaphor; one depth step; no mysticism or diagnosis.",
            },
        },
    }
    mode_table = table.get(mode, {})
    lang_table = mode_table.get(loc, mode_table.get("ru", {}))
    return lang_table.get(age_key, lang_table.get("teen", ""))


def build_reflective_prompt_block(
    *,
    mode: str,
    age_band: str,
    locale: str = "ru",
    reflective_enabled: bool = False,
    jung_enabled: bool = False,
    escalation_level: str = "L0",
) -> tuple[str, ReflectiveGuardResult]:
    guard = assert_reflective_allowed(
        mode,
        age_band=age_band,
        escalation_level=escalation_level,
        reflective_enabled=reflective_enabled,
        jung_enabled=jung_enabled,
    )
    if not guard.allowed:
        return "", guard
    if guard.redirect_pillar:
        return "", guard
    age_key = _age_key(age_band)
    instr = _mode_instruction(mode, age_key, locale)
    if not instr and age_key == "child":
        instr = _mode_instruction(mode, "teen", locale)
    lines = [
        "[WELLNESS REFLECTIVE]",
        f"reflective_mode={mode}",
        f"age_band={normalize_age_band(age_band)}",
        f"instruction={instr}",
    ]
    return "\n".join(lines) + "\n", guard
