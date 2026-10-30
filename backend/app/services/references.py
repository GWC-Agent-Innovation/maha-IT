"""Generation of unique application and certificate numbers."""
import secrets
import string
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Application, Certificate

_ALPHABET = string.ascii_uppercase + string.digits


def _random_suffix(length: int = 6) -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))


def new_application_reference(db: Session) -> str:
    """Return a reference such as MH-APP-20261030-7K2Q9D that is not yet in use."""
    while True:
        ref = f"MH-APP-{datetime.now():%Y%m%d}-{_random_suffix()}"
        if not db.scalar(select(Application.id).where(Application.reference == ref)):
            return ref


def new_certificate_number(db: Session, certificate_type: str) -> str:
    prefix = certificate_type[:3].upper()
    while True:
        number = f"MH-{prefix}-{datetime.now():%Y}-{_random_suffix(8)}"
        if not db.scalar(
            select(Certificate.id).where(Certificate.certificate_number == number)
        ):
            return number
