"""FSM для переименования устройства в карточном пульте."""

from aiogram.fsm.state import State, StatesGroup


class VpnDeviceStates(StatesGroup):
    waiting_rename = State()
