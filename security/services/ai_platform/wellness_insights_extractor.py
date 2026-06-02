# -*- coding: utf-8 -*-
"""Post-session insight: understood / observe / next step (p2-16)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ExtractedInsight:
    understood: str
    observe_text: str
    next_step_text: str
    source: str = "exercise"


def _collect_answer_texts(answers: List[Dict[str, Any]]) -> List[str]:
    out: List[str] = []
    for row in answers or []:
        text = str(row.get("text") or row.get("answer") or "").strip()
        if text:
            out.append(text)
    return out


def extract_insight_from_exercise(
    answers: List[Dict[str, Any]],
    *,
    pillar: str,
    locale: str = "ru",
) -> ExtractedInsight:
    """Rule-based extractor (no LLM) — timeline + recap continuity."""
    loc = (locale or "ru").lower()[:2]
    texts = _collect_answer_texts(answers)
    observe = texts[-1][:280] if texts else ""
    joined = " ".join(texts).lower()

    if loc == "en":
        understood = "You named what matters right now."
        if "thought" in joined or pillar == "cognitive":
            understood = "You separated a thought from the feeling."
        elif pillar == "behavioral":
            understood = "You chose one doable step."
        elif pillar == "jung":
            understood = "You looked at a symbol as a metaphor."
        if not observe:
            observe = "Finished the exercise"
        next_step = "Tomorrow, notice one small thing — no pressure."
        if pillar == "behavioral":
            next_step = "Repeat the if-then once tomorrow — tiny counts."
        elif pillar == "cognitive":
            next_step = "When the thought returns, name it gently once."
    else:
        understood = "Ты назвал(а), что сейчас важно."
        if pillar == "cognitive" or "мысл" in joined:
            understood = "Ты отделил(а) мысль от чувства."
        elif pillar == "behavioral":
            understood = "Ты выбрал(а) один выполнимый шаг."
        elif pillar == "jung":
            understood = "Ты посмотрел(а) на образ как на метафору."
        if not observe:
            observe = "Завершили упражнение"
        next_step = "Завтра можно заметить одну маленькую вещь — без давления."
        if pillar == "behavioral":
            next_step = "Завтра один раз повтори if-then — маленькое считается."
        elif pillar == "cognitive":
            next_step = "Когда мысль вернётся — мягко назови её один раз."

    return ExtractedInsight(
        understood=understood,
        observe_text=observe,
        next_step_text=next_step,
    )


def save_extracted_insight(
    store: Any,
    user_id: str,
    extracted: ExtractedInsight,
    *,
    pillar: str,
) -> Dict[str, Any]:
    from datetime import datetime

    observe = extracted.observe_text
    if extracted.understood and observe:
        observe = f"{extracted.understood} — {observe}"
    elif extracted.understood:
        observe = extracted.understood[:280]
    row = store.save_wellness_insight(
        user_id,
        pillar=pillar,
        observe_text=observe[:280],
        next_step_text=extracted.next_step_text,
        source=extracted.source,
    )
    store.upsert_wellness_settings(
        user_id,
        last_session_completed_at=datetime.utcnow().isoformat(),
    )
    return row
