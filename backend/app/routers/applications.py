"""Application submission, document upload, tracking and download endpoints."""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..catalog import get_certificate, validate_specific_fields
from ..database import get_db
from ..models import (
    PAYMENT_SUCCESS,
    STATUS_CERTIFICATE_GENERATED,
    STATUS_SUBMITTED,
    Application,
    ApplicationDocument,
    PaymentRecord,
    StatusHistory,
)
from ..schemas import (
    ApplicationCreate,
    ApplicationCreated,
    ApplicationOut,
    CertificateOut,
    DocumentOut,
    HistoryOut,
    PaymentOut,
    StatusOut,
)
from ..services.references import new_application_reference
from ..services.storage import certificate_path, safe_display_name, save_upload

router = APIRouter(prefix="/api/applications", tags=["applications"])


def _get_application(db: Session, reference: str) -> Application:
    app = db.scalar(select(Application).where(Application.reference == reference.strip().upper()))
    if app is None:
        raise HTTPException(404, "No application found for this reference number.")
    return app


def certificate_ready(app: Application) -> bool:
    return app.status == STATUS_CERTIFICATE_GENERATED and bool(
        app.certificate and app.certificate.file_name
    )


def _status_fields(app: Application) -> dict:
    cert_info = get_certificate(app.certificate_type)
    return {
        "reference": app.reference,
        "certificate_type": app.certificate_type,
        "certificate_name": cert_info["name"] if cert_info else app.certificate_type,
        "status": app.status,
        "created_at": app.created_at,
        "history": [
            HistoryOut(status=h.status, note=h.note, changed_at=h.changed_at)
            for h in app.history
        ],
        "certificate_ready": certificate_ready(app),
    }


@router.post("", response_model=ApplicationCreated, status_code=201)
def submit_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    cert_info = get_certificate(payload.certificate_type)
    if cert_info is None:
        raise HTTPException(422, "Unknown certificate type.")
    errors = validate_specific_fields(cert_info, payload.specific_data)
    if errors:
        raise HTTPException(422, {"message": "Please correct the highlighted fields.", "fields": errors})

    allowed_keys = {f["name"] for f in cert_info["fields"]}
    specific = {k: v for k, v in payload.specific_data.items() if k in allowed_keys}

    app = Application(
        reference=new_application_reference(db),
        certificate_type=payload.certificate_type,
        account_mobile=payload.account_mobile,
        full_name=payload.full_name.strip(),
        date_of_birth=payload.date_of_birth.isoformat(),
        gender=payload.gender,
        mobile=payload.mobile,
        email=str(payload.email),
        address=payload.address.strip(),
        district=payload.district,
        taluka=payload.taluka.strip(),
        pin_code=payload.pin_code,
        specific_data=specific,
        status=STATUS_SUBMITTED,
    )
    app.payment = PaymentRecord(
        account_mobile=payload.account_mobile,
        certificate_type=payload.certificate_type,
        transaction_ref=payload.payment.transaction_ref,
        amount=payload.payment.amount,
        method=payload.payment.method,
        status=PAYMENT_SUCCESS,
    )
    app.history.append(StatusHistory(
        status=STATUS_SUBMITTED,
        note="Application received and fee payment confirmed.",
    ))
    db.add(app)
    db.commit()
    db.refresh(app)
    return ApplicationCreated(reference=app.reference, status=app.status, created_at=app.created_at)


@router.post("/{reference}/documents", response_model=DocumentOut, status_code=201)
def upload_document(
    reference: str,
    doc_type: str = Form(..., min_length=2, max_length=120),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    app = _get_application(db, reference)
    stored_name, content_type, size = save_upload(file)
    doc = ApplicationDocument(
        application_id=app.id,
        doc_type=doc_type.strip(),
        original_name=safe_display_name(file.filename),
        stored_name=stored_name,
        content_type=content_type,
        size_bytes=size,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return _document_out(doc)


def _document_out(doc: ApplicationDocument) -> DocumentOut:
    return DocumentOut(
        id=doc.id,
        doc_type=doc.doc_type,
        original_name=doc.original_name,
        content_type=doc.content_type,
        size_bytes=doc.size_bytes,
        uploaded_at=doc.uploaded_at,
    )


@router.get("/{reference}", response_model=ApplicationOut)
def application_detail(reference: str, db: Session = Depends(get_db)):
    app = _get_application(db, reference)
    payment = app.payment
    cert = app.certificate
    return ApplicationOut(
        **_status_fields(app),
        full_name=app.full_name,
        date_of_birth=app.date_of_birth,
        gender=app.gender,
        mobile=app.mobile,
        email=app.email,
        address=app.address,
        district=app.district,
        taluka=app.taluka,
        pin_code=app.pin_code,
        specific_data=app.specific_data,
        documents=[_document_out(d) for d in app.documents],
        payment=PaymentOut(
            transaction_ref=payment.transaction_ref,
            amount=payment.amount,
            method=payment.method,
            status=payment.status,
            paid_at=payment.paid_at,
        ) if payment else None,
        certificate=CertificateOut(
            certificate_number=cert.certificate_number,
            officer_name=cert.officer_name,
            officer_designation=cert.officer_designation,
            issued_at=cert.issued_at,
            download_url=(
                f"/api/applications/{app.reference}/certificate"
                if certificate_ready(app) else None
            ),
        ) if cert else None,
    )


@router.get("/{reference}/status", response_model=StatusOut)
def application_status(reference: str, db: Session = Depends(get_db)):
    return StatusOut(**_status_fields(_get_application(db, reference)))


@router.get("/{reference}/certificate")
def download_certificate(reference: str, db: Session = Depends(get_db)):
    app = _get_application(db, reference)
    if not certificate_ready(app):
        raise HTTPException(409, "Certificate is not available until the application is approved.")
    path = certificate_path(app.certificate.file_name)
    if not path.is_file():
        raise HTTPException(404, "Certificate file is missing. Please contact support.")
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"{app.certificate_type}-certificate-{app.reference}.pdf",
    )
