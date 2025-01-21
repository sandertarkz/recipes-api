from typing import Annotated
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.models import (
    Account,
    AccountResponse,
    # Site,
    Company,
)
from app.database import get_session


SessionDep = Annotated[Session, Depends(get_session)]
router = APIRouter(prefix="/test", tags=["Test"])


@router.get("/", response_model=list[AccountResponse])
def get_posts(
    session: SessionDep,
):
    statement = select(Account).options(
        selectinload(Account.companies).selectinload(Company.sites)
    )
    result = session.exec(statement).all()
    print("=====================================================================================")
    print(result[0].companies[0].sites[0])
    print("=====================================================================================")
    return list(result)
