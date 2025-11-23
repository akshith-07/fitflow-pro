from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from uuid import UUID
from app.models.payment import PaymentMethod, PaymentStatus, InvoiceStatus


# Payment Schemas
class PaymentBase(BaseModel):
    member_id: UUID
    membership_id: Optional[UUID] = None
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    payment_method: PaymentMethod
    payment_date: date


class PaymentCreate(PaymentBase):
    payment_gateway: Optional[str] = None
    transaction_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PaymentUpdate(BaseModel):
    status: PaymentStatus
    transaction_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PaymentResponse(PaymentBase):
    id: UUID
    organization_id: UUID
    payment_gateway: Optional[str] = None
    transaction_id: Optional[str] = None
    status: PaymentStatus
    due_date: Optional[date] = None
    retry_count: int
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Invoice Schemas
class InvoiceBase(BaseModel):
    member_id: UUID
    amount: float = Field(..., gt=0)
    tax_amount: float = Field(default=0, ge=0)
    total_amount: float = Field(..., gt=0)
    issue_date: date
    due_date: date
    line_items: List[Dict[str, Any]] = Field(default_factory=list)


class InvoiceCreate(InvoiceBase):
    payment_id: Optional[UUID] = None


class InvoiceUpdate(BaseModel):
    status: Optional[InvoiceStatus] = None
    paid_date: Optional[date] = None
    pdf_url: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    id: UUID
    organization_id: UUID
    payment_id: Optional[UUID] = None
    invoice_number: str
    status: InvoiceStatus
    paid_date: Optional[date] = None
    pdf_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Payment Intent (for frontend)
class PaymentIntent(BaseModel):
    amount: float
    currency: str
    member_id: UUID
    membership_id: Optional[UUID] = None
    payment_method_type: PaymentMethod


class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str


# Refund
class RefundRequest(BaseModel):
    payment_id: UUID
    amount: Optional[float] = None  # If None, full refund
    reason: Optional[str] = None


class RefundResponse(BaseModel):
    refund_id: str
    payment_id: UUID
    amount: float
    status: str
    created_at: datetime
