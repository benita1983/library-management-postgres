from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Member
from app.schemas import MemberCreate, MemberRead

router = APIRouter()


@router.post("", response_model=MemberRead, status_code=status.HTTP_201_CREATED)
async def create_member(payload: MemberCreate, session: AsyncSession = Depends(get_session)) -> Member:
    existing_email = await session.execute(select(Member).where(Member.email == payload.email))
    if existing_email.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Member with this email already exists")

    existing_membership = await session.execute(
        select(Member).where(Member.membership_number == payload.membership_number)
    )
    if existing_membership.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Membership number already in use")

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return member
