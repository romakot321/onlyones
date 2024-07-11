from fastapi import APIRouter
from fastapi import Depends
from fastapi import Header
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.user import UserPostSchema
from app.schemas.user import UserGetSchema
from app.schemas.user import UserGetFilterSchema
from app.schemas.post import PostListElementSchema
from app.repositories.user import UserRepository, get_request_actor


router = APIRouter(prefix='/api/user', tags=['User'])


@router.post('', status_code=201, response_model=UserGetSchema)
async def create_user(
        schema: UserPostSchema,
        access_token: str | None = Header(default=None),
        repository: UserRepository = Depends()
):
    """Provide access token only if create admin"""
    return await repository.create(schema, access_token)


@router.get('', response_model=UserGetSchema)
async def get_user(
        schema: UserGetFilterSchema = Depends(),
        actor=Depends(get_request_actor),
        repository: UserRepository = Depends()
):
    """If filters not specified then get user by access_token"""
    user = await repository.get(username=schema.name, user_id=schema.id)
    if user is not None:
        return user
    return actor


@router.post('/login')
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        repository: UserRepository = Depends()
):
    return await repository.login(form_data.username, form_data.password)


@router.get('/{user_id}/posts', response_model=list[PostListElementSchema])
async def get_user_posts(
        user_id: int,
        actor=Depends(get_request_actor),
        repository: UserRepository = Depends()
):
    return await repository.get_posts(user_id, actor)

