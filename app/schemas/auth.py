from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int | None = None


class User(BaseModel):
    user_id: int
    username: str
    user_timezone: str = "UTC"

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    password: str
    user_timezone: str = "UTC"


class UserInDB(User):
    hashed_password: str