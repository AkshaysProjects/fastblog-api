from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

# Create a context for bcrypt
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create a scheme for OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")
