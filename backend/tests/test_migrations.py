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
