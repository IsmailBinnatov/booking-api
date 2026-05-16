from fastapi import Depends

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.repositories.repositories import UserRepository, RefreshTokenRepository
from app.services.auth_service import AuthService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_repo(db: AsyncSession = Depends(get_db)):
    return UserRepository(db=db)


async def get_token_repo(db: AsyncSession = Depends(get_db)):
    return RefreshTokenRepository(db=db)


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
    token_repo: RefreshTokenRepository = Depends(get_token_repo),
):
    return AuthService(user_repo=user_repo, token_repo=token_repo)
