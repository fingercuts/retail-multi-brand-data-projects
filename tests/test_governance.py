import hashlib
import pytest

def mask_email(email: str) -> str:
    """Simulation of the MD5 hashing logic used in the dbt governance layer"""
    if not email:
        return None
    return hashlib.md5(email.strip().lower().encode()).hexdigest()

def redact_address(address: str) -> str:
    """Simulation of the full redaction logic for street addresses"""
    return "[REDACTED]"

def partial_mask_phone(phone: str) -> str:
    """Simulation of the partial masking logic (trailing 4 digits)"""
    if not phone or len(phone) < 4:
        return "****"
    return f"***-***-{phone[-4:]}"

def test_governance_email_hashing():
    """Verify that emails are consistently hashed and normalized"""
    email = " User@Example.COM "
    hashed = mask_email(email)
    
    # Verify normalization (lowercase + stripped)
    assert hashed == mask_email("user@example.com")
    assert len(hashed) == 32  # MD5 length

def test_governance_address_redaction():
    """Verify that street addresses are fully scrubbed"""
    address = "123 Platinum Street, Tech City"
    assert redact_address(address) == "[REDACTED]"

def test_governance_phone_masking():
    """Verify that phone numbers only expose the last 4 digits"""
    phone = "1-800-555-1234"
    masked = partial_mask_phone(phone)
    assert masked == "***-***-1234"
