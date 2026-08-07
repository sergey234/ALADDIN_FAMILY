"""FSM: админ вводит аргументы команды после кнопки (без ручного /command)."""

from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class AdminCmdStates(StatesGroup):
    waiting_args = State()
