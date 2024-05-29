from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as column
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.expression import false, true
from sqlalchemy import ForeignKey
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy import text
from sqlalchemy import String

from uuid import UUID

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: M[int] = column(
        primary_key=True, index=True
    )
    name: M[str] = column(unique=True, index=True)
    password: M[str]
    is_admin: M[bool] = column(server_default=false())

    accesses: M[list['UserPostAccess']] = relationship(
        back_populates='user',
        lazy='selectin',
        cascade='all, delete'
    )
    posts: M[list['Post']] = relationship(
        back_populates='author',
        lazy='selectin',
        cascade='all, delete'
    )


class Post(Base):
    __tablename__ = 'posts'

    id: M[UUID] = column(
        primary_key=True, server_default=text('gen_random_uuid()'), index=True
    )
    title: M[str] = column(unique=True)
    text: M[str]
    is_public: M[bool] = column(server_default=true())

    author_id: M[int] = column(ForeignKey('users.id'))
    author: M['User'] = relationship(back_populates='posts')

    accesses: M[list['UserPostAccess']] = relationship(
        back_populates='post',
        lazy='selectin',
        cascade='all, delete'
    )


class UserPostAccess(Base):
    __tablename__ = 'user_post_assoctiations'

    user_id: M[int] = column(ForeignKey('users.id'), primary_key=True)
    post_id: M[UUID] = column(ForeignKey('posts.id'), primary_key=True)
    level: M[str] = column(String(1))

    user: M['User'] = relationship(back_populates='accesses', foreign_keys=[user_id])
    post: M['Post'] = relationship(back_populates='accesses')

