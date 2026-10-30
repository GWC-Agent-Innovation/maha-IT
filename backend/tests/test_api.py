import os

from app.config import settings
from app.database import SessionLocal
from app.services.approval import run_approval_cycle

from .conftest import PDF_BYTES, PNG_BYTES, income_payload


def test_list_certificates(client):
    response = client.get("/api/certificates")
    assert response.status_code == 200
    ids = [c["id"] for c in response.json()]
    assert ids == ["income", "caste", "domicile", "residence", "non-creamy-layer"]


def test_certificate_detail_and_404(client):
    assert client.get("/api/certificates/caste").json()["name"] == "Caste Certificate"
    assert client.get("/api/certificates/unknown").status_code == 404


def test_submit_application(client):
    response = client.post("/api/applications", json=income_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["reference"].startswith("MH-APP-")
    assert body["status"] == "SUBMITTED"


def test_references_are_unique(client):
    refs = {client.post("/api/applications", json=income_payload()).json()["reference"] for _ in range(5)}
    assert len(refs) == 5


def test_submit_rejects_invalid_common_fields(client):
    response = client.post("/api/applications", json=income_payload(mobile="12345", pin_code="111111"))
    assert response.status_code == 422
    fields = response.json()["detail"]["fields"]
    assert fields["mobile"].startswith("Enter a valid 10-digit mobile number")
    assert "PIN code" in fields["pin_code"]


def test_short_address_gives_friendly_message(client):
    response = client.post("/api/applications", json=income_payload(address="Pune"))
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["fields"]["address"] == "Address must be at least 5 characters."
    assert detail["message"] == "Address must be at least 5 characters."


def test_submit_rejects_missing_specific_field(client):
    payload = income_payload(specific_data={"occupation": "Farmer"})
    response = client.post("/api/applications", json=payload)
    assert response.status_code == 422
    assert "annual_family_income" in response.json()["detail"]["fields"]


def test_upload_document(client, reference):
    response = client.post(
        f"/api/applications/{reference}/documents",
        data={"doc_type": "Identity Proof"},
        files={"file": ("aadhaar.pdf", PDF_BYTES, "application/pdf")},
    )
    assert response.status_code == 201
    assert "stored_name" not in response.json()
    detail = client.get(f"/api/applications/{reference}").json()
    assert detail["documents"][0]["doc_type"] == "Identity Proof"


def test_upload_rejects_bad_extension(client, reference):
    response = client.post(
        f"/api/applications/{reference}/documents",
        data={"doc_type": "Identity Proof"},
        files={"file": ("script.exe", b"MZ...", "application/octet-stream")},
    )
    assert response.status_code == 400


def test_upload_rejects_mismatched_content(client, reference):
    response = client.post(
        f"/api/applications/{reference}/documents",
        data={"doc_type": "Identity Proof"},
        files={"file": ("fake.png", b"not really a png", "image/png")},
    )
    assert response.status_code == 400


def test_upload_rejects_oversize(client, reference):
    big = PDF_BYTES + b"0" * (settings.max_upload_mb * 1024 * 1024)
    response = client.post(
        f"/api/applications/{reference}/documents",
        data={"doc_type": "Income Proof"},
        files={"file": ("big.pdf", big, "application/pdf")},
    )
    assert response.status_code == 400


def test_upload_path_traversal_name_is_neutralised(client, reference):
    response = client.post(
        f"/api/applications/{reference}/documents",
        data={"doc_type": "Address Proof"},
        files={"file": ("../../evil.png", PNG_BYTES, "image/png")},
    )
    assert response.status_code == 201
    assert response.json()["original_name"] == "evil.png"
    assert not os.path.exists(os.path.join(settings.data_dir, "..", "evil.png"))


def test_citizen_history_includes_failed_payments(client):
    mobile = "9811122233"
    failed = client.post("/api/payments/failed", json={
        "account_mobile": mobile, "certificate_type": "caste",
        "transaction_ref": "TXNFAILED0001", "amount": 57.2, "method": "Card",
    })
    assert failed.status_code == 201
    created = client.post("/api/applications", json=income_payload(account_mobile=mobile))
    reference = created.json()["reference"]

    payments = client.get(f"/api/citizens/{mobile}/payments").json()
    by_status = {p["status"]: p for p in payments}
    assert by_status["FAILED"]["application_reference"] is None
    assert by_status["SUCCESS"]["application_reference"] == reference

    apps = client.get(f"/api/citizens/{mobile}/applications").json()
    assert [a["reference"] for a in apps] == [reference]
    assert apps[0]["download_url"] is None


def test_citizen_history_rejects_bad_mobile(client):
    assert client.get("/api/citizens/123/payments").status_code == 422


def test_unknown_reference_returns_404(client):
    assert client.get("/api/applications/MH-APP-00000000-XXXXXX/status").status_code == 404


def test_full_lifecycle(client, reference):
    status = client.get(f"/api/applications/{reference}/status").json()
    assert status["status"] == "SUBMITTED"
    assert status["certificate_ready"] is False
    assert client.get(f"/api/applications/{reference}/certificate").status_code == 409

    with SessionLocal() as db:
        assert run_approval_cycle(db) >= 1

    status = client.get(f"/api/applications/{reference}/status").json()
    assert status["status"] == "CERTIFICATE_GENERATED"
    assert [h["status"] for h in status["history"]] == [
        "SUBMITTED", "APPROVED", "CERTIFICATE_GENERATED",
    ]

    response = client.get(f"/api/applications/{reference}/certificate")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
