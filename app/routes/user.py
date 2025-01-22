from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
from app.models import User, UserCreate, UserPublic
from app.database import get_session
from app.utils import hash_password


SessionDep = Annotated[Session, Depends(get_session)]
router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserPublic)
def create_user(user: UserCreate, session: SessionDep):
    hashed_password = hash_password(user.password)
    user.password = hashed_password
    new_user = User(**user.model_dump())
    session.add(new_user)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        # Check if the error is due to the unique constraint on email
        if 'email' in str(e.orig):
            raise HTTPException(status_code=400, detail="Email already registered")
        elif 'username' in str(e.orig):
            raise HTTPException(status_code=400, detail="Username already taken")
        else:
            # Re-raise the exception if it's a different IntegrityError
            raise
    session.refresh(new_user)
    return new_user


@router.get("/{id}", response_model=UserPublic)
def get_user(id: int, session: SessionDep):
    user = session.get(User, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")
    return user
