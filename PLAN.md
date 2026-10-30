# Plan: Maharashtra Citizen Certificate Portal (from prd.md)

## Context
Greenfield repo (`d:\maha-IT`, only `prd.md`). Build the baseline "legacy" monolith described in the PRD: static HTML + Tailwind (Play CDN) + vanilla JS frontend, FastAPI + SQLAlchemy + SQLite backend, background mock approval, ReportLab PDF certificates, one Docker container with persistent volume. Used later as a training codebase, so keep it conventional and readable.

Decisions confirmed with user:
- Upload flow: browser holds files until final submit. `POST /api/applications` (with mock payment info) returns reference, then frontend uploads each file to `POST /api/applications/{reference}/documents`. Only 3 statuses: SUBMITTED, APPROVED, CERTIFICATE_GENERATED.
- Tailwind via Play CDN `<script>`; no Node build.
- SQLAlchemy ORM.
- Small pytest suite.

## Project layout
```
backend/app/
  main.py            # FastAPI app, routers, static mount, startup (create tables, start approval worker)
  config.py          # env settings: DATA_DIR, APPROVAL_DELAY_SECONDS (default 90), MAX_UPLOAD_MB (5)
  database.py        # engine, SessionLocal, Base, get_db
  models.py          # Application, ApplicationDocument, PaymentRecord, StatusHistory, Certificate
  schemas.py         # Pydantic request/response models
  catalog.py         # 5 certificate definitions: id, name, description, eligibility, documents, fee, processing info, specific fields
  routers/certificates.py
  routers/applications.py
  services/references.py   # MH-APP-YYYYMMDD-XXXXXX, MH-CERT-..., unique check
  services/storage.py      # safe filenames (uuid), ext + size validation, path resolution
  services/approval.py     # asyncio loop: poll DB every 10s, approve SUBMITTED older than delay, then generate PDF
  services/pdf.py          # ReportLab certificate + qrcode
backend/tests/       # pytest + TestClient, tmp DATA_DIR, delay=0
frontend/
  index.html login.html register.html certificate.html apply.html
  confirmation.html track.html   # apply.html = form/review/upload/payment wizard
  js/api.js js/session.js js/toast.js js/validation.js js/<page>.js
  assets/ (emblem-style placeholder logo, seal/signature drawn in PDF code)
requirements.txt  Dockerfile  docker-compose.yml  .dockerignore  README.md
```
FastAPI serves `frontend/` as static files at `/`; APIs under `/api`.

## Steps (all done)

Deviations: ReportLab built-in QR widget replaces the `qrcode` package; upload and payment are steps inside `apply.html`.

0. [x] **Save plan in repo** – copy this plan to `d:\maha-IT\PLAN.md` and use it as the build checklist; tick steps off as they complete.

1. [x] **Scaffold** – folders, `requirements.txt` (fastapi, uvicorn, sqlalchemy, python-multipart, reportlab, qrcode, pillow, pydantic-settings, pytest, httpx), `config.py`, `database.py`, `main.py` with health route + static mount.

2. [x] **Models** (`models.py`)
   - `Application`: id, reference (unique), certificate_type, common fields (full_name, dob, gender, mobile, email, address, district, taluka, pin), `specific_data` JSON, status, created_at, updated_at, approved_at.
   - `ApplicationDocument`: id, application_id FK, doc_type, original_name, stored_name, content_type, size, uploaded_at.
   - `PaymentRecord`: application_id FK, transaction_ref, amount, method, paid_at (mock, from frontend).
   - `StatusHistory`: application_id FK, status, note, changed_at.
   - `Certificate`: application_id FK unique, certificate_number unique, officer_name, designation, file_name, generated_at.

3. [x] **Catalog + certificate APIs** – `catalog.py` static data for 5 services incl. specific field definitions (name, label, type, required, options) so the form renders dynamically. `GET /api/certificates`, `GET /api/certificates/{id}` (404 unknown).

