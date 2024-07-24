from pydantic import BaseModel
from datetime import datetime


class PaymentCreate(BaseModel):
    amount: float
    currency: str
    description: str
    time_qr_code: int
    telegram_user_id: int


class PaymentView(BaseModel):
    amount: float
    currency: str
    description: str
    url: str
    date: datetime