from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models import Token, TokenData, User, UserLogin
from app.database import get_session
from app.oauth2 import create_access_token
from app.utils import verify_password


ACCESS_TOKEN_EXPIRE_MINUTES = 30
SessionDep = Annotated[Session, Depends(get_session)]
router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=Token)
def create_user(user_credentials: UserLogin, session: SessionDep):
    statement = select(User).where(User.username == user_credentials.username)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials")

    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=TokenData(id=user.id), expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
