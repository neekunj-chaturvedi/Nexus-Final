"""
Nexus guardrails (§4). Shared by all servers and the orchestrator.
More functions will be added here later:
sanitize_free_text, redact_for_logging, output filtering.
"""

import html
import re

def mask_number(value):
    """Keep only the last 4 digits: 50100020077431 -> **********7431"""
    if not value:
        return value
    value = str(value)
    return "*" * (len(value) - 4) + value[-4:]


ACCOUNT_SCOPES = {
    "basic": [
        "account_id", "account_type", "status", "currency",
    ],
    "financial": [
        "account_id", "account_type", "account_number", "status",
        "restriction_reason", "auto_debit_allowed", "balance", "currency",
    ],
    "full": [
        "account_id", "customer_id", "account_type", "account_number", "status",
        "restriction_reason", "auto_debit_allowed", "balance", "currency", "opened_on",
    ],
}


def minimize_account_fields(account, caller_scope):
    """Return only the fields allowed for this scope. Account number always masked."""
    if caller_scope not in ACCOUNT_SCOPES:
        raise ValueError(f"Invalid caller_scope, expected one of {list(ACCOUNT_SCOPES)}")

    account = dict(account)
    if "account_number" in account:
        account["account_number"] = mask_number(account["account_number"])

    return {k: account[k] for k in ACCOUNT_SCOPES[caller_scope] if k in account}


# ---------------------------------------------------------------
# Input sanitisation / prompt-injection defence (§4)
# ---------------------------------------------------------------
MAX_TEXT_LENGTH = 2000

INJECTION_PATTERNS = [
    r"ignore (all |any )?(previous|prior|above) instructions",
    r"disregard (all |any )?(previous|prior|above)",
    r"you are now (in )?\w+ mode",
    r"\badmin mode\b",
    r"\bsystem\s*:",
    r"disable (all )?(safety|security) (checks|filters)",
    r"reveal .*(account number|password|system prompt)",
    r"approve any request",
    r"without escalation",
]
_INJECTION_RES = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def sanitize_free_text(text, max_length=MAX_TEXT_LENGTH):
    """Clean text and check it for injection attempts.

    Returns a dict:
        text                - cleaned text (HTML removed, length limited)
        injection_detected  - True if any injection pattern matched
        matched_patterns    - which patterns matched (for logging/demo)
    """
    text = "" if text is None else str(text)
    text = html.unescape(text)             # turn &lt;b&gt; into <b> first...
    text = re.sub(r"<[^>]+>", "", text)    # ...then strip all tags
    text = text.strip()[:max_length]

    matches = [p.pattern for p in _INJECTION_RES if p.search(text)]
    return {
        "text": text,
        "injection_detected": bool(matches),
        "matched_patterns": matches,
    }

# ---------------------------------------------------------------
# Output filtering (§4): catch unmasked identifiers before they reach a customer
# ---------------------------------------------------------------
_UNMASKED_ID_PATTERNS = [
    re.compile(r"\b\d{8,}\b"),                     # long digit runs: account numbers, phones
    re.compile(r"\b(?:GIP|HLP|TRP|PF)\d{6,}\b"),   # raw policy / portfolio numbers
]


def find_unmasked_identifiers(text):
    """Return any identifier-looking strings that are NOT masked."""
    found = []
    for pattern in _UNMASKED_ID_PATTERNS:
        found.extend(pattern.findall(text or ""))
    return found

# Internal system IDs must never appear in a customer-facing reply
_INTERNAL_ID_RE = re.compile(
    r"\b(?:CUS|ACC|PORT|CLM)-\d{5}\b|\bPOL-[A-Z]{2}-\d{5}\b"
)


def find_internal_ids(text):
    """Return internal IDs (ACC-XXXXX, POL-XX-XXXXX, ...) found in text."""
    return _INTERNAL_ID_RE.findall(text or "")

# ---------------------------------------------------------------
# Sanitise structured tool output (§4: "every document or tool output")
# ---------------------------------------------------------------
def sanitize_structure(value, path="$"):
    """Run sanitize_free_text on every string inside a dict/list.
    Unsafe strings are replaced. Returns (clean_value, findings)."""
    findings = []

    def walk(v, p):
        if isinstance(v, dict):
            return {k: walk(x, f"{p}.{k}") for k, x in v.items()}
        if isinstance(v, list):
            return [walk(x, f"{p}[{i}]") for i, x in enumerate(v)]
        if isinstance(v, str):
            checked = sanitize_free_text(v)
            if checked["injection_detected"]:
                findings.append({"path": p, "matched_patterns": checked["matched_patterns"]})
                return "[REMOVED: unsafe content]"
            return checked["text"]
        return v

    return walk(value, path), findings


# ---------------------------------------------------------------
# PII redaction for logs (§4)
# ---------------------------------------------------------------
ID_KEYS = {
    "account_id", "customer_id", "policy_id", "portfolio_id", "claim_id",
    "account_number", "policy_number", "portfolio_number",
}
CONTACT_KEYS = {"phone", "email", "full_name"}

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
_PHONE_RE = re.compile(r"\+\d{1,3}[-\s]?\d{6,12}\b")
_LONG_DIGITS_RE = re.compile(r"\b\d{10,}\b")


def _redact_string(text):
    text = _EMAIL_RE.sub("[EMAIL]", text)
    text = _PHONE_RE.sub("[PHONE]", text)
    text = _LONG_DIGITS_RE.sub(lambda m: mask_number(m.group()), text)
    text = _INTERNAL_ID_RE.sub(lambda m: mask_number(m.group()), text)
    return text


def redact_for_logging(value):
    """Return a copy that is safe to write to a log line.

    - Values under PII-shaped keys are masked (IDs) or removed (contact details)
    - Free text is scanned for emails, phone numbers, long digit runs and IDs
    - Works on dicts, lists, Pydantic models and plain strings
    """
    if hasattr(value, "model_dump"):               # Pydantic model
        value = value.model_dump()

    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if k in CONTACT_KEYS and v is not None:
                out[k] = "[REDACTED]"
            elif k in ID_KEYS and isinstance(v, (str, int)):
                out[k] = mask_number(str(v))
            else:
                out[k] = redact_for_logging(v)
        return out

    if isinstance(value, (list, tuple)):
        return [redact_for_logging(v) for v in value]

    if isinstance(value, str):
        return _redact_string(value)

    return value