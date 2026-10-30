"""Citizen account views (applications, certificates and payment history) and
recording of failed payment attempts.

Citizens are identified by the mobile number used at login. There is no real
authentication in this prototype (see PRD section 4.2).
"""
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..catalog import get_certificate
from ..database import get_db
from ..models import PAYMENT_FAILED, Application, PaymentRecord
from ..schemas import CitizenApplicationOut, EligibilityOut, FailedPaymentIn, PaymentHistoryOut
from ..services.validity import application_block_reason, validity_label
from .applications import certificate_ready

router = APIRouter(prefix="/api", tags=["citizens"])

MobilePath = Path(pattern=r"^[6-9]\d{9}$")


def _certificate_name(cert_type: str) -> str:
    info = get_certificate(cert_type)
    return info["name"] if info else cert_type


@router.post("/payments/failed", response_model=PaymentHistoryOut, status_code=201)
def record_failed_payment(payload: FailedPaymentIn, db: Session = Depends(get_db)):
    if get_certificate(payload.certificate_type) is None:
        raise HTTPException(422, "Unknown certificate type.")
    payment = PaymentRecord(
        account_mobile=payload.account_mobile,
        certificate_type=payload.certificate_type,
        transaction_ref=payload.transaction_ref,
        amount=payload.amount,
        method=payload.method,
        status=PAYMENT_FAILED,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return _payment_out(payment)


def _payment_out(p: PaymentRecord) -> PaymentHistoryOut:
    return PaymentHistoryOut(
        transaction_ref=p.transaction_ref,
        amount=p.amount,
        method=p.method,
        status=p.status,
        paid_at=p.paid_at,
        certificate_type=p.certificate_type,
        certificate_name=_certificate_name(p.certificate_type),
        application_reference=p.application.reference if p.application else None,
    )


@router.get("/citizens/{mobile}/applications", response_model=list[CitizenApplicationOut])
def citizen_applications(mobile: str = MobilePath, db: Session = Depends(get_db)):
    apps = db.scalars(
        select(Application)
        .where(Application.account_mobile == mobile)
        .order_by(Application.created_at.desc())
    ).all()
    result = []
    for app in apps:
        ready = certificate_ready(app)
        cert = app.certificate
        result.append(CitizenApplicationOut(
            reference=app.reference,
            certificate_type=app.certificate_type,
            certificate_name=_certificate_name(app.certificate_type),
            status=app.status,
            created_at=app.created_at,
            certificate_number=cert.certificate_number if cert else None,
            issued_at=cert.issued_at if cert else None,
            valid_until=cert.valid_until if cert else None,
            validity=validity_label(app.certificate_type, cert.valid_until) if cert else "",
            download_url=f"/api/applications/{app.reference}/certificate" if ready else None,
        ))
    return result


@router.get("/citizens/{mobile}/payments", response_model=list[PaymentHistoryOut])
def citizen_payments(mobile: str = MobilePath, db: Session = Depends(get_db)):
    payments = db.scalars(
        select(PaymentRecord)
        .where(PaymentRecord.account_mobile == mobile)
        .order_by(PaymentRecord.paid_at.desc())
    ).all()
    return [_payment_out(p) for p in payments]


@router.get("/citizens/{mobile}/eligibility/{certificate_type}", response_model=EligibilityOut)
def citizen_eligibility(certificate_type: str, mobile: str = MobilePath, db: Session = Depends(get_db)):
    """Check whether this account can apply for a certificate now (before payment)."""
    info = get_certificate(certificate_type)
    if info is None:
        raise HTTPException(404, "Certificate service not found.")
    reason = application_block_reason(db, mobile, certificate_type)
    return EligibilityOut(
        certificate_type=certificate_type,
        eligible=reason is None,
        message=reason,
        validity=info["validity"],
        reapply_note=info["reapply_note"],
    )
