import random
import string
from datetime import datetime, timedelta

from jose import JWTError, jwt

from agora.core.config import settings

ALGORITHM = "HS256"


def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
