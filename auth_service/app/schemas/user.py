from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.user import UserRole
from app.schemas.token import RefreshTokenSchemaResponse


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=15)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=4, max_length=15)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    refresh_tokens: list[RefreshTokenSchemaResponse]

    model_config = ConfigDict(from_attributes=True)


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(from_attributes=True)
