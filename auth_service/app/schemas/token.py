from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.user import UserRole


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    user_id: int | None
    user_role: UserRole | None


class RefreshTokenSchemaResponse(BaseModel):
    id: int
    token: str
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)
