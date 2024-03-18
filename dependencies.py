from typing import Annotated
from fastapi import Depends
from database import get_db
from pymongo.database import Database
from configs.auth_config import oauth2_scheme
from models import User

# Dependency to get the database
DatabaseDependency = Annotated[Database, Depends(get_db)]

# Dependency to get the access token
TokenDependency = Annotated[str, Depends(oauth2_scheme)]
