from app.repositories.repositories import UserRepository, RefreshTokenRepository
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.schemas.user import UserCreate, UserLogin
from app.models.user import User
from app.models.security import RefreshToken as RefreshTokenModel


class AuthService:
    def __init__(self, user_repo: UserRepository, token_repo: RefreshTokenRepository):
        self.user_repo = user_repo
        self.token_repo = token_repo

    async def register_user(self, user_data: UserCreate) -> User | None:
        user_exists = await self.user_repo.get_by_email(user_data.email)
        if user_exists:
            return None

        hashed_pw = hash_password(user_data.password)

        user_dict = user_data.model_dump()
        user_dict.pop('password')
        user_dict['hashed_password'] = hashed_pw

        return await self.user_repo.create(user_dict)

    async def authenticate_user(self, login_data: UserLogin) -> User | None:
        user = await self.user_repo.get_by_email(login_data.email)
        if (
            not user or
            not verify_password(login_data.password, user.hashed_password)
        ):
            return None

        return user

    async def create_token_pair(self, user: User) -> dict:
        token_data = {
            'sub': str(user.id),
            'email': user.email,
            'role': user.role,
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        await self.token_repo.delete_by_user_id(user.id)

        refresh_token_obj = RefreshTokenModel(
            token=refresh_token,
            user=user,
        )

        await self.token_repo.create(refresh_token_obj)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
        }

    async def refresh_access_token(self, refresh_token: str) -> dict | None:
        payload = decode_token(refresh_token)
        if not payload:
            return None

        user_id = int(payload.get('sub'))
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None

        return await self.create_token_pair(user)
