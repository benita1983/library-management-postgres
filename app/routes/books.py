from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Book, Loan, Member
from app.schemas import BookCreate, BookRead, LoanCreate, LoanRead, MemberCreate, MemberRead

router = APIRouter()


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(payload: BookCreate, session: AsyncSession = Depends(get_session)) -> Book:
    existing = await session.execute(select(Book).where(Book.isbn == payload.isbn))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Book with this ISBN already exists")

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
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("", response_model=MemberRead, status_code=status.HTTP_201_CREATED)
async def create_member(payload: MemberCreate, session: AsyncSession = Depends(get_session)) -> Member:
    existing_email = await session.execute(select(Member).where(Member.email == payload.email))
    if existing_email.scalars().first():
        raise HTTPException(status_code=400, detail="Member with this email already exists")

    existing_membership = await session.execute(
        select(Member).where(Member.membership_number == payload.membership_number)
    )
    if existing_membership.scalars().first():
        raise HTTPException(status_code=400, detail="Membership number already in use")

    member = Member(**payload.model_dump())
    session.add(member)
    await session.commit()
    await session.refresh(member)
    return member


@router.get("", response_model=list[MemberRead])
async def list_members(session: AsyncSession = Depends(get_session)) -> list[Member]:
    result = await session.execute(select(Member).order_by(Member.name))
    return result.scalars().all()


@router.get("/{member_id}", response_model=MemberRead)
async def get_member(member_id: int, session: AsyncSession = Depends(get_session)) -> Member:
    member = await session.get(Member, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.post("/borrow", response_model=LoanRead, status_code=status.HTTP_201_CREATED)
async def borrow_book(payload: LoanCreate, session: AsyncSession = Depends(get_session)) -> Loan:
    book = await session.get(Book, payload.book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    member = await session.get(Member, payload.member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    if book.copies_available <= 0:
        raise HTTPException(status_code=400, detail="No copies available for borrowing")

    loan = Loan(
        book_id=payload.book_id,
        member_id=payload.member_id,
        due_date=payload.due_date,
        status="borrowed",
    )
    book.copies_available -= 1
    session.add(loan)
    await session.commit()
    await session.refresh(loan)
    return loan


@router.post("/{loan_id}/return", response_model=LoanRead)
async def return_book(loan_id: int, session: AsyncSession = Depends(get_session)) -> Loan:
    loan = await session.get(Loan, loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")

    if loan.returned_at is not None:
        raise HTTPException(status_code=400, detail="Book already returned")

    loan.returned_at = datetime.utcnow()
    loan.status = "returned"

    book = await session.get(Book, loan.book_id)
    if book is not None:
        book.copies_available += 1

    await session.commit()
    await session.refresh(loan)
    return loan


@router.get("", response_model=list[LoanRead])
async def list_loans(session: AsyncSession = Depends(get_session)) -> list[Loan]:
    result = await session.execute(select(Loan).order_by(Loan.issued_at.desc()))
    return result.scalars().all()
