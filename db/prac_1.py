# /usr/bin/env python3

from sqlalchemy import Column, create_engine, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, relationship
import os
from datetime import date


engine = create_engine(
    url=os.getenv("DATABASE_URL") # type: ignore
)

Session_local = sessionmaker(engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


buy_book = Table(
    "buy_book",
    Base.metadata,
    Column("buy_id", ForeignKey("buy.buy_id")),
    Column("book_id", ForeignKey("book.book_id")),
)

buy_step = Table(
    "buy_step",
    Base.metadata,
    Column("buy_id", ForeignKey("buy.buy_id")),
    Column("step_id", ForeignKey("step.step_id")),
)


class Genre(Base):
    __tablename__ = "genre"

    genre_id: Mapped[int] = mapped_column(primary_key=True)
    name_genre: Mapped[str]

    books: Mapped[list["Book"]] = relationship(back_populates="genre")


class Author(Base):
    __tablename__ = "author"

    author_id: Mapped[int] = mapped_column(primary_key=True)
    name_author: Mapped[str]

    books: Mapped[list["Book"]] = relationship(back_populates="genre")


class City(Base):
    __tablename__ = "city"

    city_id: Mapped[int] = mapped_column(primary_key=True)
    name_city: Mapped[str]
    days_delivery: Mapped[int]

    clients: Mapped[list["Client"]] = relationship(back_populates="city")


class Book(Base):
    __tablename__ = "book"

    book_id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("author.author_id"))
    genre_id: Mapped[int] = mapped_column(ForeignKey("genre.genre_id"))
    price: Mapped[int]
    amount: Mapped[int]

    genre: Mapped[Genre] = relationship(back_populates="books")
    author: Mapped[Author] = relationship(back_populates="books")
    buys: Mapped[list["Buy"]] = relationship(secondary=buy_book)


class Client(Base):
    __tablename__ = "client"

    client_id: Mapped[int] = mapped_column(primary_key=True)
    name_client: Mapped[str]
    city_id: Mapped[int] = mapped_column(ForeignKey("city.city_id"))
    email: Mapped[str]

    city: Mapped["City"] = relationship(back_populates="clients")


class Buy(Base):
    __tablename__ = "buy"

    buy_id: Mapped[int] = mapped_column(primary_key=True)
    buy_description: Mapped[str]
    client_id: Mapped[int] = mapped_column(ForeignKey("client.client_id"))

    steps: Mapped[list["Step"]] = relationship(secondary=buy_step)


class Step(Base):
    __tablename__ = "step"

    step_id: Mapped[int] = mapped_column(primary_key=True)
    name_step: Mapped[str]


# class BuyBook(Base):
#     __tablename__ = "buy_book"
#
#     buy_book_id: Mapped[int] = mapped_column(primary_key=True)
#     buy_id: Mapped[int] = mapped_column(ForeignKey("buy.buy_id"))
#     book_id: Mapped[int] = mapped_column(ForeignKey("book.book_id"))
#     amount: Mapped[int]


# class BuyStep(Base):
#     __tablename__ = "buy_step"
#
#     buy_step_id: Mapped[int] = mapped_column(primary_key=True)
#     buy_id: Mapped[int] = mapped_column(ForeignKey("buy.buy_id"))
#     step_id: Mapped[int] = mapped_column(ForeignKey("step.step_id"))
#     date_step_beg: Mapped[date]
#     date_step_end: Mapped[date]
