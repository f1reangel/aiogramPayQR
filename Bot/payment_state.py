from aiogram.fsm.state import StatesGroup, State

class Payment(StatesGroup):
    amount = State()
    currency = State()
    description = State()
    time_qr_code = State()