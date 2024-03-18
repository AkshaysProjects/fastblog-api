from datetime import timedelta, datetime
from typing import Annotated, Optional
from pydantic import EmailStr
from bson import ObjectId

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from configs.auth_config import bcrypt_context
from jose import jwt, JWTError

from settings import settings
from dependencies import DatabaseDependency, TokenDependency
from auth import UserDependency
from models import CreateUserRequest, User, UserUpdateRequest

# Create a router for the users
router = APIRouter(prefix="/users", tags=["users"])


# Endpoint to register a new user
@router.post("/register", summary="Register a new user", response_description="User created successfully")
async def create_user(db: DatabaseDependency, create_user_request: CreateUserRequest):
    """
    Endpoint to register a new user.
    """
    # Get the collection
    collection = db.get_collection('Users')

    # Check if email already exists
    existing_user = collection.find_one({"$or": [{"email": create_user_request.email}, {
                                        "username": create_user_request.username}]})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # If email is unique, proceed with user creation
    hashed_password = bcrypt_context.hash(create_user_request.password)
    user_data = {
        "email": create_user_request.email,
        "username": create_user_request.username,
        "hashed_password": hashed_password,
        "role": create_user_request.role,
        "tags": create_user_request.tags,
    }
    result = collection.insert_one(user_data)
    return {"message": "User created successfully", "user_id": str(result.inserted_id)}


# Endpoint to log in a user
@router.post("/login", summary="Log in a user", response_description="Access token generated successfully")
async def login(db: DatabaseDependency, userdata: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Endpoint to log in a user.
    """
    # Authenticate user
    user = authenticate_user(db, userdata.username, userdata.password)

    # Create access token
    access_token = create_access_token(data={"id": str(user["_id"])})
    return {"access_token": access_token, "token_type": "bearer"}


# Endpoint to retrieve user profile
@router.get("/profile", summary="Retrieve user profile", response_description="User profile retrieved successfully")
async def get_profile(user: UserDependency):
    """
    Endpoint to retrieve user profile.
    """
    return {"id": user.id, "username": user.username, "email": user.email, "role": user.role, "tags": user.tags}


# Endpoint to update a user's profile
@router.patch("/profile", summary="Update user profile", response_description="Profile updated successfully")
async def update_profile(db: DatabaseDependency, user: UserDependency, profile: UserUpdateRequest):
    """
    Endpoint to update a user's profile.
    """

    # Filter out the None values
    profile_data = {k: v for k, v in profile.model_dump().items()
                    if v is not None}

    # If password exists, hash it
    if "password" in profile_data:
        profile_data["hashed_password"] = bcrypt_context.hash(
            profile_data.pop("password"))

    # Update the user
    collection = db.get_collection('Users')
    collection.update_one(
        {"_id": ObjectId(user.id)}, {"$set": profile_data})

    # Update the user object
    user = collection.find_one({"_id": ObjectId(user.id)})

    return {"id": str(user["_id"]), "username": user["username"], "email": user["email"], "role": user["role"], "tags": user["tags"]}


# Endpoint to add tags to a user
@router.post("/tags", summary="Add tags to a user", response_description="Tags added successfully")
async def add_tags(db: DatabaseDependency, user: UserDependency, tags: list[str]):
    """
    Endpoint to add tags to a user.
    """
    # Get the collection
    collection = db.get_collection('Users')

    # Check if tags already exist in user's tags. If yes do not add
    tags = list(set(tags) - set(user.tags))

    # If no new tags, return
    if not tags:
        return {"message": "No new tags added"}

    # Add tags to the user
    user = collection.update_one(
        {"_id": ObjectId(user.id)}, {"$addToSet": {"tags": {"$each": tags}}})
    return {"message": "Tags added successfully"}


# Endpoint to remove tags from a user
@router.delete("/tags", summary="Remove tags from a user", response_description="Tags removed successfully")
async def remove_tags(db: DatabaseDependency, user: UserDependency, tags: list[str]):
    """
    Endpoint to remove tags from a user.
    """
    # Get the collection
    collection = db.get_collection('Users')

    # Remove tags from the user
    user = collection.update_one(
        {"_id": ObjectId(user.id)}, {"$pull": {"tags": {"$in": tags}}})
    return {"message": "Tags removed successfully"}


# Endpoint to update a user's role
@router.patch("/role/{userId}", summary="Update user role", response_description="Role updated successfully")
async def update_role(db: DatabaseDependency, userId: str, user: UserDependency, role: str):
    """
    Endpoint to update a user's role.
    """
    # Check if current user is an admin
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have permission to perform this action",
        )

    # Check if the role is valid
    if role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role",
        )

    # Check if user ID is equal to current user's ID
    if userId == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot update your own role",
        )

    # Get the collection
    collection = db.get_collection('Users')

    # Update the user's role
    user = collection.update_one(
        {"_id": ObjectId(userId)}, {"$set": {"role": role}})
    return {"message": "Role updated successfully"}


# Function to authenticate a user
def authenticate_user(db: DatabaseDependency, username: str, password: str) -> Optional[dict]:
    """
    Function to authenticate a user.
    """
    # Get the collection
    collection = db.get_collection('Users')

    # Authenticate user
    user = collection.find_one({"username": username})
    if not user or not bcrypt_context.verify(password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# Function to create an access token
def create_access_token(data: dict) -> str:
    """
    Function to create an access token.
    """
    # Create a copy of the data and add an expiration time
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    # Encode the ObjectId to a string
    if "_id" in to_encode:
        to_encode["_id"] = str(to_encode["_id"])

    # Encode the data
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt
