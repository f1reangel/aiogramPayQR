from pydantic import BaseModel
from typing import Optional
from enum import Enum
import uuid

class UserRole(Enum):
    user = "user"
    admin = 'admin'


class User(BaseModel):
    id: uuid.UUID
    name:str
    name_telegram:Optional[str] = None
    phone:Optional[str] = None
    role: UserRole

class UserChangeData(BaseModel):
    name: Optional[str] = None
    name_telegram: Optional[str] = None
    phone: Optional[str] = None

class UserChangeRole(BaseModel):
    role: UserRole