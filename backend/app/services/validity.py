"""Certificate validity periods and re-application rules.

The rules for each certificate type are defined in the catalogue:
- Income and Residence: valid for 1 year; a new application is allowed only
  after the current certificate expires.
- Caste and Domicile: permanent; issued once per citizen account.
- Non-Creamy Layer: valid for 1 year; can be applied for any number of times.
"""
from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..catalog import AFTER_EXPIRY, ONCE, get_certificate
from ..models import STATUS_CERTIFICATE_GENERATED, Application


def _add_months(day: date, months: int) -> date:
    month_index = day.month - 1 + months
    year, month = day.year + month_index // 12, month_index % 12 + 1
    # Clamp the day for shorter months (e.g. 29 February in a non-leap year).
    for d in (day.day, 30, 29, 28):
        try:
            return date(year, month, d)
        except ValueError:
            continue
    raise ValueError("Invalid date")


def compute_valid_until(cert_type: str, issued_at: datetime) -> date | None:
    """Last day the certificate is valid, or None if it is permanent."""
    info = get_certificate(cert_type)
    months = info.get("validity_months") if info else None
    if not months:
        return None
    return _add_months(issued_at.date(), months) - timedelta(days=1)


def validity_label(cert_type: str, valid_until: date | None, today: date | None = None) -> str:
    """Short text for screens, e.g. 'Permanent' or 'Valid until 29-10-2027'."""
    if valid_until is None:
        info = get_certificate(cert_type)
        return "Permanent" if info and not info.get("validity_months") else ""
    today = today or date.today()
    if valid_until < today:
        return f"Expired on {valid_until:%d-%m-%Y}"
    return f"Valid until {valid_until:%d-%m-%Y}"


def application_block_reason(db: Session, mobile: str, cert_type: str) -> str | None:
    """Return why this account cannot apply for this certificate now, or None."""
    info = get_certificate(cert_type)
    if info is None:
        return None
    policy = info["reapply"]
    if policy not in (ONCE, AFTER_EXPIRY):
        return None

    apps = db.scalars(
        select(Application)
        .where(Application.account_mobile == mobile, Application.certificate_type == cert_type)
        .order_by(Application.created_at.desc())
    ).all()
    name = info["name"]
    today = date.today()
    for app in apps:
        if app.status != STATUS_CERTIFICATE_GENERATED:
            return (
                f"Your {name} application {app.reference} is already being processed. "
                "Please track that application instead of applying again."
            )
        cert = app.certificate
        if policy == ONCE:
            return (
                f"A {name} ({cert.certificate_number}) has already been issued to this account. "
                "It is valid for life, so a new application is not required. "
                "You can download it from My Account."
            )
        if cert.valid_until is None or cert.valid_until >= today:
            until = f" until {cert.valid_until:%d-%m-%Y}" if cert.valid_until else ""
            return (
                f"Your {name} ({cert.certificate_number}) is valid{until}. "
                "You can apply for a new one after it expires."
            )
    return None
