from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, col, select
from app.models import (
    Post,
    PostCreate,
    PostPublic,
    Rating,
    TokenData,
)
from app.database import get_session
from app.oauth2 import get_current_user
from fastapi_pagination import Page, paginate



SessionDep = Annotated[Session, Depends(get_session)]
CurrentUserDep = Annotated[TokenData, Depends(get_current_user)]
router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("", response_model=PostPublic)
def create_post(
    post: PostCreate,
    session: SessionDep,
    current_user: CurrentUserDep
):
    post_db = Post(owner_id=current_user.id, **post.model_dump())
    session.add(post_db)
    session.commit()
    session.refresh(post_db)
    return post_db


@router.get("", response_model=Page[PostPublic])
def get_posts(
    session: SessionDep,
    limit: int = 10,
    offset: int = 0,
    search: str | None = ""
) -> Page[PostPublic]:
    statement = select(Post)

    if search:
        statement = statement.where(col(Post.title).contains(search))

    posts = session.exec(statement)
    return paginate(list(posts))


@router.get("/{id}", response_model=PostPublic)
def get_post(id: int, session: SessionDep):
    post = session.get(Post, id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found")
    return post


@router.delete("/{id}", response_class=Response)
def delete_post(
    id: int,
    session: SessionDep,
    current_user: CurrentUserDep
) -> Response:
    post = session.get(Post, id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found")
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action"
        )
    session.delete(post)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=PostPublic)
def update_post(
    id: int,
    session: SessionDep,
    updated_post: PostCreate,
    current_user: CurrentUserDep
):
    post = session.get(Post, id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found")
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action"
        )
    update_data = updated_post.model_dump(exclude_unset=True)
    post.sqlmodel_update(update_data)
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


@router.post("/{id}/rate", response_model=PostPublic)
def rate_post(
    id: int,
    rating: int,
    session: SessionDep,
    current_user: CurrentUserDep
):
    post = session.get(Post, id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found")
    if rating < 1 or rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    post.ratings.append(Rating(user_id=current_user.id, rating=rating))
    session.add(post)
    session.commit()
    session.refresh(post)
    return post
