from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Limiter, Rate, Duration

from typing import AsyncGenerator, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.repositories.repositories import UserRepository, RefreshTokenRepository
from app.schemas.token import TokenPayload
# from app.core.security import decode_token


if TYPE_CHECKING:
    from app.services.auth_service import AuthService


security = HTTPBearer()

rate_limiter = RateLimiter(limiter=Limiter(Rate(5, Duration.MINUTE)))


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db=db)


async def get_token_repo(db: AsyncSession = Depends(get_db)) -> RefreshTokenRepository:
    return RefreshTokenRepository(db=db)


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
    token_repo: RefreshTokenRepository = Depends(get_token_repo),
) -> 'AuthService':
    from app.services.auth_service import AuthService
    return AuthService(user_repo=user_repo, token_repo=token_repo)


async def get_current_token_payload(
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenPayload:
    from app.core.security import decode_token

    payload_dict = decode_token(credentials.credentials)

    if not payload_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired"
        )

    return TokenPayload(
        user_id=payload_dict['sub'],
        user_role=payload_dict['role'],
    )
