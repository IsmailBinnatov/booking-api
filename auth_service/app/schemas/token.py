from pydantic import BaseModel

from auth_service.app.models.user import UserRole


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    user_id: int | None
    user_role: UserRole | None
