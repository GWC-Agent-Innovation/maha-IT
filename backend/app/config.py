"""Application settings, read from environment variables."""
from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # Root folder for the SQLite database, uploaded documents and generated PDFs.
    data_dir: Path = BASE_DIR / "data"
    # Seconds after submission before the mock officer approves an application.
    approval_delay_seconds: int = 90
    # How often the background approval worker checks the database.
    approval_poll_seconds: int = 10
    # Set to false to disable the background worker (used by tests).
    approval_worker_enabled: bool = True
    max_upload_mb: int = 5
    frontend_dir: Path = BASE_DIR / "frontend"
    # Base URL printed in the certificate QR code.
    public_base_url: str = "http://localhost:8000"

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.data_dir / 'portal.db'}"

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def certificates_dir(self) -> Path:
        return self.data_dir / "certificates"

    def ensure_dirs(self) -> None:
        for path in (self.data_dir, self.uploads_dir, self.certificates_dir):
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
