from sqlmodel import Session, create_engine
from app.config import settings


DATABASE_URL = (
    f'postgresql://{settings.database_username}:{settings.database_password}@'
    f'{settings.database_hostname}:{settings.database_port}/'
    f'{settings.database_name}'

)
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session
