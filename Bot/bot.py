import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from app.Bot.payment_state import Payment
from app.config import TOKEN_TELEGRAM_BOT
import requests

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN_TELEGRAM_BOT)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello! Use /create to start creating a payment.")

@dp.message(StateFilter(None), Command("create"))
async def cmd_create(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Payment.amount)
    await message.answer(text="Enter amount:")

@dp.message(Payment.amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(amount=amount)
        await state.set_state(Payment.currency)
        await message.answer(f"Amount: {amount}\nEnter currency:")
    except ValueError:
        await message.answer("Please enter a valid number for the amount.")

@dp.message(Payment.currency)
async def process_currency(message: types.Message, state: FSMContext):
    currency = message.text.upper()
    await state.update_data(currency=currency)
    await state.set_state(Payment.description)
    await message.answer(f"Currency: {currency}\nEnter description:")

@dp.message(Payment.description)
async def process_description(message: types.Message, state: FSMContext):
    description = message.text
    await state.update_data(description=description)
    await state.set_state(Payment.time_qr_code)
    await message.answer(f"Description: {description}\nEnter QR code validity time in minutes:")

@dp.message(Payment.time_qr_code)
async def process_time_qr_code(message: types.Message, state: FSMContext):
    time_qr_code = int(message.text)
    user_id = message.from_user.id
    await state.update_data(time_qr_code=time_qr_code, telegram_user_id=user_id)
    data = await state.get_data()
    payload = {
            "amount": data['amount'],
            "currency": data['currency'],
            "description": data['description'],
            "time_qr_code": data['time_qr_code'],
            "telegram_user_id": data['telegram_user_id']
    }
        
    response = requests.post("http://127.0.0.1:8000/payments/save/", json=payload)

    if response.status_code == 202:
        result = response.json()
        await message.answer(f"Payment created successfully. Order ID: {result['order_id']}, {result['url']}")
    else:
        await message.answer(f"Failed to create payment. Error: {response.text}")
        await state.clear()

@dp.message(Command("cancel"))
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer("Operation cancelled.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
