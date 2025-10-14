import re
from email_validator import validate_email, EmailNotValidError
import phonenumbers

def normalize_email(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return validate_email(value, check_deliverability=False).normalized
    except EmailNotValidError:
        return None

def normalize_phone(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = phonenumbers.parse(value, None)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        return None
    except Exception:
        return None
