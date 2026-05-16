from collections.abc import Sequence

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, RefreshToken


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.scalar(select(User).where(User.email == email))
        return result

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.scalar(select(User).where(User.id == user_id))
        return result

    async def create(self, user_data: dict) -> User:
        new_user = User(**user_data)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def delete_by_user_id(self, user_id: int):
        stmt = delete(RefreshToken).where(RefreshToken.user_id == user_id)
        await self.db.execute(stmt)
        await self.db.commit()

    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        self.db.add(refresh_token)
        await self.db.commit()
        await self.db.refresh(refresh_token)
        return refresh_token
