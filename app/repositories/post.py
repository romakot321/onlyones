from fastapi import Depends, HTTPException
from loguru import logger

from app.services.post import PostService
from app.schemas.post import PostMethods, PostAccess
from app.db.tables import Post


class PostRepository:
    def __init__(
            self,
            service: PostService = Depends()
    ):
        self.service = service

    async def create(self, schema, author_id):
        return await self.service.create(schema, author_id)

    async def get(self, post_id):
        return await self.service.get(id=post_id, select_in_load=Post.accesses)

    async def get_list(self, page=0):
        return await self.service.get_list(page=page)

    async def edit(self, post_id, schema):
        return await self.service.update(post_id, schema)

    async def delete(self, post_id):
        return await self.service.delete(post_id)

    async def grant_post_access(
            self,
            user_id,
            post_id,
            actor_id,
            access: PostAccess
    ):
        await self.verify_user_post_access(actor_id, post_id, PostMethods.PATCH)
        try:
            return await self.service.grant_post_access(user_id, post_id, access)
        except HTTPException as e:
            if e.status_code == 409:
                return await self.service.edit_post_access(user_id, post_id, access)
            raise e

    async def edit_post_access(
            self,
            user_id,
            post_id,
            actor_id,
            access: PostAccess
    ):
        await self.verify_user_post_access(actor_id, post_id, PostMethods.PATCH)
        return await self.service.edit_post_access(user_id, post_id, access)

    async def check_user_post_access(self, *args, **kwargs):
        try:
            await self.verify_user_post_access(*args, **kwargs)
        except HTTPException:
            return False
        return True

    async def verify_user_post_access(
            self,
            user_id,
            post_id,
            method: PostMethods
    ):
        access = await self.service.get_user_post_access(user_id=user_id, post_id=post_id)
        if access is None:
            post = await self.service.get(id=post_id, select_in_load=Post.author)
            if post.is_public and method == PostMethods.GET:
                return
            if post.author_id == user_id:
                return
        elif access.user.is_admin:
            return
        elif method.compare_with_access(access.level):
            return
        raise HTTPException(401)

