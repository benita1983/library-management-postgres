from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Book
from app.schemas import BookCreate, BookRead

router = APIRouter()


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(payload: BookCreate, session: AsyncSession = Depends(get_session)) -> Book:
    existing = await session.execute(select(Book).where(Book.isbn == payload.isbn))
    if existing.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book with this ISBN already exists")

    book = Book(**payload.model_dump())
    book.copies_available = payload.copies_total
    session.add(book)
    await session.commit()
    await session.refresh(book)
    return book


@router.get("", response_model=list[BookRead])
async def list_books(session: AsyncSession = Depends(get_session)) -> list[Book]:
    result = await session.execute(select(Book).order_by(Book.title))
    return result.scalars().all()


@router.get("/{book_id}", response_model=BookRead)
async def get_book(book_id: int, session: AsyncSession = Depends(get_session)) -> Book:
    book = await session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book
