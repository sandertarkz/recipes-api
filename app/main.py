from typing import Annotated
from fastapi import Depends, FastAPI
from sqlmodel import Session
from app.database import get_session
from app.routes import post, user, auth, test


SessionDep = Annotated[Session, Depends(get_session)]
app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(post.router)
app.include_router(test.router)
