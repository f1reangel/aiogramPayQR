from pydantic import BaseModel
from datetime import datetime


class PaymentCreate(BaseModel):
    amount: float
    currency: str
    description: str
    time_qr_code: int


class PaymentView(BaseModel):
    amount: float
    currency: str
    description: str
    url: str
    date: datetime