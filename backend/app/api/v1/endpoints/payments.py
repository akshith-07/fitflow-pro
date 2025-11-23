from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.payment import Payment, Invoice, PaymentStatus, InvoiceStatus
from app.schemas.payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse
)

router = APIRouter()


# ===== PAYMENTS =====
@router.get("", response_model=List[PaymentResponse])
def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[PaymentStatus] = None,
    member_id: Optional[UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get payments with filters"""
    query = db.query(Payment).filter(
        Payment.organization_id == current_user.organization_id
    )

    if status_filter:
        query = query.filter(Payment.status == status_filter)

    if member_id:
        query = query.filter(Payment.member_id == member_id)

    if start_date:
        query = query.filter(Payment.payment_date >= start_date)

    if end_date:
        query = query.filter(Payment.payment_date <= end_date)

    payments = query.order_by(Payment.payment_date.desc()).offset(skip).limit(limit).all()
    return payments


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new payment"""
    if current_user.role not in ["gym_owner", "admin", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    new_payment = Payment(
        organization_id=current_user.organization_id,
        **payment_data.model_dump()
    )

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return new_payment


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific payment"""
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.organization_id == current_user.organization_id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    return payment


@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: UUID,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a payment"""
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.organization_id == current_user.organization_id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    update_data = payment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(payment, field, value)

    db.commit()
    db.refresh(payment)

    return payment


@router.get("/pending/all", response_model=List[PaymentResponse])
def get_pending_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all pending payments"""
    payments = db.query(Payment).filter(
        Payment.organization_id == current_user.organization_id,
        Payment.status == PaymentStatus.PENDING,
        Payment.due_date < date.today()
    ).order_by(Payment.due_date).all()

    return payments


# ===== INVOICES =====
@router.get("/invoices", response_model=List[InvoiceResponse])
def get_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[InvoiceStatus] = None,
    member_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get invoices with filters"""
    query = db.query(Invoice).filter(
        Invoice.organization_id == current_user.organization_id
    )

    if status_filter:
        query = query.filter(Invoice.status == status_filter)

    if member_id:
        query = query.filter(Invoice.member_id == member_id)

    invoices = query.order_by(Invoice.issue_date.desc()).offset(skip).limit(limit).all()
    return invoices


@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new invoice"""
    if current_user.role not in ["gym_owner", "admin", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Generate invoice number
    from datetime import datetime
    latest_invoice = db.query(Invoice).filter(
        Invoice.organization_id == current_user.organization_id
    ).order_by(Invoice.created_at.desc()).first()

    if latest_invoice:
        # Extract number and increment
        last_num = int(latest_invoice.invoice_number.split('-')[-1])
        invoice_number = f"INV-{datetime.now().year}-{last_num + 1:05d}"
    else:
        invoice_number = f"INV-{datetime.now().year}-00001"

    new_invoice = Invoice(
        organization_id=current_user.organization_id,
        invoice_number=invoice_number,
        **invoice_data.model_dump()
    )

    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)

    return new_invoice


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific invoice"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.organization_id == current_user.organization_id
    ).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    return invoice


@router.put("/invoices/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: UUID,
    invoice_data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an invoice"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.organization_id == current_user.organization_id
    ).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    update_data = invoice_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(invoice, field, value)

    db.commit()
    db.refresh(invoice)

    return invoice
