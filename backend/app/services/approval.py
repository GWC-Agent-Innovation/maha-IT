"""Simulated officer approval workflow (DEMONSTRATION ONLY).

A background task polls the database. Any application that has been in
SUBMITTED status for longer than APPROVAL_DELAY_SECONDS is approved by a
mock officer, and a certificate PDF is generated for it.

Because the workflow is driven by data in SQLite, it is not affected by
browser refreshes and resumes after a server or container restart.
"""
import asyncio
import logging
import random
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import SessionLocal
from ..models import (
    STATUS_APPROVED,
    STATUS_CERTIFICATE_GENERATED,
    STATUS_SUBMITTED,
    Application,
    Certificate,
    StatusHistory,
    utcnow,
)
from .pdf import generate_certificate_pdf
from .references import new_certificate_number
from .storage import certificate_path
from .validity import compute_valid_until

logger = logging.getLogger(__name__)

# Fictional officers used by the simulated approval.
MOCK_OFFICERS = [
    ("Shri A. R. Patil", "Tahsildar"),
    ("Smt. S. M. Deshmukh", "Sub-Divisional Officer"),
    ("Shri V. K. Jadhav", "Naib Tahsildar"),
]


def approve_application(db: Session, app: Application) -> None:
    """Move an application from SUBMITTED to APPROVED with a mock officer record."""
    officer_name, designation = random.choice(MOCK_OFFICERS)
    now = utcnow()
    app.status = STATUS_APPROVED
    app.approved_at = now
    app.certificate = Certificate(
        certificate_number=new_certificate_number(db, app.certificate_type),
        officer_name=officer_name,
        officer_designation=designation,
        issued_at=now,
        valid_until=compute_valid_until(app.certificate_type, now),
    )
    app.history.append(StatusHistory(
        status=STATUS_APPROVED,
        note=f"Application verified and approved by {officer_name}, {designation}",
        changed_at=now,
    ))
    db.commit()


def generate_certificate(db: Session, app: Application) -> None:
    """Generate the PDF for an APPROVED application and mark it CERTIFICATE_GENERATED."""
    cert = app.certificate
    file_name = f"{cert.certificate_number}.pdf"
    generate_certificate_pdf(app, cert, certificate_path(file_name))
    now = utcnow()
    cert.file_name = file_name
    cert.generated_at = now
    app.status = STATUS_CERTIFICATE_GENERATED
    app.history.append(StatusHistory(
        status=STATUS_CERTIFICATE_GENERATED,
        note="Certificate PDF generated and ready for download",
        changed_at=now,
    ))
    db.commit()


def run_approval_cycle(db: Session) -> int:
    """Process all due applications once. Returns the number processed."""
    cutoff = utcnow() - timedelta(seconds=settings.approval_delay_seconds)
    due = db.scalars(
        select(Application).where(
            Application.status == STATUS_SUBMITTED, Application.created_at <= cutoff
        )
    ).all()
    # Approved but not yet generated (e.g. the server stopped mid-way).
    pending_pdf = db.scalars(
        select(Application).where(Application.status == STATUS_APPROVED)
    ).all()

    processed = 0
    for app in list(due) + list(pending_pdf):
        try:
            if app.status == STATUS_SUBMITTED:
                approve_application(db, app)
            generate_certificate(db, app)
            processed += 1
            logger.info("Demo approval completed for %s", app.reference)
        except Exception:
            db.rollback()
            logger.exception("Demo approval failed for %s", app.reference)
    return processed


def _cycle_in_new_session() -> int:
    with SessionLocal() as db:
        return run_approval_cycle(db)


async def approval_worker() -> None:
    """Run the approval cycle forever, every APPROVAL_POLL_SECONDS."""
    logger.info(
        "Mock approval worker started (delay=%ss, poll=%ss)",
        settings.approval_delay_seconds, settings.approval_poll_seconds,
    )
    while True:
        try:
            await asyncio.to_thread(_cycle_in_new_session)
        except Exception:
            logger.exception("Mock approval cycle crashed")
        await asyncio.sleep(settings.approval_poll_seconds)
