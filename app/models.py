from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String
from sqlmodel import Field, Relationship, SQLModel


class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(index=True, unique=True)
    phone: Optional[str] = None
    membership_number: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    loans: list["Loan"] = Relationship(back_populates="member")


class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    author: str = Field(index=True)
    isbn: str = Field(unique=True, index=True, sa_column=String(length=32))
    publication_year: Optional[int] = None
    genre: Optional[str] = None
    copies_total: int = Field(default=1, ge=1)
    copies_available: int = Field(default=1, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    loans: list["Loan"] = Relationship(back_populates="book")


class Loan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="book.id", index=True)
    member_id: int = Field(foreign_key="member.id", index=True)
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    due_date: datetime = Field(default_factory=datetime.utcnow)
    returned_at: Optional[datetime] = None
    status: str = Field(default="borrowed")

    book: Optional[Book] = Relationship(back_populates="loans")
    member: Optional[Member] = Relationship(back_populates="loans")
