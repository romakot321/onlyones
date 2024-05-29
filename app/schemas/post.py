from pydantic import BaseModel
from uuid import UUID
from enum import Enum


class PostAccess(Enum):
    NONE = 'n'
    READ = 'r'
    READ_WRITE = 'w'

    @classmethod
    def from_value(cls, value):
        for attrname in cls._member_names_:
            attr = getattr(cls, attrname)
            if attr.value == value:
                return attr


class PostMethods(Enum):
    POST = 0
    PATCH = 1
    GET = 2
    DELETE = 3

    def compare_with_access(self, access: str | PostAccess) -> bool:
        if isinstance(access, str):
            access = PostAccess.from_value(access)
        if self in (PostMethods.POST, PostMethods.PATCH, PostMethods.DELETE) \
                and access == PostAccess.READ_WRITE:
            return True
        if self == PostMethods.GET and access in (PostAccess.READ, PostAccess.READ_WRITE):
            return True
        return False


class PostCreateSchema(BaseModel):
    title: str
    text: str
    is_public: bool


class PostPatchSchema(BaseModel):
    title: str | None = None
    text: str | None = None
    is_public: bool | None = None


class PostGetSchema(BaseModel):
    id: UUID
    title: str
    text: str
    is_public: bool
    author_id: int


class PostListElementSchema(BaseModel):
    id: UUID
    title: str