4. [x] **Application APIs** (`routers/applications.py`)
   - `POST /api/applications`: validate common + per-type required specific fields (Pydantic + catalog check: mobile 10 digits, PIN 6 digits starting 4, email, district in Maharashtra list), require payment block, create app status SUBMITTED + history row + payment record, return reference.
   - `POST /api/applications/{reference}/documents`: multipart, doc_type form field; allow .pdf/.jpg/.jpeg/.png, check size ≤ MAX_UPLOAD_MB, store as `uploads/<uuid>.<ext>` (never original name), return doc metadata without paths.
   - `GET /api/applications/{reference}`: details, documents (names only), payment, history, certificate availability.
   - `GET /api/applications/{reference}/status`: status + history (lightweight for polling).
   - `GET /api/applications/{reference}/certificate`: 409 if not CERTIFICATE_GENERATED, else `FileResponse` with friendly filename.
   - Note: PRD writes `{id}` for documents; use reference for consistency.

5. [x] **Approval worker** (`services/approval.py`) – started in FastAPI lifespan as asyncio task. Every 10s: query SUBMITTED apps where `created_at <= now - delay`; for each: set APPROVED + history ("Demo: simulated officer approval"), create Certificate record with mock officer (e.g. "Tahsildar (Demo)"), generate PDF, set CERTIFICATE_GENERATED + history. Also picks up APPROVED apps lacking a PDF (crash recovery). DB-driven, so survives browser refresh and container restart.

6. [x] **PDF generator** (`services/pdf.py`, ReportLab canvas, A4) – header band with "Government of Maharashtra – Demo Portal" branding, certificate title, certificate no., application ref, citizen details table, type-specific details, issue date, officer name/designation, drawn script-style mock signature, circular mock seal (drawn circles + text), QR code (qrcode lib) encoding ref + track URL, diagonal watermark and footer `SAMPLE – NOT A VALID GOVERNMENT CERTIFICATE`. Saved to `DATA_DIR/certificates/<cert_no>.pdf`.

7. [x] **Frontend shared** – common header/nav/footer markup per page (saffron/blue gov style, "Demo portal" banner), `api.js` (fetch wrapper, error display), `session.js` (localStorage mock citizen session, login guard for apply flow), `toast.js`, `validation.js` (field-level messages).

8. [x] **Frontend pages**
   - `index.html`: branding, search/filter over certificate cards, instructions, announcements, Login/Register, Track entry.
   - `login.html` / `register.html`: sample data, mock success, store session, redirect to `next`.
   - `certificate.html?id=`: details, eligibility, docs checklist, fee, processing time, Apply Now.
   - `apply.html?id=`: common fields + dynamic specific fields from catalog, validation, review step; draft saved to sessionStorage.
   - Upload screen: `File` objects can't survive page navigation, so `apply.html` is a wizard (Form → Review → Documents → Payment → Submit) with each PRD screen as a step. Drop separate `upload.html`/`payment.html`. Documents step: per-required-doc file pickers, client ext/size check.
   - Payment step: fee summary, mock card/UPI/netbanking UI, 2s fake processing, mock txn ref, toast.
   - Submit: POST application, then upload each file, redirect to `confirmation.html?ref=`.
   - `track.html?ref=`: lookup form, status badge, timeline history, polls `/status` every 10s, toast on APPROVED/CERTIFICATE_GENERATED, Download button when ready. Demo notice about 1–2 min simulated approval.

9. [x] **Docker** – `python:3.12-slim`, install requirements, copy backend + frontend, `DATA_DIR=/data`, `VOLUME /data`, expose 8000, uvicorn CMD. `docker-compose.yml` with named volume `maha_data:/data`.

10. [x] **Tests** (`backend/tests/`) – catalog list/detail; create application valid/invalid; upload valid, bad extension, oversize, traversal name stored safely; status before approval; certificate download 409 before; run approval cycle function directly with delay=0, then status CERTIFICATE_GENERATED and PDF download 200 with `application/pdf`.

11. [x] **README** – overview, demo disclaimer, local run (`pip install -r requirements.txt`, `uvicorn app.main:app`), Docker run, env vars, API table, demo journey steps, running tests.

## Verification
- `pytest backend/tests` passes.
- `docker compose up --build`, open `http://localhost:8000`, walk PRD §13 journey: browse, mock login, Income Certificate, fill form, upload PDF/JPG, mock pay, submit, see ref, track shows SUBMITTED, within ~90s+poll shows APPROVED then CERTIFICATE_GENERATED with toast, download PDF and check contents (signature, seal, QR, disclaimer).
- `docker compose restart`, re-track same ref: data and PDF still present (AC-14).
- Submit, restart container before approval: approval still completes after restart.
