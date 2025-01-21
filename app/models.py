from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
from sqlalchemy import text
from pydantic import EmailStr


class BasePost(SQLModel):
    title: str
    content: str
    published: bool | None = True


class Post(BasePost, table=True):
    __tablename__ = "posts"
    id: int = Field(default=None, primary_key=True,)
    owner_id: int | None = Field(nullable=False, foreign_key="users.id")
    created_at: datetime = Field(
       default_factory=datetime.utcnow,
       nullable=False,
       sa_column_kwargs={
           "server_default": text("current_timestamp(0)")
       })
    owner: "User" = Relationship(back_populates="posts")
    ratings: list["Rating"] = Relationship(back_populates="post")

    @property
    def average_rating(self) -> float:
        if not self.ratings:
            return 0.0
        return round(
            sum(r.rating for r in self.ratings) / len(self.ratings),
            2)


class PostCreate(BasePost):
    pass


class PostPublic(BasePost):
    id: int
    created_at: datetime
    owner: "UserPublic"
    average_rating: float


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(nullable=False, unique=True)
    email: EmailStr = Field(nullable=False, unique=True)
    password: str
    posts: list["Post"] = Relationship(back_populates="owner")
    created_at: datetime = Field(
       default_factory=datetime.utcnow,
       nullable=False,
       sa_column_kwargs={
           "server_default": text("current_timestamp(0)")
       })


class UserCreate(SQLModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(SQLModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime


class UserLogin(SQLModel):
    username: str
    password: str


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    id: int | None = None


class Rating(SQLModel, table=True):
    __tablename__ = "ratings"
    user_id: int | None = Field(
        default=None,
        foreign_key="users.id",
        primary_key=True,
        ondelete="CASCADE"
    )
    post_id: int | None = Field(
        default=None,
        foreign_key="posts.id",
        primary_key=True,
        ondelete="CASCADE"
    )
    rating: int = Field(ge=1, le=5)
    post: Post = Relationship(back_populates="ratings")
    created_at: datetime = Field(
       default_factory=datetime.utcnow,
       nullable=False,
       sa_column_kwargs={
           "server_default": text("current_timestamp(0)")
       })


class SitesCompaniesLink(SQLModel, table=True):
    __tablename__ = "sites_companies_links"
    site_id: int | None = Field(nullable=False, foreign_key="sites.id", primary_key=True, default=None, ondelete="CASCADE")
    company_id: int | None = Field(nullable=False, foreign_key="companies.id", primary_key=True, default=None, ondelete="CASCADE")


class Account(SQLModel, table=True):
    __tablename__ = "accounts"
    id: int | None = Field(default=None, primary_key=True)
    companies: list["Company"] = Relationship(back_populates="account")
    name: str


class Company(SQLModel, table=True):
    __tablename__ = "companies"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    account_id: int | None = Field(nullable=False, index=True, foreign_key="accounts.id")
    account: Account = Relationship(back_populates="companies")
    sites: list["Site"] = Relationship(back_populates="companies", link_model=SitesCompaniesLink)


class Site(SQLModel, table=True):
    __tablename__ = "sites"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    companies: list["Company"] = Relationship(back_populates="sites", link_model=SitesCompaniesLink)


class AccountResponse(SQLModel):
    id: int
    name: str
    companies: list["CompanyResponse"]


class CompanyResponse(SQLModel):
    id: int
    name: str
    account_id: int
    sites: list["SiteResponse"]


class SiteResponse(SQLModel):
    id: int
    name: str
