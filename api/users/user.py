from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse

from app.api.models.user_model import User, UserChangeData

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from app.config import FIREBASE_SERVICE_ACCOUNT_KEY

import json
import uuid

router = APIRouter(prefix="/users",tags=['User'])

if not firebase_admin._apps:
    firebase_info_config = json.loads(FIREBASE_SERVICE_ACCOUNT_KEY)
    cred = credentials.Certificate(firebase_info_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()


@router.get("/info/all/")
def all_payment_info():
    user_ref = db.collection('users')
    docs = user_ref.stream()
    all_users = {}
    for doc in docs:
        all_users[doc.id] = doc.to_dict()
    return JSONResponse(content = all_users, status_code = status.HTTP_200_OK)


@router.get("/info/{id}/detail/", response_model = User)
async def info_user(id: str):
    user_ref = db.collection('users')

    query = user_ref.where('id','==', id).stream()
    user_data = None
    for doc in query:
        user_data = doc.to_dict()
        break
    
    if user_data is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail = "User not found")
    
    user = User(
        id = user_data.get("id"),
        name = user_data.get("name"),
        name_telegram = user_data.get("name_telegram"),
        phone = user_data.get("phone"),
        role = user_data.get("role")
    )
    return user


@router.post("/save/")
def save_user(data:User):
    user_data = {
        "id": str(uuid.uuid1().hex),
        "name":data.name,
        "name_telegram": data.name_telegram,
        "phone":data.phone,
        "role":data.role.value
    }
    db.collection('users').document(user_data.get("id")).set(user_data)
    return JSONResponse(content = {"message": "success"}, status_code = status.HTTP_200_OK)


@router.delete("/delete/")
def delete_user(id:str):
    db.collection("users").document(id).delete()
    return JSONResponse(content = {'message':"deleted user"}, status_code = status.HTTP_200_OK)


@router.put("/change/")
def change_data_user(id:str, data:UserChangeData):
    user_change_data = {key: value for key, value in data.model_dump().items() if value is not None}

    if not user_change_data:
        return HTTPException(detail = "Not data provide for update")
    
    db.collection("users").document(id).update(user_change_data)

    return JSONResponse(content = {"message": "User data updated successfully"}, status_code = status.HTTP_200_OK)