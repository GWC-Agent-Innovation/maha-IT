from datetime import date, datetime, timedelta

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Application
from app.services.approval import run_approval_cycle
from app.services.validity import compute_valid_until, validity_label

from .conftest import income_payload, new_mobile

CASTE_DATA = {
    "caste_category": "OBC", "caste": "Kunbi", "father_name": "Kumar Patil", "father_caste": "Kunbi",
}
NCL_DATA = {
    "caste_category": "OBC", "caste": "Kunbi", "annual_family_income": 450000,
    "father_name": "Kumar Patil", "father_occupation": "Farmer", "mother_name": "Sunita Patil",
}


def _approve_all():
    with SessionLocal() as db:
        run_approval_cycle(db)


def _eligibility(client, mobile, cert_type):
    return client.get(f"/api/citizens/{mobile}/eligibility/{cert_type}").json()


def test_valid_until_rules():
    issued = datetime(2026, 10, 30, 11, 0)
    assert compute_valid_until("income", issued) == date(2027, 10, 29)
    assert compute_valid_until("residence", issued) == date(2027, 10, 29)
    assert compute_valid_until("non-creamy-layer", issued) == date(2027, 10, 29)
    assert compute_valid_until("caste", issued) is None
    assert compute_valid_until("domicile", issued) is None
    # Leap day: the next year has no 29 February.
    assert compute_valid_until("income", datetime(2028, 2, 29)) == date(2029, 2, 27)


def test_validity_label():
    today = date(2026, 10, 30)
    assert validity_label("caste", None, today) == "Permanent"
    assert validity_label("income", date(2027, 10, 29), today) == "Valid until 29-10-2027"
    assert validity_label("income", date(2026, 10, 29), today) == "Expired on 29-10-2026"


def test_income_can_be_reapplied_only_after_expiry(client):
    mobile = new_mobile()
    assert client.post("/api/applications", json=income_payload(account_mobile=mobile)).status_code == 201

    # Pending application blocks a second one.
    blocked = client.post("/api/applications", json=income_payload(account_mobile=mobile))
    assert blocked.status_code == 409
    assert "already being processed" in blocked.json()["detail"]["message"]

    # Issued and still valid: blocked, and the citizen sees until when.
    _approve_all()
    check = _eligibility(client, mobile, "income")
    assert check["eligible"] is False and "valid until" in check["message"]
    apps = client.get(f"/api/citizens/{mobile}/applications").json()
    assert apps[0]["validity"].startswith("Valid until")
    assert client.post("/api/applications", json=income_payload(account_mobile=mobile)).status_code == 409

    # Once expired, a new application is accepted.
    with SessionLocal() as db:
        app = db.scalar(select(Application).where(Application.account_mobile == mobile))
        app.certificate.valid_until = date.today() - timedelta(days=1)
        db.commit()
    assert _eligibility(client, mobile, "income")["eligible"] is True
    assert client.post("/api/applications", json=income_payload(account_mobile=mobile)).status_code == 201


def test_caste_certificate_is_permanent_and_issued_once(client):
    mobile = new_mobile()
    payload = income_payload(account_mobile=mobile, certificate_type="caste", specific_data=CASTE_DATA)
    assert client.post("/api/applications", json=payload).status_code == 201
    _approve_all()

    apps = client.get(f"/api/citizens/{mobile}/applications").json()
    assert apps[0]["validity"] == "Permanent" and apps[0]["valid_until"] is None
    blocked = client.post("/api/applications", json=payload)
    assert blocked.status_code == 409
    assert "valid for life" in blocked.json()["detail"]["message"]
    # Other certificate types are not affected.
    assert _eligibility(client, mobile, "income")["eligible"] is True


def test_non_creamy_layer_can_be_applied_any_time(client):
    mobile = new_mobile()
    payload = income_payload(account_mobile=mobile, certificate_type="non-creamy-layer", specific_data=NCL_DATA)
    assert client.post("/api/applications", json=payload).status_code == 201
    assert client.post("/api/applications", json=payload).status_code == 201
    _approve_all()
    assert client.post("/api/applications", json=payload).status_code == 201
    apps = client.get(f"/api/citizens/{mobile}/applications").json()
    issued = [a for a in apps if a["valid_until"]]
    assert len(issued) == 2 and all(a["validity"].startswith("Valid until") for a in issued)


def test_eligibility_unknown_certificate(client):
    assert client.get(f"/api/citizens/{new_mobile()}/eligibility/unknown").status_code == 404


def test_catalog_exposes_validity(client):
    certs = {c["id"]: c for c in client.get("/api/certificates").json()}
    assert certs["income"]["validity"] == "1 year from the date of issue"
    assert certs["caste"]["validity"] == "Permanent"
    assert certs["domicile"]["reapply"] == "once"
    assert certs["non-creamy-layer"]["reapply"] == "anytime"
