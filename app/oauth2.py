from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session
from app.database import get_session
from app.models import TokenData, User
from app.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm


def create_access_token(data: TokenData, expires_delta: timedelta):
    to_encode = data.model_dump().copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(
        token: str,
        credentials_exception: HTTPException
) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: int = payload.get("id")
        if id is None:
            raise credentials_exception
        return TokenData(id=id)
    except InvalidTokenError:
        raise credentials_exception


def get_current_user(
        session: SessionDep,
        token: TokenDep
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_access_token(token, credentials_exception)
    current_user = session.get(User, token_data.id)
    if current_user is None:
        raise credentials_exception
    return current_user
