from bson import ObjectId
from typing import Annotated
from settings import settings
from fastapi import HTTPException, status, Depends
from dependencies import DatabaseDependency, TokenDependency
from models import User
from jose import jwt, JWTError


def get_current_user(token: TokenDependency, db: DatabaseDependency) -> User:
    """
    Function to get the current user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key,
                             algorithms=[settings.algorithm])

        # Retrieve the user from the database using the ObjectId
        user_id = payload.get("id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Get the user from the database
    users = db.get_collection('Users')
    user = users.find_one({"_id": ObjectId(user_id)})

    # Decode the ObjectId to a string
    user["_id"] = str(user["_id"])

    # Change from _id to id
    user["id"] = user.pop("_id")

    # If user is None, raise an exception
    if user is None:
        raise credentials_exception

    return User(**user)


# Dependency to get the user
UserDependency = Annotated[User, Depends(get_current_user)]
