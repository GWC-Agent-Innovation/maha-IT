"""Pydantic request and response models."""
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator

from .catalog import MAHARASHTRA_DISTRICTS


class PaymentIn(BaseModel):
    """Payment details produced by the frontend payment simulation."""

    transaction_ref: str = Field(min_length=6, max_length=40)
    amount: float = Field(ge=0)
    method: str = Field(min_length=2, max_length=32)


class FailedPaymentIn(PaymentIn):
    """A payment attempt that did not complete (e.g. cancelled by the citizen)."""

    account_mobile: str = Field(pattern=r"^[6-9]\d{9}$")
    certificate_type: str


class ApplicationCreate(BaseModel):
    certificate_type: str
    account_mobile: str = Field(pattern=r"^[6-9]\d{9}$")
    full_name: str = Field(min_length=3, max_length=120)
    date_of_birth: date
    gender: str
    mobile: str = Field(pattern=r"^[6-9]\d{9}$")
    email: EmailStr
    address: str = Field(min_length=5, max_length=500)
    district: str
    taluka: str = Field(min_length=2, max_length=64)
    pin_code: str = Field(pattern=r"^4\d{5}$")
    specific_data: dict[str, Any] = Field(default_factory=dict)
    payment: PaymentIn

    @field_validator("gender")
    @classmethod
    def check_gender(cls, value: str) -> str:
        if value not in ("Male", "Female", "Other"):
            raise ValueError("Gender must be Male, Female or Other.")
        return value

    @field_validator("district")
    @classmethod
    def check_district(cls, value: str) -> str:
        if value not in MAHARASHTRA_DISTRICTS:
            raise ValueError("Select a valid Maharashtra district.")
        return value

    @field_validator("date_of_birth")
    @classmethod
    def check_dob(cls, value: date) -> date:
        if value >= date.today():
            raise ValueError("Date of birth must be in the past.")
        return value


class ApplicationCreated(BaseModel):
    reference: str
    status: str
    created_at: datetime


class DocumentOut(BaseModel):
    id: int
    doc_type: str
    original_name: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime


class HistoryOut(BaseModel):
    status: str
    note: str
    changed_at: datetime


class PaymentOut(BaseModel):
    transaction_ref: str
    amount: float
    method: str
    status: str
    paid_at: datetime


class PaymentHistoryOut(PaymentOut):
    certificate_type: str
    certificate_name: str
    application_reference: str | None


class CitizenApplicationOut(BaseModel):
    reference: str
    certificate_type: str
    certificate_name: str
    status: str
    created_at: datetime
    certificate_number: str | None
    issued_at: datetime | None
    download_url: str | None


class CertificateOut(BaseModel):
    certificate_number: str
    officer_name: str
    officer_designation: str
    issued_at: datetime
    download_url: str | None


class StatusOut(BaseModel):
    reference: str
    certificate_type: str
    certificate_name: str
    status: str
    created_at: datetime
    history: list[HistoryOut]
    certificate_ready: bool


class ApplicationOut(StatusOut):
    full_name: str
    date_of_birth: str
    gender: str
    mobile: str
    email: str
    address: str
    district: str
    taluka: str
    pin_code: str
    specific_data: dict[str, Any]
    documents: list[DocumentOut]
    payment: PaymentOut | None
    certificate: CertificateOut | None
