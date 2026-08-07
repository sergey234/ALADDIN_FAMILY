from aiogram.fsm.state import State, StatesGroup


class CheckoutStates(StatesGroup):
    waiting_recipient = State()
    waiting_verify_username = State()
    waiting_confirm = State()


class BuyStarsCustomStates(StatesGroup):
    waiting_qty = State()


class TopupStates(StatesGroup):
    waiting_custom_amount = State()


class ApiKeyStates(StatesGroup):
    waiting_contact = State()
    waiting_comment = State()


class RefWithdrawStates(StatesGroup):
    waiting_crypto_target = State()


class FeedbackStates(StatesGroup):
    waiting_negative_comment = State()
    waiting_suggestion = State()
