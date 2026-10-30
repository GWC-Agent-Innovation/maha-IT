import os
import tempfile

# Settings are read at import time, so configure the environment first.
_TMP = tempfile.mkdtemp(prefix="maha-portal-test-")
os.environ["DATA_DIR"] = _TMP
os.environ["APPROVAL_DELAY_SECONDS"] = "0"
os.environ["APPROVAL_WORKER_ENABLED"] = "false"
os.environ["MAX_UPLOAD_MB"] = "1"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

PDF_BYTES = b"%PDF-1.4\n%test document\n"
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


def income_payload(**overrides):
    payload = {
        "certificate_type": "income",
        "account_mobile": "9876543210",
        "full_name": "Ramesh Kumar Patil",
        "date_of_birth": "1990-05-14",
        "gender": "Male",
        "mobile": "9876543210",
        "email": "ramesh@example.com",
        "address": "12, Shivaji Nagar, Near Bus Stand",
        "district": "Pune",
        "taluka": "Haveli",
        "pin_code": "411005",
        "specific_data": {
            "occupation": "Farmer",
            "annual_family_income": 180000,
            "income_source": "Agriculture",
        },
        "payment": {"transaction_ref": "MOCKTXN123456", "amount": 33.6, "method": "UPI"},
    }
    payload.update(overrides)
    return payload


@pytest.fixture
def reference(client):
    response = client.post("/api/applications", json=income_payload())
    assert response.status_code == 201, response.text
    return response.json()["reference"]
