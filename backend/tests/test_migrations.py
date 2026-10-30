from sqlalchemy import create_engine, inspect, text

from app.migrations import upgrade_schema


def test_upgrade_from_v1_schema_keeps_payments(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'v1.db'}")
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE applications (id INTEGER PRIMARY KEY, reference VARCHAR(32), "
            "certificate_type VARCHAR(32), full_name VARCHAR(120), date_of_birth VARCHAR(10), "
            "gender VARCHAR(16), mobile VARCHAR(10), email VARCHAR(120), address TEXT, "
            "district VARCHAR(64), taluka VARCHAR(64), pin_code VARCHAR(6), specific_data JSON, "
            "status VARCHAR(32), created_at DATETIME, updated_at DATETIME, approved_at DATETIME)"
        ))
        conn.execute(text(
            "CREATE TABLE payment_records (id INTEGER PRIMARY KEY, application_id INTEGER NOT NULL, "
            "transaction_ref VARCHAR(40), amount FLOAT, method VARCHAR(32), paid_at DATETIME)"
        ))
        conn.execute(text("CREATE UNIQUE INDEX ix_payment_records_application_id ON payment_records (application_id)"))
        conn.execute(text(
            "INSERT INTO applications (id, reference, certificate_type, mobile, status) "
            "VALUES (1, 'MH-APP-OLD', 'income', '9876543210', 'SUBMITTED')"
        ))
        conn.execute(text(
            "INSERT INTO payment_records (application_id, transaction_ref, amount, method) "
            "VALUES (1, 'TXN-OLD-1', 33.6, 'UPI')"
        ))

    upgrade_schema(engine)

    assert "account_mobile" in {c["name"] for c in inspect(engine).get_columns("applications")}
    with engine.connect() as conn:
        row = conn.execute(text(
            "SELECT account_mobile, certificate_type, status, transaction_ref FROM payment_records"
        )).one()
    assert tuple(row) == ("9876543210", "income", "SUCCESS", "TXN-OLD-1")
    assert "payment_records_v1" not in inspect(engine).get_table_names()


def test_upgrade_adds_certificate_validity(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'v2.db'}")
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE applications (id INTEGER PRIMARY KEY, certificate_type VARCHAR(32), "
            "account_mobile VARCHAR(10))"
        ))
        conn.execute(text(
            "CREATE TABLE certificates (id INTEGER PRIMARY KEY, application_id INTEGER, "
            "certificate_number VARCHAR(40), officer_name VARCHAR(120), "
            "officer_designation VARCHAR(120), file_name VARCHAR(80), issued_at DATETIME, "
            "generated_at DATETIME)"
        ))
        conn.execute(text(
            "INSERT INTO applications (id, certificate_type, account_mobile) "
            "VALUES (1, 'income', '9876543210'), (2, 'caste', '9876543210')"
        ))
        conn.execute(text(
            "INSERT INTO certificates (application_id, certificate_number, issued_at) VALUES "
            "(1, 'MH-INC-OLD', '2026-03-15 10:00:00'), (2, 'MH-CST-OLD', '2026-03-15 10:00:00')"
        ))

    upgrade_schema(engine)

    with engine.connect() as conn:
        rows = dict(conn.execute(text("SELECT certificate_number, valid_until FROM certificates")).all())
    assert rows == {"MH-INC-OLD": "2027-03-14", "MH-CST-OLD": None}
