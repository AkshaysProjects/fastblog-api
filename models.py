from pydantic import BaseModel, EmailStr, List, str
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "user"
    tags: List[str] = []


class CreateUserRequest(UserBase):
    password: str


class User(UserBase):
    id: str
    hashed_password: str


class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    tags: Optional[List[str]] = None


class AuthForm(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
