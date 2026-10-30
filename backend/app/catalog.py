"""Static catalogue of the five certificate services.

All eligibility, document and fee information is sample content written for
the prototype. It is not authoritative legal guidance.
"""

MAHARASHTRA_DISTRICTS = [
    "Ahmednagar", "Akola", "Amravati", "Beed", "Bhandara", "Buldhana",
    "Chandrapur", "Chhatrapati Sambhajinagar", "Dharashiv", "Dhule",
    "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna", "Kolhapur",
    "Latur", "Mumbai City", "Mumbai Suburban", "Nagpur", "Nanded",
    "Nandurbar", "Nashik", "Palghar", "Parbhani", "Pune", "Raigad",
    "Ratnagiri", "Sangli", "Satara", "Sindhudurg", "Solapur", "Thane",
    "Wardha", "Washim", "Yavatmal",
]

CASTE_CATEGORIES = ["SC", "ST", "OBC", "VJ/DT (NT-A)", "NT-B", "NT-C", "NT-D", "SBC"]

# Field definition keys: name, label, type (text|number|select|textarea), required, options
CERTIFICATES = [
    {
        "id": "income",
        "name": "Income Certificate",
        "description": (
            "Certifies the annual family income of the applicant. Commonly used "
            "for scholarships, fee concessions and welfare schemes."
        ),
        "eligibility": [
            "Applicant must be a resident of Maharashtra.",
            "Income of all earning family members must be declared.",
            "Applicable for salaried, self-employed and agricultural income.",
        ],
        "documents": ["Identity Proof", "Address Proof", "Income Proof"],
        "fee": 33.60,
        "processing_time": "Up to 15 working days",
        "fields": [
            {"name": "occupation", "label": "Occupation", "type": "text", "required": True},
            {"name": "annual_family_income", "label": "Annual Family Income (₹)", "type": "number", "required": True},
            {
                "name": "income_source", "label": "Primary Income Source", "type": "select", "required": True,
                "options": ["Salary", "Business", "Agriculture", "Pension", "Other"],
            },
            {"name": "family_members", "label": "Number of Family Members", "type": "number", "required": False},
        ],
    },
    {
        "id": "caste",
        "name": "Caste Certificate",
        "description": (
            "Certifies that the applicant belongs to a particular caste or "
            "category recognised by the State of Maharashtra."
        ),
        "eligibility": [
            "Applicant must belong to a notified caste or category.",
            "Proof of caste of father or paternal relative is required.",
            "Applicant must be domiciled in Maharashtra.",
        ],
        "documents": ["Identity Proof", "Address Proof", "Caste Proof of Father / Relative"],
        "fee": 57.20,
        "processing_time": "Up to 21 working days",
        "fields": [
            {"name": "caste_category", "label": "Caste Category", "type": "select", "required": True, "options": CASTE_CATEGORIES},
            {"name": "caste", "label": "Caste", "type": "text", "required": True},
            {"name": "sub_caste", "label": "Sub-Caste", "type": "text", "required": False},
            {"name": "father_name", "label": "Father's Name", "type": "text", "required": True},
            {"name": "father_caste", "label": "Father's Caste", "type": "text", "required": True},
        ],
    },
    {
        "id": "domicile",
        "name": "Domicile Certificate",
        "description": (
            "Certifies that the applicant is domiciled in Maharashtra. Used for "
            "education admissions and state government employment."
        ),
        "eligibility": [
            "Applicant should have resided in Maharashtra for at least 10 years.",
            "Proof of continuous residence is required.",
        ],
        "documents": ["Identity Proof", "Address Proof", "Proof of Residence for 10 Years"],
        "fee": 33.60,
        "processing_time": "Up to 15 working days",
        "fields": [
            {"name": "place_of_birth", "label": "Place of Birth", "type": "text", "required": True},
            {"name": "residence_place", "label": "Place of Residence in Maharashtra", "type": "text", "required": True},
            {"name": "years_of_residence", "label": "Years of Residence in Maharashtra", "type": "number", "required": True},
            {
                "name": "purpose", "label": "Purpose", "type": "select", "required": True,
                "options": ["Education", "Employment", "Other"],
            },
        ],
    },
    {
        "id": "residence",
        "name": "Residence Certificate",
        "description": (
            "Certifies the current residential address of the applicant within "
            "a Maharashtra district and taluka."
        ),
        "eligibility": [
            "Applicant must currently reside at the declared address.",
            "Address proof in the applicant's or family member's name is required.",
        ],
        "documents": ["Identity Proof", "Address Proof"],
        "fee": 33.60,
        "processing_time": "Up to 7 working days",
        "fields": [
            {
                "name": "residence_type", "label": "Type of Residence", "type": "select", "required": True,
                "options": ["Owned", "Rented", "Family Owned", "Government Quarters"],
            },
            {"name": "residing_since", "label": "Residing at Current Address Since (Year)", "type": "number", "required": True},
            {"name": "ward_or_village", "label": "Ward / Village", "type": "text", "required": True},
        ],
    },
    {
        "id": "non-creamy-layer",
        "name": "Non-Creamy Layer Certificate",
        "description": (
            "Certifies that the applicant from a backward category does not "
            "belong to the creamy layer, based on family income and status."
        ),
        "eligibility": [
            "Applicant must hold a valid caste certificate (OBC/VJNT/SBC).",
            "Family income must be below the notified limit of ₹8,00,000 per annum.",
            "Parents must not hold specified constitutional posts.",
        ],
        "documents": ["Identity Proof", "Caste Certificate", "Income Proof of Parents"],
        "fee": 57.20,
        "processing_time": "Up to 21 working days",
        "fields": [
            {"name": "caste_category", "label": "Caste Category", "type": "select", "required": True, "options": CASTE_CATEGORIES},
            {"name": "caste", "label": "Caste", "type": "text", "required": True},
            {"name": "annual_family_income", "label": "Annual Family Income (₹)", "type": "number", "required": True},
            {"name": "father_name", "label": "Father's Name", "type": "text", "required": True},
            {"name": "father_occupation", "label": "Father's Occupation", "type": "text", "required": True},
            {"name": "mother_name", "label": "Mother's Name", "type": "text", "required": True},
            {"name": "mother_occupation", "label": "Mother's Occupation", "type": "text", "required": False},
        ],
    },
]

CERTIFICATES_BY_ID = {cert["id"]: cert for cert in CERTIFICATES}


def get_certificate(cert_id: str) -> dict | None:
    return CERTIFICATES_BY_ID.get(cert_id)


def validate_specific_fields(cert: dict, data: dict) -> dict[str, str]:
    """Check certificate-specific fields. Returns {field_name: error_message}."""
    errors: dict[str, str] = {}
    for field in cert["fields"]:
        name = field["name"]
        value = data.get(name)
        text = "" if value is None else str(value).strip()
        if not text:
            if field["required"]:
                errors[name] = f"{field['label']} is required."
            continue
        if field["type"] == "number":
            try:
                if float(text) < 0:
                    errors[name] = f"{field['label']} cannot be negative."
            except ValueError:
                errors[name] = f"{field['label']} must be a number."
        if field["type"] == "select" and text not in field["options"]:
            errors[name] = f"{field['label']} has an invalid option."
    return errors
