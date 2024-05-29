from fastapi import Response, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseService
from app.db.base import get_session
from app.db.tables import Post, UserPostAccess
from app.schemas.post import PostAccess
from app.services.post_access import PostAccessService


class PostService(BaseService):
    base_table = Post

    def __init__(
            self,
            response: Response = Response,
            session: AsyncSession = Depends(get_session),
            post_access_service: PostAccessService = Depends()
    ):
        super().__init__(response, session)
        self.post_access_service = post_access_service

    async def create(self, schema, author_id):
        schema = schema.model_dump() | {'author_id': author_id}
        return await self._create(**schema)

    async def get(self, **filters):
        return await self._get_one(**filters)

    async def update(self, post_id, schema):
        return await self._update(post_id, schema)

    async def delete(self, post_id):
        return await self._delete(post_id)

    async def edit_post_access(self, user_id, post_id, access: PostAccess):
        return await self.post_access_service.update(user_id, post_id, access)

    async def get_user_post_access(self, user_id, post_id) -> UserPostAccess | None:
        return await self.post_access_service.get(user_id, post_id)

    async def grant_post_access(self, user_id, post_id, access: PostAccess) -> UserPostAccess:
        return await self.post_access_service.create(user_id, post_id, access)

