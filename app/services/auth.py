from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Union

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from app.schemas.user import UserTokenSchema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")


class AuthService:
    ADMIN_token = os.getenv('ADMIN_ACCESS_TOKEN', '')
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = "3acf14faaa69293b0df24afebc611348e136d00d61c763f982056ac4407f0ce2"
    ALGORITHM = "HS256"

    @classmethod
    def verify_admin_token(cls, token):
        """Raise error for invalid token"""
        if token != cls.ADMIN_token:
            raise HTTPException(401)

    @classmethod
    def hash_password(cls, password: str):
        return cls.pwd_context.hash(password)

    @classmethod
    def compare_password(cls, password: str, user_password: str):
        print(password, user_password)
        return cls.pwd_context.verify(password, user_password)

    def login(self, user, password):
        if not self.compare_password(password, user.password):
            raise HTTPException(404)
        token = self.create_token({'sub': user.id})
        return UserTokenSchema(access_token=token, token_type='bearer')

    def create_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def decode_token(self, token: str) -> int:
        """Return user id"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            user_id: int = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except InvalidTokenError:
            raise credentials_exception
        return user_id

