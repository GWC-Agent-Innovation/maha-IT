"""Certificate catalogue endpoints."""
from fastapi import APIRouter, HTTPException

from ..catalog import CERTIFICATES, MAHARASHTRA_DISTRICTS, get_certificate

router = APIRouter(prefix="/api", tags=["certificates"])


@router.get("/certificates")
def list_certificates():
    return CERTIFICATES


@router.get("/certificates/{cert_id}")
def certificate_detail(cert_id: str):
    cert = get_certificate(cert_id)
    if cert is None:
        raise HTTPException(404, "Certificate service not found.")
    return cert


@router.get("/districts")
def list_districts():
    return MAHARASHTRA_DISTRICTS
