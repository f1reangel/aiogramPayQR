from fastapi import FastAPI
from app.api.payments import payment
from app.api.users import user
app = FastAPI()

app.include_router(payment.router)
app.include_router(user.router)