from pydantic import BaseModel


class TokenPayload(BaseModel):
    user_id: int
    token_type: str
