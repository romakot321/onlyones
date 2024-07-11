from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
import os

from app.services.user import UserService
from app.services.auth import AuthService, oauth2_scheme
from app.repositories.post import PostRepository
from app.schemas.user import UserPostSchema
from app.schemas.post import PostMethods


class UserRepository:
    def __init__(
            self,
            service: UserService = Depends(),
            auth: AuthService = Depends(),
            post_repository: PostRepository = Depends()  # TODO Change dep to service
    ):
        self.service = service
        self.auth = auth
        self.post_rep = post_repository

    async def create(
            self,
            schema: UserPostSchema,
            access_token: str | None = None,
    ):
        if schema.is_admin:
            self.auth.verify_admin_token(access_token)
        schema.password = self.auth.hash_password(schema.password)
        return await self.service.create(schema)

    async def get(
            self,
            username: str = None,
            user_id: int = None
    ):
        filters = {
            k: v
            for k, v in zip(('name', 'id'), (username, user_id))
            if v is not None
        }
        if not filters:
            return
        return await self.service.get(**filters)

    async def get_posts(self, user_id, actor):
        posts = await self.service.get_posts(user_id)
        return [
            p
            for p in posts
            if await self.post_rep.check_user_post_access(actor.id, p.id, PostMethods.GET)
        ]

    async def login(self, username, password):
        user = await self.get(username=username)
        return self.auth.login(user, password)

    async def get_current_user(self, token: str):
        user_id = self.auth.decode_token(token)
        return await self.get(user_id=user_id)


async def get_request_actor(
        token: str = Depends(oauth2_scheme),
        user_rep: UserRepository = Depends()
):
    return await user_rep.get_current_user(token)

