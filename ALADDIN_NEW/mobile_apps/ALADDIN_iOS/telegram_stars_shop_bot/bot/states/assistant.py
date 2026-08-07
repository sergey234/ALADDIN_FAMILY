from aiogram.fsm.state import State, StatesGroup


class AssistantStates(StatesGroup):
    active = State()
