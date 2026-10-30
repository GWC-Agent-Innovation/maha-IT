"""Minimal schema upgrades for existing SQLite databases.

Version 1 databases had no citizen account link on applications and stored
only successful payments. This upgrade keeps their data.
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
