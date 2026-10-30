"""Minimal schema upgrades for existing SQLite databases.

Version 1 databases had no citizen account link on applications and stored
only successful payments. Version 2 databases had no certificate validity.
These upgrades keep existing data.
"""
from sqlalchemy import Engine, inspect, text

from .database import Base


def _columns(engine: Engine, table: str) -> set[str]:
    return {c["name"] for c in inspect(engine).get_columns(table)}


def upgrade_schema(engine: Engine) -> None:
    tables = set(inspect(engine).get_table_names())
    copy_old_payments = False

    with engine.begin() as conn:
        if "applications" in tables and "account_mobile" not in _columns(engine, "applications"):
            conn.execute(text("ALTER TABLE applications ADD COLUMN account_mobile VARCHAR(10)"))
            conn.execute(text("UPDATE applications SET account_mobile = mobile"))
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS ix_applications_account_mobile "
                "ON applications (account_mobile)"
            ))

        if "certificates" in tables and "valid_until" not in _columns(engine, "certificates"):
            conn.execute(text("ALTER TABLE certificates ADD COLUMN valid_until DATE"))
            # Certificates issued before validity rules existed: 1 year for the
            # types that expire, permanent (NULL) for caste and domicile.
            conn.execute(text(
                "UPDATE certificates SET valid_until = date(issued_at, '+1 year', '-1 day') "
                "WHERE application_id IN (SELECT id FROM applications WHERE certificate_type "
                "IN ('income', 'residence', 'non-creamy-layer'))"
            ))

        if "payment_records" in tables and "status" not in _columns(engine, "payment_records"):
            # SQLite cannot drop NOT NULL, so rebuild the table.
            conn.execute(text("ALTER TABLE payment_records RENAME TO payment_records_v1"))
            conn.execute(text("DROP INDEX IF EXISTS ix_payment_records_application_id"))
            copy_old_payments = True

    Base.metadata.create_all(bind=engine)

    if copy_old_payments:
        with engine.begin() as conn:
            conn.execute(text(
                "INSERT INTO payment_records (application_id, account_mobile, certificate_type, "
                "transaction_ref, amount, method, status, paid_at) "
                "SELECT p.application_id, a.account_mobile, a.certificate_type, "
                "p.transaction_ref, p.amount, p.method, 'SUCCESS', COALESCE(p.paid_at, CURRENT_TIMESTAMP) "
                "FROM payment_records_v1 p JOIN applications a ON a.id = p.application_id"
            ))
            conn.execute(text("DROP TABLE payment_records_v1"))
