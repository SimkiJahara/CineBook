import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "18f4e284c20f7efd72e85380a2ef7c71dca25a7a797ce7de093201a3bd3e83e8"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


#def get_password_hash(password: str) -> str:
 #   return pwd_context.hash(password)

def get_password_hash(password: str) -> str:
    # --- IMPORTANT: Fix for the 72-byte limit ---
    # Encode the string to bytes, take the first 72 bytes, and pass that to hash.
    # While this fixes the server error, you should ideally validate the length
    # in your Pydantic model and return a 400 Bad Request to the user.
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncate to the maximum allowed length (72 bytes)
        # Note: This is an internal fix; Pydantic validation is better for the user.
        password_to_hash = password_bytes[:72]
    else:
        password_to_hash = password_bytes
        
    return pwd_context.hash(password_to_hash)



def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt