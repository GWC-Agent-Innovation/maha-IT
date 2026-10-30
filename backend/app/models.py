"""Database models."""
from datetime import date, datetime, timezone

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

STATUS_SUBMITTED = "SUBMITTED"
STATUS_APPROVED = "APPROVED"
STATUS_CERTIFICATE_GENERATED = "CERTIFICATE_GENERATED"

PAYMENT_SUCCESS = "SUCCESS"
PAYMENT_FAILED = "FAILED"


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reference: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    certificate_type: Mapped[str] = mapped_column(String(32), index=True)
    # Mobile number of the logged-in citizen account that filed the application.
    account_mobile: Mapped[str] = mapped_column(String(10), index=True)

    full_name: Mapped[str] = mapped_column(String(120))
    date_of_birth: Mapped[str] = mapped_column(String(10))
    gender: Mapped[str] = mapped_column(String(16))
    mobile: Mapped[str] = mapped_column(String(10))
    email: Mapped[str] = mapped_column(String(120))
    address: Mapped[str] = mapped_column(Text)
    district: Mapped[str] = mapped_column(String(64))
    taluka: Mapped[str] = mapped_column(String(64))
    pin_code: Mapped[str] = mapped_column(String(6))
    specific_data: Mapped[dict] = mapped_column(JSON, default=dict)

    status: Mapped[str] = mapped_column(String(32), default=STATUS_SUBMITTED, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    documents: Mapped[list["ApplicationDocument"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    payment: Mapped["PaymentRecord | None"] = relationship(
        back_populates="application", cascade="all, delete-orphan", uselist=False
    )
    history: Mapped[list["StatusHistory"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="StatusHistory.changed_at",
    )
    certificate: Mapped["Certificate | None"] = relationship(
        back_populates="application", cascade="all, delete-orphan", uselist=False
    )


class ApplicationDocument(Base):
    __tablename__ = "application_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), index=True)
    doc_type: Mapped[str] = mapped_column(String(120))
    original_name: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(64), unique=True)
    content_type: Mapped[str] = mapped_column(String(64))
    size_bytes: Mapped[int] = mapped_column(Integer)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    application: Mapped[Application] = relationship(back_populates="documents")


class PaymentRecord(Base):
    """A payment attempt. Successful payments are linked to their application;
    failed attempts have no application."""

    __tablename__ = "payment_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int | None] = mapped_column(
        ForeignKey("applications.id"), unique=True, index=True, nullable=True
    )
    account_mobile: Mapped[str] = mapped_column(String(10), index=True)
    certificate_type: Mapped[str] = mapped_column(String(32))
    transaction_ref: Mapped[str] = mapped_column(String(40))
    amount: Mapped[float] = mapped_column(Float)
    method: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16), default=PAYMENT_SUCCESS)
    paid_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    application: Mapped[Application] = relationship(back_populates="payment")


class StatusHistory(Base):
    __tablename__ = "application_status_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), index=True)
    status: Mapped[str] = mapped_column(String(32))
    note: Mapped[str] = mapped_column(String(255), default="")
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    application: Mapped[Application] = relationship(back_populates="history")


class Certificate(Base):
    __tablename__ = "certificates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id"), unique=True, index=True
    )
    certificate_number: Mapped[str] = mapped_column(String(40), unique=True)
    officer_name: Mapped[str] = mapped_column(String(120))
    officer_designation: Mapped[str] = mapped_column(String(120))
    file_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    # Last valid day; None for permanent certificates (caste, domicile).
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    application: Mapped[Application] = relationship(back_populates="certificate")
