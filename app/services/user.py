from fastapi import HTTPException

from .base import BaseService
from app.db.tables import User


class UserService(BaseService):
    base_table = User

    async def create(self, schema):
        return await self._create(schema)

    async def get(self, **filters):
        return await self._get_one(**filters)

    async def get_posts(self, user_id) -> list:
        user = await self._get_one(
            id=user_id,
            select_in_load=User.posts
        )
        return user.posts

