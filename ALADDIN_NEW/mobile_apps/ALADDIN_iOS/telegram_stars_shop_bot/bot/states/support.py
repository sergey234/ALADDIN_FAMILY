"""FSM: пользователь пишет обращение в поддержку (тикет → только админам)."""

from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class SupportStates(StatesGroup):
    waiting_message = State()
