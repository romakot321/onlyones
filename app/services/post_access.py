from .base import BaseService
from app.db.tables import Post, UserPostAccess
from app.schemas.post import PostAccess


class PostAccessService(BaseService):
    base_table = UserPostAccess

    async def update(self, user_id, post_id, access: PostAccess):
        post_access = await self.get(user_id=user_id, post_id=post_id)
        return await self._update_obj(post_access, user_id=user_id, post_id=post_id, level=access.value)

    async def get(self, user_id, post_id) -> UserPostAccess | None:
        return await self._get_one(
            user_id=user_id,
            post_id=post_id,
            mute_not_found_exception=True,
            select_in_load=[UserPostAccess.user, UserPostAccess.post]
        )

    async def create(self, user_id, post_id, access: PostAccess) -> UserPostAccess:
        return await self._create(user_id=user_id, post_id=post_id, level=access.value)

