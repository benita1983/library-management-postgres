from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, Query, status
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session

from app.database import get_session
from app.models import Book, Loan, Member


async def get_book_or_404(session: AsyncSession, book_id: int) -> Book:
    result = await session.get(Book, book_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return result


async def get_member_or_404(session: AsyncSession, member_id: int) -> Member:
    result = await session.get(Member, member_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return result


async def get_loan_or_404(session: AsyncSession, loan_id: int) -> Loan:
    result = await session.get(Loan, loan_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    return result
