import jwt
from typing import Any

from app.core.config import settings


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        return payload if payload else None

    except jwt.PyJWTError:
        return None
