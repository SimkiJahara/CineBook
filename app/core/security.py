from passlib.context import CryptContext

pwd_context= CryptContext(schemas=["bcrpyt"], deprecated= "auto")

def verify_password(plain_password: str, hashed_password: str)-> bool:
    """Verifies a plain password againts a hash."""
    return pwd_context.verify(plain_password,hashed_password)

def get_password_hash(password: str)-> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)
