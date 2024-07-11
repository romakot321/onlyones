from pydantic import BaseModel
from enum import Enum

from app.schemas.post import PostListElementSchema


class UserPostSchema(BaseModel):
    name: str
    password: str
    is_admin: bool = False


class UserGetSchema(BaseModel):
    name: str
    is_admin: bool
    posts: list[PostListElementSchema]
    id: int


class UserGetFilterSchema(BaseModel):
    name: str | None = None
    id: int | None = None


class UserLoginSchema(BaseModel):
    name: str
    password: str


class UserTokenSchema(BaseModel):
    access_token: str
    token_type: str

