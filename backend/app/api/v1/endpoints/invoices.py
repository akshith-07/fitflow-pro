from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.payment import Invoice
from app.models.member import Member
from app.schemas.payment import InvoiceCreate, InvoiceResponse, InvoiceUpdate

router = APIRouter()


@router.get("/", response_model=List[InvoiceResponse])
def get_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    member_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all invoices for organization"""
    query = db.query(Invoice).filter(
        Invoice.organization_id == current_user.organization_id
    )

    if status:
        query = query.filter(Invoice.status == status)

    if member_id:
        query = query.filter(Invoice.member_id == member_id)

    invoices = query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()
    return invoices


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice_in: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new invoice"""
    # Verify member exists
    member = db.query(Member).filter(
        Member.id == invoice_in.member_id,
        Member.organization_id == current_user.organization_id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    # Generate invoice number
    last_invoice = db.query(Invoice).filter(
        Invoice.organization_id == current_user.organization_id
    ).order_by(Invoice.created_at.desc()).first()

    invoice_number = f"INV-{datetime.now().year}-{(last_invoice.id if last_invoice else 0) + 1:05d}"

    # Calculate totals
    total_amount = invoice_in.amount + invoice_in.tax_amount

    invoice = Invoice(
        organization_id=current_user.organization_id,
        member_id=invoice_in.member_id,
        invoice_number=invoice_number,
        amount=invoice_in.amount,
        tax_amount=invoice_in.tax_amount,
        total_amount=total_amount,
        status=invoice_in.status or "draft",
        issue_date=invoice_in.issue_date or datetime.now().date(),
        due_date=invoice_in.due_date,
        line_items=invoice_in.line_items
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return invoice


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get invoice by ID"""
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


@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: UUID,
    invoice_update: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update invoice"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.organization_id == current_user.organization_id
    ).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    # Update fields
    update_data = invoice_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(invoice, field, value)

    # Recalculate total if amount or tax changed
    if 'amount' in update_data or 'tax_amount' in update_data:
        invoice.total_amount = invoice.amount + invoice.tax_amount

    db.commit()
    db.refresh(invoice)

    return invoice


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete invoice"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.organization_id == current_user.organization_id
    ).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    if invoice.status == "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete paid invoice"
        )

    db.delete(invoice)
    db.commit()

    return None


@router.post("/{invoice_id}/send", response_model=InvoiceResponse)
def send_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send invoice to member via email"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.organization_id == current_user.organization_id
    ).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    # Update status to sent
    invoice.status = "sent"
    db.commit()
    db.refresh(invoice)

    # TODO: Trigger email sending via notification service
    # from app.tasks.notifications import send_invoice_email
    # send_invoice_email.delay(invoice_id)

    return invoice


@router.post("/{invoice_id}/mark-paid", response_model=InvoiceResponse)
def mark_invoice_paid(
    invoice_id: UUID,
    paid_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark invoice as paid"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.organization_id == current_user.organization_id
    ).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    invoice.status = "paid"
    invoice.paid_date = paid_date or datetime.now().date()

    db.commit()
    db.refresh(invoice)

    return invoice


@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download invoice as PDF"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.organization_id == current_user.organization_id
    ).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    # TODO: Generate PDF using library like ReportLab or WeasyPrint
    # For now, return the PDF URL if it exists
    if invoice.pdf_url:
        return {"pdf_url": invoice.pdf_url}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="PDF not generated yet"
    )
