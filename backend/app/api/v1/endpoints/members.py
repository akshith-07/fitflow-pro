from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.db.session import get_db
from app.core.deps import get_current_user, get_current_organization, require_role
from app.models.user import User, UserRole
from app.models.member import Member
from app.models.organization import Organization
from app.schemas.member import MemberCreate, MemberUpdate, MemberResponse

router = APIRouter()


@router.post("/", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(
    member_in: MemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.GYM_OWNER, UserRole.ADMIN, UserRole.RECEPTIONIST])),
    organization: Organization = Depends(get_current_organization)
):
    """Create a new member"""
    # Check if member already exists for this user
    existing_member = db.query(Member).filter(
        Member.user_id == member_in.user_id,
        Member.organization_id == organization.id
    ).first()

    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Member already exists for this user"
        )

    member = Member(
        organization_id=organization.id,
        **member_in.dict()
    )

    db.add(member)
    db.commit()
    db.refresh(member)

    return member


@router.get("/", response_model=List[MemberResponse])
def list_members(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search by name, email, or member ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization)
):
    """List members with filtering and search"""
    query = db.query(Member).filter(Member.organization_id == organization.id)

    if search:
        query = query.filter(Member.member_id.ilike(f"%{search}%"))

    if status:
        from app.models.member import MemberStatus
        query = query.filter(Member.status == MemberStatus(status))

    members = query.offset(skip).limit(limit).all()
    return members


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(
    member_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization)
):
    """Get member details"""
    member = db.query(Member).filter(
        Member.id == member_id,
        Member.organization_id == organization.id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    # Members can only see their own details
    if current_user.role == UserRole.MEMBER:
        if member.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

    return member


@router.put("/{member_id}", response_model=MemberResponse)
def update_member(
    member_id: UUID,
    member_update: MemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization)
):
    """Update member details"""
    member = db.query(Member).filter(
        Member.id == member_id,
        Member.organization_id == organization.id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    # Members can update their own details, staff can update any member
    if current_user.role == UserRole.MEMBER:
        if member.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

    # Update fields
    for field, value in member_update.dict(exclude_unset=True).items():
        setattr(member, field, value)

    db.commit()
    db.refresh(member)

    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(
    member_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.GYM_OWNER, UserRole.ADMIN])),
    organization: Organization = Depends(get_current_organization)
):
    """Delete member"""
    member = db.query(Member).filter(
        Member.id == member_id,
        Member.organization_id == organization.id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    db.delete(member)
    db.commit()

    return None
