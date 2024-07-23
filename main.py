from fastapi import FastAPI
from app.api.payments import payment
app = FastAPI()

app.include_router(payment.router)