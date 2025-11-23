from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.db.session import get_db
from app.core.deps import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationResponse

router = APIRouter()


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    org_in: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """Create a new organization (Super Admin only)"""
    # Check if slug already exists
    existing_org = db.query(Organization).filter(Organization.slug == org_in.slug).first()
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization slug already exists"
        )

    organization = Organization(**org_in.dict())
    db.add(organization)
    db.commit()
    db.refresh(organization)

    return organization


@router.get("/", response_model=List[OrganizationResponse])
def list_organizations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """List all organizations (Super Admin only)"""
    organizations = db.query(Organization).offset(skip).limit(limit).all()
    return organizations


@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get organization details"""
    # Users can only see their own organization unless they're super admin
    if current_user.role != UserRole.SUPER_ADMIN:
        if current_user.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    return organization


@router.put("/{organization_id}", response_model=OrganizationResponse)
def update_organization(
    organization_id: UUID,
    org_update: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.GYM_OWNER]))
):
    """Update organization details"""
    if current_user.role == UserRole.GYM_OWNER:
        if current_user.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Update fields
    for field, value in org_update.dict(exclude_unset=True).items():
        setattr(organization, field, value)

    db.commit()
    db.refresh(organization)

    return organization


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """Delete organization (Super Admin only)"""
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    db.delete(organization)
    db.commit()

    return None
