from fastmcp import FastMCP
import sqlite3
import re 
# 1. First tell Python where the project root is
from pathlib import Path
import sys 

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from guardrails import minimize_account_fields
mcp = FastMCP()

DB_PATH = "meridian.db"


def get_db_connection():
    return sqlite3.connect(DB_PATH)


@mcp.tool(
    name="get_account_summary",
    description="Retrieves a minimized account summary based on the account ID and the caller's authorization scope.",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
def get_account_summary(account_id, caller_scope):
     # NEW: check the ID format before touching the database
    if not re.match(r"^ACC-\d{5}$", str(account_id)):
        raise ValueError("Invalid account_id format, expected ACC-XXXXX")

    # NEW: reject unknown scopes up front
    if caller_scope not in ("basic", "financial", "full"):
        raise ValueError("Invalid caller_scope, expected basic, financial or full")

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
        account_id,
        customer_id,
        account_number,
        account_type,
        status, 
        restriction_reason,
        auto_debit_allowed,
        balance,
        currency,
        opened_on
        FROM accounts
        WHERE account_id = ?
        """,
        (account_id,)
    )

    account = cursor.fetchone()
    conn.close()

    if account is None:
        raise LookupError("Account not found")

    account = dict(account)

    if caller_scope == "basic":
        # return {
        #     "account_id": account["account_id"],
        #     "account_type": account["account_type"],
        #     "status": account["status"],
        #     "currency": account["currency"]
        # }
        return minimize_account_fields(account, caller_scope)

    elif caller_scope == "financial":
        return {
            "account_id": account["account_id"],
            "account_type": account["account_type"],
            "status": account["status"],
            "balance": account["balance"],
            "currency": account["currency"]
        }

    elif caller_scope == "full":
        return account

    return {"error": "Invalid authorization scope"}


@mcp.tool(
    name="get_transaction_history",
    description="Retrieves the most recent transactions for the specified account, up to the requested limit.",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
def get_transaction_history(account_id, limit):

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            txn_id,
            account_id,
            txn_date,
            description,
            amount,
            direction,
            balance_after
        FROM transactions
        WHERE account_id = ?
        ORDER BY txn_date DESC
        LIMIT ?
        """,
        (account_id, limit)
    )

    transactions = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return transactions


@mcp.tool(
    name="get_linked_accounts",
    description="Retrieves all accounts linked to the specified customer with account information minimized according to the caller's authorization scope.",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
def get_linked_accounts(customer_id , caller_scope = "basic"):

    if not re.match(r"^CUS-\d{5}$", str(customer_id)):
        raise ValueError("Invalid customer_id format, expected CUS-XXXXX")
        
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
        account_id,
        account_type,
        account_number,
        status,
        restriction_reason,
        auto_debit_allowed,
        balance,
        currency,
        opened_on
    FROM accounts
    WHERE customer_id = ?
        """,
        (customer_id,)
    )

    accounts = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return [minimize_account_fields(a, caller_scope) for a in accounts]


if __name__ == "__main__":
    mcp.run(transport="stdio")