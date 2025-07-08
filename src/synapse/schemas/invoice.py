"""
Schemas for Invoice - a model for managing invoices.
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from decimal import Decimal
from enum import Enum


class InvoiceStatus(str, Enum):
    """Enum for the status of an invoice."""
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class InvoiceItemType(str, Enum):
    """Enum for the type of an invoice item."""
    SUBSCRIPTION = "subscription"
    USAGE = "usage"
    ONE_TIME = "one_time"
    DISCOUNT = "discount"
    TAX = "tax"


class InvoicePaymentStatus(str, Enum):
    """Enum for the status of an invoice payment."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class InvoiceReminderType(str, Enum):
    """Enum for the type of an invoice reminder."""
    DUE_SOON = "due_soon"
    OVERDUE = "overdue"
    PAYMENT_CONFIRMATION = "payment_confirmation"


class InvoiceBase(BaseModel):
    """Base schema for Invoice attributes."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    invoice_number: str = Field(..., description="Unique identifier for the invoice.")
    subscription_id: UUID = Field(..., description="The ID of the associated subscription.")
    user_id: UUID = Field(..., description="The ID of the user to whom the invoice belongs.")
    invoice_date: date = Field(..., description="The date the invoice was issued.")
    due_date: date = Field(..., description="The date the invoice is due.")
    subtotal: Decimal = Field(..., ge=0, description="The subtotal amount before taxes and discounts.")
    tax_amount: Decimal = Field(0, ge=0, description="The total tax amount.")
    discount_amount: Decimal = Field(0, ge=0, description="The total discount amount.")
    total_amount: Decimal = Field(..., ge=0, description="The total amount of the invoice.")
    status: InvoiceStatus = Field(InvoiceStatus.PENDING, description="The current status of the invoice.")
    billing_period_start: date = Field(..., description="The start date of the billing period.")
    billing_period_end: date = Field(..., description="The end date of the billing period.")
    payment_method_id: Optional[UUID] = Field(None, description="The ID of the payment method used.")
    payment_provider_id: Optional[UUID] = Field(None, description="The ID of the payment provider.")
    tenant_id: UUID = Field(..., description="The tenant to which this invoice belongs.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the invoice.")
    notes: Optional[str] = Field(None, description="Any notes or comments related to the invoice.")


class InvoiceCreate(InvoiceBase):
    """Schema for creating a new Invoice."""
    pass


class InvoiceUpdate(BaseModel):
    """Schema for updating an existing Invoice. All fields are optional."""
    due_date: Optional[date] = Field(None, description="New due date.")
    subtotal: Optional[Decimal] = Field(None, ge=0, description="New subtotal amount.")
    tax_amount: Optional[Decimal] = Field(None, ge=0, description="New tax amount.")
    discount_amount: Optional[Decimal] = Field(None, ge=0, description="New discount amount.")
    total_amount: Optional[Decimal] = Field(None, ge=0, description="New total amount.")
    status: Optional[InvoiceStatus] = Field(None, description="New status for the invoice.")
    payment_method_id: Optional[UUID] = Field(None, description="New payment method ID.")
    payment_provider_id: Optional[UUID] = Field(None, description="New payment provider ID.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="New metadata.")
    notes: Optional[str] = Field(None, description="New notes.")


class InvoiceResponse(InvoiceBase):
    """Response schema for an Invoice, including database-generated fields and related data."""
    id: UUID = Field(..., description="Unique identifier for the invoice.")
    created_at: datetime = Field(..., description="Timestamp of when the invoice was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")
    user_name: Optional[str] = Field(None, description="The name of the user.")
    user_email: Optional[str] = Field(None, description="The email of the user.")
    subscription_plan_name: Optional[str] = Field(None, description="The name of the subscription plan.")
    paid_at: Optional[datetime] = Field(None, description="Timestamp of when the invoice was paid.")
    payment_transaction_id: Optional[str] = Field(None, description="The ID of the payment transaction.")
    items: Optional[List[Dict[str, Any]]] = Field(None, description="Line items included in the invoice.")
    is_overdue: Optional[bool] = Field(None, description="Indicates if the invoice is overdue.")
    days_until_due: Optional[int] = Field(None, description="Number of days until the invoice is due (negative if overdue).")


class InvoiceListResponse(BaseModel):
    """Paginated list of Invoices."""
    items: List[InvoiceResponse] = Field(..., description="List of invoices for the current page.")
    total: int = Field(..., description="Total number of invoices.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")


class InvoiceItem(BaseModel):
    """Schema for a single line item within an invoice."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    invoice_id: UUID = Field(..., description="The ID of the invoice this item belongs to.")
    description: str = Field(..., description="Description of the item.")
    item_type: InvoiceItemType = Field(..., description="The type of the invoice item.")
    quantity: int = Field(1, ge=1, description="The quantity of the item.")
    unit_price: Decimal = Field(..., ge=0, description="The unit price of the item.")
    total_price: Decimal = Field(..., ge=0, description="The total price for this item (quantity * unit_price).")
    period_start: Optional[date] = Field(None, description="The start date of the period for recurring items.")
    period_end: Optional[date] = Field(None, description="The end date of the period for recurring items.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the item.")


