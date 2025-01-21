from sqlmodel import Session, create_engine
from app.config import settings


DATABASE_URL = (
    f'postgresql://{settings.db_user}:{settings.db_password}@'
    f'{settings.db_host}:{settings.db_port}/'
    f'{settings.db_name}'

)
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session
