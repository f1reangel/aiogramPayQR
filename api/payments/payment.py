from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request

from app.api.models.payment_model import PaymentCreate, PaymentView
from app.config import *
from app.api.payments.helper import get_qr_code

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore, storage

from datetime import timezone, datetime

from liqpay import LiqPay
from aiogram import Bot

import json
import base64
import hashlib
import uuid

router = APIRouter(prefix="/payments", tags=["Payment"])
firebase_info_config = json.loads(FIREBASE_SERVICE_ACCOUNT_KEY)
firebase_info_storage_bucket = json.loads(STORAGE_BUCKET_URL)

cred = credentials.Certificate(firebase_info_config)
app = firebase_admin.initialize_app(cred, firebase_info_storage_bucket)
telegram_bot = Bot(token=TOKEN_TELEGRAM_BOT)
db = firestore.client()
bucket = storage.bucket()

@router.get("/all/info/")
def all_payment_info():
    payment_ref = db.collection('payment')
    docs = payment_ref.stream()
    all_payments = {}
    for doc in docs:
        all_payments[doc.id] = doc.to_dict()
    return JSONResponse(content=all_payments, status_code=status.HTTP_200_OK)

@router.get("/info/{order_id}/detail/", response_model=PaymentView)
async def info_detail_payment(order_id: str):
    payment_ref = db.collection('payment')
    query = payment_ref.where('order_id', '==', order_id).stream()
    payment_data = None
    for doc in query:
        payment_data = doc.to_dict()
        break 

    if payment_data is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    date_str = payment_data.get("date_time")
    if date_str:
        date_str = date_str.replace(',', 'T')

    payment = PaymentView(
        amount=float(payment_data.get("amount")),
        currency=payment_data.get("currency"),
        description=payment_data.get("description"),
        url=payment_data.get("url"),
        date=date_str
    )
    return payment

@router.post("/save/")
def save_payment(data: PaymentCreate):
    liqpay = LiqPay(PUBLIC_LIQPAY_KEY, PRIVATE_LIQPAY_KEY)
    order_id = uuid.uuid4().hex
    data.time_qr_code = int(data.time_qr_code * 60)

    if data.amount < 0:
        raise HTTPException(status_code=400, detail="Amount must be a positive number")

    pay_params = {
        "action": "payqr",
        "version": "3",
        "amount": int(data.amount),
        "currency": data.currency,
        "description": data.description,
        "order_id": str(order_id),
        "server_url": "https://8245-194-44-45-59.ngrok-free.app/payments/webhook/",
        "date_time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        "time_qr_code": data.time_qr_code,
        "telegram_user_id": data.telegram_user_id
    }
    res = liqpay.api("request", pay_params)

    if res and res.get('status') == 'wait_qr':
        pay_params['status'] = res.get('status')
        current_time = int(datetime.now(tz=timezone.utc).timestamp())
        qr_url = res.get('qr_code')
        qr_image = get_qr_code(qr_url)
        blob = bucket.blob(f'{order_id}_qr.png')
        blob.upload_from_file(qr_image, content_type='image/png')

        download_url = blob.generate_signed_url(expiration=data.time_qr_code + current_time)

        pay_params['url'] = download_url
        pay_params['url_qr_code'] = res.get("qr_code")
        db.collection('payment').document(order_id).set(pay_params)

        return JSONResponse(content={'message': 'Payment processing started', 'order_id': order_id, 'url': download_url}, status_code=status.HTTP_202_ACCEPTED)
    else:
        return JSONResponse(content={"message": 'Payment not created'}, status_code=status.HTTP_400_BAD_REQUEST)

@router.post("/webhook/")
async def webhook(request: Request):
    form_data = await request.form()
    data = form_data.get('data')
    signature = form_data.get('signature')

    if not data or not signature:
        raise HTTPException(status_code=400, detail="Invalid request")

    liqpay = LiqPay(PUBLIC_LIQPAY_KEY, PRIVATE_LIQPAY_KEY)
    generated_signature = base64.b64encode(
        hashlib.sha1((PRIVATE_LIQPAY_KEY + data + PRIVATE_LIQPAY_KEY).encode()).digest()
    ).decode()

    if generated_signature == signature:
        response = liqpay.decode_data_from_str(data)
        payment_status = response.get('status')
        order_id = response.get('order_id')

        payment_ref = db.collection("payment").document(order_id)
        payment_data = payment_ref.get().to_dict()

        if payment_data is None:
            raise HTTPException(status_code=404, detail="Payment not found")

        if payment_status == 'success':
            payment_ref.update({'status': payment_status})
            telegram_user_id = payment_data.get('telegram_user_id')
            if telegram_user_id:
                await telegram_bot.send_message(telegram_user_id, f"Payment successful! Order ID: {order_id}")
            return JSONResponse(content={'message': 'Success', 'order_id': order_id}, status_code=status.HTTP_200_OK)
        else:
            payment_ref.update({'status': payment_status})
            return JSONResponse(content={'message': 'Payment status updated', 'order_id': order_id}, status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(status_code=400, detail="Invalid signature")

@router.delete("/delete/")
def delete_doc(order_id: str):
    db.collection("payment").document(order_id).delete()
    return JSONResponse(content = {"message":"deleted document"}, status_code = status.HTTP_200_OK)