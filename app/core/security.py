"""
================================================================================
BOILERPLATE: Enterprise Security & Secret Sanitizer Guardrails
Use Case: Scrubs sensitive credentials, private IP addresses, AWS/cloud tokens,
API keys, and checks prompt injection attempts before external LLM calls.
================================================================================
"""
import re
from typing import Tuple

SECRET_PATTERNS = [
    # AWS / Cloud Keys
    (r"(?i)AKIA[0-9A-Z]{16}", "[REDACTED_AWS_ACCESS_KEY]"),
    (r"(?i)aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{40}", "aws_secret_access_key=[REDACTED_SECRET]"),
    # Generic API Keys / Tokens (Bearer, gsk_, AIza, etc.)
    (r"(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}", "Bearer [REDACTED_BEARER_TOKEN]"),
    (r"gsk_[a-zA-Z0-9]{30,}", "[REDACTED_GROQ_KEY]"),
    (r"AIza[0-9A-Za-z-_]{35}", "[REDACTED_GOOGLE_KEY]"),
    # Internal IPv4 addresses (10.x.x.x, 192.168.x.x, 172.16-31.x.x)
    (r"\b(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3})\b", "[REDACTED_INTERNAL_IP]"),
    # Proprietary repo URLs with embedded basic auth
    (r"https?://[^:\s]+:[^@\s]+@[^\s]+", "https://[REDACTED_CREDENTIALS]@[HOST]"),
]

INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"(?i)you\s+are\s+now\s+(unrestricted|DAN|jailbroken)",
    r"(?i)system\s+override\s*:\s*reveal\s+prompt",
    r"(?i)bypass\s+safety\s+guidelines",
]


def sanitize_input(text: str) -> Tuple[str, bool, list[str]]:
    """
    Sanitize raw error logs or prompt text.
    Returns:
        (sanitized_text, injection_detected, detected_redactions)
    """
    if not text:
        return "", False, []

    # 1. Prompt Injection Check
    injection_detected = False
    for pat in INJECTION_PATTERNS:
        if re.search(pat, text):
            injection_detected = True
            break

    # 2. Secret and PII Masking
    sanitized = text
    redactions = []
    for pattern, replacement in SECRET_PATTERNS:
        matches = re.findall(pattern, sanitized)
        if matches:
            redactions.append(replacement)
            sanitized = re.sub(pattern, replacement, sanitized)

    return sanitized, injection_detected, redactions
