import sqlite3
from datetime import datetime
from fastmcp import FastMCP
import re 
DB_PATH = "meridian.db"

mcp = FastMCP("concierge_ops_server")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool(
    name="get_customer_kyc_status",
    description="Returns raw KYC information for a customer. This is the only tool allowed to expose KYC data."
)
def get_customer_kyc_status(customer_id):

    if not re.match(r"^CUS-\d{5}$", str(customer_id)):
        raise ValueError("Invalid customer_id format, expected CUS-XXXXX")

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        """
        SELECT customer_id, kyc_status, kyc_verified_on
        FROM customers
        WHERE customer_id = ?
        """,
        (customer_id,)
    ).fetchone()
    conn.close()

    if row is None:
        raise LookupError("Customer not found")

    return dict(row)


HARD_CATEGORIES = {
    "financial_hardship",
    "safeguarding_concern",
    "compliance_override_request",
}
VALID_CATEGORIES = HARD_CATEGORIES | {"none"}

# Flags on the customer's record that also force a human review
HARD_FLAG_TYPES = HARD_CATEGORIES | {"vulnerable_customer"}

CONFIDENCE_THRESHOLD = 0.80


@mcp.tool(
    name="run_escalation_check",
    description="Deterministic escalation decision using active escalation flags and confidence score."
)
def run_escalation_check(
    customer_id: str,
    request_category: str,
    draft_confidence: float
):

    # ---- 0. Validate inputs: anything unexpected is rejected, never ignored ----
    if not re.match(r"^CUS-\d{5}$", str(customer_id)):
        raise ValueError("Invalid customer_id format, expected CUS-XXXXX")

    if request_category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid request_category, expected one of {sorted(VALID_CATEGORIES)}")

    try:
        confidence = float(draft_confidence)
    except (TypeError, ValueError):
        raise ValueError("draft_confidence must be a number")
    if not 0.0 <= confidence <= 1.0:       # also rejects NaN
        raise ValueError("draft_confidence must be between 0.0 and 1.0")

    # ---- 1. Read the customer's active flags ----
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    try:
        if conn.execute(
            "SELECT 1 FROM customers WHERE customer_id = ?", (customer_id,)
        ).fetchone() is None:
            raise LookupError("Customer not found")

        active_flags = conn.execute(
            """
            SELECT flag_type, raised_on
            FROM escalation_flags
            WHERE customer_id = ? AND active = 1
            """,
            (customer_id,)
        ).fetchall()
    finally:
        conn.close()

    # ---- 2. HARD escalation - runs first, ignores confidence completely ----
    hard_reasons = []

    if request_category in HARD_CATEGORIES:
        hard_reasons.append(f"Hard category from intake: {request_category}")

    for flag in active_flags:
        if flag["flag_type"] in HARD_FLAG_TYPES:
            hard_reasons.append(
                f"Active flag on record: {flag['flag_type']} (since {flag['raised_on']})"
            )

    if hard_reasons:
        return {
            "customer_id": customer_id,
            "request_category": request_category,
            "draft_confidence": confidence,
            "escalate": True,
            "escalation_type": "hard",
            "reasons": hard_reasons,
        }

    # ---- 3. Confidence-based escalation - only reached if no hard rule fired ----
    if confidence < CONFIDENCE_THRESHOLD:
        return {
            "customer_id": customer_id,
            "request_category": request_category,
            "draft_confidence": confidence,
            "escalate": True,
            "escalation_type": "confidence",
            "reasons": [f"Confidence {confidence} is below threshold {CONFIDENCE_THRESHOLD}"],
        }

    # ---- 4. Safe to resolve automatically ----
    return {
        "customer_id": customer_id,
        "request_category": request_category,
        "draft_confidence": confidence,
        "escalate": False,
        "escalation_type": "none",
        "reasons": [],
    }
@mcp.tool(
    name="send_customer_notification",
    description="Sends a customer notification after applying KYC-based communication controls and logs the interaction."
)
def send_customer_notification(
    customer_id: str,
    channel: str,
    message: str
):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            kyc_status,
            preferred_channel
        FROM customers
        WHERE customer_id = ?
        """,
        (customer_id,)
    )

    customer = cursor.fetchone()

    if not customer:
        conn.close()
        return {
            "sent": False,
            "reason": "Customer not found"
        }

    kyc_status = customer["kyc_status"]

    if kyc_status != "verified":
        conn.close()

        return {
            "sent": False,
            "reason": f"Notification blocked. KYC status is '{kyc_status}'"
        }

    sanitized_message = message.strip()[:1000]

    cursor.execute(
        """
        INSERT INTO interaction_log
        (
            customer_id,
            channel,
            direction,
            summary,
            request_id
        )
        VALUES
        (?, ?, ?, ?, ?)
        """,
        (
            customer_id,
            channel,
            "outbound",
            sanitized_message,
            f"NOTIF-{datetime.utcnow().timestamp()}"
        )
    )

    conn.commit()
    conn.close()

    return {
        "sent": True,
        "customer_id": customer_id,
        "channel": channel,
        "message_preview": sanitized_message[:100]
    }


@mcp.tool(
    name="write_audit_log",
    description="Creates an immutable audit trail entry."
)
def write_audit_log(
    action_type: str,
    performed_by: str,
    customer_id: str,
    outcome: str,
    details: str
):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO audit_log
        (
            action_type,
            performed_by,
            customer_id,
            outcome,
            details
        )
        VALUES
        (?, ?, ?, ?, ?)
        """,
        (
            action_type,
            performed_by,
            customer_id,
            outcome,
            details
        )
    )

    audit_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "success": True,
        "audit_id": audit_id,
        "action_type": action_type,
        "outcome": outcome
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")