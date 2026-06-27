from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.auth.security import decode_token
from app.schemas.token import TokenPayload


security = HTTPBearer()


async def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenPayload:

    payload = decode_token(credentials.credentials)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Missing or invalid token',
        )

    sub = payload.get('sub')
    token_type = payload.get('token_type')

    if token_type != 'access':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Wrong token type was given',
        )

    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Missing sub',
        )

    user_id = int(sub)
    return TokenPayload(user_id=user_id, token_type=token_type)
