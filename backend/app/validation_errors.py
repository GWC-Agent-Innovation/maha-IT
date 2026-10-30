"""Translate Pydantic validation errors into messages a citizen can act on."""

FIELD_LABELS = {
    "full_name": "Full name",
    "date_of_birth": "Date of birth",
    "gender": "Gender",
    "mobile": "Mobile number",
    "account_mobile": "Login mobile number",
    "email": "Email",
    "address": "Address",
    "district": "District",
    "taluka": "Taluka",
    "pin_code": "PIN code",
    "certificate_type": "Certificate type",
    "doc_type": "Document type",
    "file": "File",
}

PATTERN_MESSAGES = {
    "mobile": "Enter a valid 10-digit mobile number starting with 6–9.",
    "account_mobile": "Please log in again with a valid mobile number.",
    "pin_code": "Enter a valid 6-digit Maharashtra PIN code (starts with 4).",
}


def _message(field: str, label: str, error: dict) -> str:
    kind = error.get("type", "")
    ctx = error.get("ctx") or {}
    if kind == "missing":
        return f"{label} is required."
    if kind == "string_too_short":
        return f"{label} must be at least {ctx.get('min_length')} characters."
    if kind == "string_too_long":
        return f"{label} must be at most {ctx.get('max_length')} characters."
    if kind == "string_pattern_mismatch":
        return PATTERN_MESSAGES.get(field, f"{label} is not in the correct format.")
    if kind.startswith("date"):
        return f"Enter a valid {label.lower()}."
    if kind == "value_error":
        return error.get("msg", "").removeprefix("Value error, ") or f"{label} is invalid."
    return f"{label} is invalid."


def friendly_errors(errors: list[dict]) -> tuple[dict[str, str], str | None]:
    """Return ({field: message}, general_message)."""
    fields: dict[str, str] = {}
    general = None
    for error in errors:
        loc = [str(part) for part in error.get("loc", []) if part not in ("body", "query", "path")]
        if not loc:
            general = general or "The request could not be processed. Please try again."
            continue
        if loc[0] == "payment":
            general = "Payment details were incomplete. Please make the payment again."
            continue
        field = loc[0]
        label = FIELD_LABELS.get(field, field.replace("_", " ").capitalize())
        fields.setdefault(field, _message(field, label, error))
    if fields and not general:
        general = next(iter(fields.values())) if len(fields) == 1 else None
    return fields, general
