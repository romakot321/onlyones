from fastapi import APIRouter
from fastapi import Depends
from uuid import UUID

from app.repositories.post import PostRepository
from app.repositories.user import get_request_actor
from app.schemas.post import PostCreateSchema, PostMethods
from app.schemas.post import PostPatchSchema, PostAccess
from app.schemas.post import PostGetSchema, PostListElementSchema
from app.schemas.post import UserPostAccessSchema
from app.db.tables import User

router = APIRouter(prefix='/api/post', tags=['Post'])


@router.post('', status_code=201)
async def create_post(
        schema: PostCreateSchema,
        author: User = Depends(get_request_actor),
        repository: PostRepository = Depends()
):
    return await repository.create(schema, author.id)


@router.get('', response_model=list[PostListElementSchema])
async def get_posts(
        page: int = 0,
        repository: PostRepository = Depends()
):
    return await repository.get_list(page)


@router.get('/{post_id}', response_model=PostGetSchema)
async def get_post(
        post_id: UUID,
        user: User = Depends(get_request_actor),
        repository: PostRepository = Depends(),
):
    await repository.verify_user_post_access(user.id, post_id, PostMethods.GET)
    return await repository.get(post_id)


@router.patch('/{post_id}', response_model=PostGetSchema)
async def edit_post(
        post_id: UUID,
        schema: PostPatchSchema,
        author: User = Depends(get_request_actor),
        repository: PostRepository = Depends()
):
    await repository.verify_user_post_access(author.id, post_id, PostMethods.PATCH)
    return await repository.edit(post_id, schema)


@router.delete('/{post_id}')
async def delete_post(
        post_id: UUID,
        user: User = Depends(get_request_actor),
        repository: PostRepository = Depends()
):
    await repository.verify_user_post_access(user.id, post_id, PostMethods.DELETE)
    await repository.delete(post_id)


@router.post('/{post_id}/access', response_model=UserPostAccessSchema)
async def grant_post_access(
        post_id: UUID,
        user_id: int,
        access: PostAccess,
        actor: User = Depends(get_request_actor),
        repository: PostRepository = Depends()
):
    """
    Values for access: 'r' - only read post, 'w' - read, write, delete and edit post
    'n' - no access
    """
    return await repository.grant_post_access(user_id, post_id, actor.id, access)


@router.patch('/{post_id}/access', response_model=UserPostAccessSchema)
async def edit_post_access(
        post_id: UUID,
        user_id: int,
        access: PostAccess,
        actor: User = Depends(get_request_actor),
        repository: PostRepository = Depends()
):
    """
    Values for access: 'r' - only read post, 'w' - read, write, delete and edit post
    'n' - no access
    """
    return await repository.edit_post_access(user_id, post_id, actor.id, access)