class InvoicePayment(BaseModel):
    """Schema for recording a payment made towards an invoice."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    invoice_id: UUID = Field(..., description="The ID of the invoice being paid.")
    amount: Decimal = Field(..., ge=0, description="The amount of the payment.")
    payment_method_id: Optional[UUID] = Field(None, description="The ID of the payment method used.")
    payment_provider_id: Optional[UUID] = Field(None, description="The ID of the payment provider.")
    payment_data: Optional[Dict[str, Any]] = Field(None, description="Raw data from the payment gateway.")


class InvoicePaymentResult(BaseModel):
    """Schema for the result of an invoice payment operation."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    invoice_id: UUID = Field(..., description="The ID of the invoice.")
    payment_id: UUID = Field(..., description="The ID of the payment record.")
    status: InvoicePaymentStatus = Field(..., description="The status of the payment.")
    amount: Decimal = Field(..., ge=0, description="The amount paid.")
    transaction_id: Optional[str] = Field(None, description="The transaction ID from the payment provider.")
    processed_at: datetime = Field(..., description="Timestamp of when the payment was processed.")
    error_message: Optional[str] = Field(None, description="Any error message if the payment failed.")


class InvoiceReminder(BaseModel):
    """Schema for sending an invoice reminder."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    invoice_id: UUID = Field(..., description="The ID of the invoice for which to send a reminder.")
    reminder_type: InvoiceReminderType = Field(..., description="The type of reminder to send.")
    send_email: bool = Field(True, description="Whether to send the reminder via email.")
    send_notification: bool = Field(True, description="Whether to send the reminder via in-app notification.")
    subject: Optional[str] = Field(None, description="Custom subject for the reminder (if email).")
    message: Optional[str] = Field(None, description="Custom message for the reminder.")


class InvoiceStatistics(BaseModel):
    """Schema for aggregated invoice statistics."""
    model_config = ConfigDict(from_attributes=True)

    total_invoices: int = Field(..., description="Total number of invoices.")
    total_amount: Decimal = Field(..., description="Total amount across all invoices.")
    by_status: Dict[InvoiceStatus, int] = Field(..., description="Count of invoices by status.")
    amounts_by_status: Dict[InvoiceStatus, Decimal] = Field(..., description="Total amount of invoices by status.")
    paid_invoices: int = Field(..., description="Number of paid invoices.")
    paid_amount: Decimal = Field(..., description="Total amount of paid invoices.")
    overdue_invoices: int = Field(..., description="Number of overdue invoices.")
    overdue_amount: Decimal = Field(..., description="Total amount of overdue invoices.")
    average_invoice_amount: Decimal = Field(..., description="Average amount per invoice.")
    average_payment_time_days: float = Field(..., description="Average time to payment in days.")
    period_start: datetime = Field(..., description="The start date of the statistics period.")
    period_end: datetime = Field(..., description="The end date of the statistics period.")


class InvoiceReport(BaseModel):
    """Schema for an invoice report."""
    model_config = ConfigDict(from_attributes=True)

    report_type: str = Field(..., description="The type of report (e.g., 'summary', 'detailed').")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters applied to generate the report.")
    data: List[Dict[str, Any]] = Field(..., description="The data included in the report.")
    summary: Dict[str, Any] = Field(..., description="A summary of the report data.")
    period_start: datetime = Field(..., description="The start date of the report period.")
    period_end: datetime = Field(..., description="The end date of the report period.")


class InvoiceExport(BaseModel):
    """Schema for exporting invoices."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    format: str = Field(..., description="The export format (e.g., 'csv', 'pdf').")
    status: Optional[InvoiceStatus] = Field(None, description="Filter invoices by status.")
    date_from: Optional[date] = Field(None, description="Filter invoices from this date.")
    date_to: Optional[date] = Field(None, description="Filter invoices up to this date.")
    include_items: bool = Field(True, description="Whether to include line items in the export.")
    include_payments: bool = Field(True, description="Whether to include payment details in the export.")


class InvoicePreview(BaseModel):
    """Schema for previewing an invoice before generation."""
    model_config = ConfigDict(from_attributes=True)

    subscription_id: UUID = Field(..., description="The ID of the subscription for which to preview the invoice.")
    billing_period_start: date = Field(..., description="The start date of the billing period for the preview.")
    billing_period_end: date = Field(..., description="The end date of the billing period for the preview.")
    calculated_items: List[Dict[str, Any]] = Field(..., description="The calculated line items for the preview.")
    calculated_total: Decimal = Field(..., description="The calculated total amount for the preview.")
