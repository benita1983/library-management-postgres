from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class BookCreate(SQLModel):
    title: str
    author: str
    isbn: str
    publication_year: Optional[int] = None
    genre: Optional[str] = None
    copies_total: int = Field(default=1, ge=1)


class BookRead(BookCreate):
    id: int
    copies_available: int
    created_at: datetime


class MemberCreate(SQLModel):
    name: str
    email: str
    phone: Optional[str] = None
    membership_number: str


class MemberRead(MemberCreate):
    id: int
    created_at: datetime


class LoanCreate(SQLModel):
    book_id: int
    member_id: int
    due_date: datetime


class LoanRead(SQLModel):
    id: int
    book_id: int
    member_id: int
    issued_at: datetime
    due_date: datetime
    returned_at: Optional[datetime] = None
    status: str


class LoanReturn(SQLModel):
    loan_id: int
