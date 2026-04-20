from aiogram.fsm.state import State, StatesGroup


class CheckoutStates(StatesGroup):
    waiting_recipient = State()
    waiting_verify_username = State()
    waiting_confirm = State()


class SellStates(StatesGroup):
    waiting_stars_amount = State()


class TopupStates(StatesGroup):
    waiting_custom_amount = State()


class ApiKeyStates(StatesGroup):
    waiting_contact = State()
    waiting_comment = State()
