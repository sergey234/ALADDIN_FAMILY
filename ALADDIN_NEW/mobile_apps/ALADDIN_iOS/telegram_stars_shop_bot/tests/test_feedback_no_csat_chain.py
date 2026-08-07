"""CSAT после фонового NPS отключён; post-order NPS остаётся."""

from __future__ import annotations

import inspect
from pathlib import Path

from bot.handlers import common as common_handlers
from bot.keyboards.shop_kb import feedback_nps_kb
from bot.services.post_order_feedback import NPS_PROMPT_TEXT, schedule_post_order_nps_prompt


def test_background_nps_handler_does_not_prompt_csat() -> None:
    src = inspect.getsource(common_handlers.feedback_nps_callback)
    assert "удовлетворенность" not in src.lower()
    assert "feedback_csat_kb" not in src
    assert "fb:csat:" not in src
    assert "Спасибо за оценку" in src


def test_legacy_csat_callback_does_not_save_score() -> None:
    src = inspect.getsource(common_handlers.feedback_csat_callback)
    assert "save_feedback" not in src
    assert "kind=\"csat\"" not in src and "kind='csat'" not in src


def test_post_order_nps_still_present() -> None:
    assert "NPS" in NPS_PROMPT_TEXT
    assert "0-10" in NPS_PROMPT_TEXT or "0–10" in NPS_PROMPT_TEXT
    assert callable(schedule_post_order_nps_prompt)
    kb = feedback_nps_kb(order_id=144)
    # aiogram markup: callbacks fb:n:144:N
    raw = str(kb.model_dump() if hasattr(kb, "model_dump") else kb)
    assert "fb:n:144:10" in raw or any(
        (btn.callback_data or "").startswith("fb:n:144:")
        for row in kb.inline_keyboard
        for btn in row
    )


def test_common_module_has_no_csat_prompt_copy() -> None:
    text = Path(common_handlers.__file__).read_text(encoding="utf-8")
    assert "удовлетворенность (CSAT)" not in text
    assert "feedback_csat_kb" not in text
