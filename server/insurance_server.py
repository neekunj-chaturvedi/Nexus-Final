import sqlite3
from fastmcp import FastMCP
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from guardrails import mask_number


DB_PATH = "meridian.db"

mcp = FastMCP("insurance_server")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool(
    name="get_policy_details",
    description=(
        "Read-only policy lookup. Returns premium information, "
        "payment terms, and policy status for a single policy."
    )
)
def get_policy_details(policy_id: str):
    """
    Retrieve policy details with minimum necessary data.
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            policy_id,
            policy_number,
            policy_type,
            status,
            premium_amount,
            premium_frequency,
            payment_methods_allowed,
            start_date,
            renewal_date
        FROM policies
        WHERE policy_id = ?
        """,
        (policy_id,)
    )

    policy = cursor.fetchone()
    conn.close()

    if not policy:
        return {
            "error": f"Policy '{policy_id}' not found"
        }

    policy = dict(policy)   # (or whatever your variable is called)
    policy["policy_number"] = mask_number(policy["policy_number"])
    return policy

    # return dict(policy)


@mcp.tool(
    name="check_coverage_clause",
    description=(
        "Deterministically checks whether a scenario tag is covered "
        "under a policy based on covered and excluded scenario tags."
    )
)
def check_coverage_clause(
    policy_id: str,
    scenario_tag: str
):
    """
    Check whether a scenario is covered by policy clauses.
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            policy_id,
            status,
            covered_scenario_tags,
            excluded_scenario_tags
        FROM policies
        WHERE policy_id = ?
        """,
        (policy_id,)
    )

    policy = cursor.fetchone()
    conn.close()

    if not policy:
        return {
            "error": f"Policy '{policy_id}' not found"
        }

    covered_tags = {
        tag.strip().lower()
        for tag in (policy["covered_scenario_tags"] or "").split(",")
        if tag.strip()
    }

    excluded_tags = {
        tag.strip().lower()
        for tag in (policy["excluded_scenario_tags"] or "").split(",")
        if tag.strip()
    }

    scenario = scenario_tag.strip().lower()

    if scenario in excluded_tags:
        coverage_status = "excluded"
    elif scenario in covered_tags:
        coverage_status = "covered"
    else:
        coverage_status = "not_covered"

    return {
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "scenario_tag": scenario_tag,
        "coverage_status": coverage_status
    }


@mcp.tool(
    name="get_claim_status",
    description=(
        "Read-only claim status lookup. Returns claim status and "
        "tracking information. Does not provide settlement authority."
    )
)
def get_claim_status(claim_id: str):
    """
    Retrieve claim status information.
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            claim_id,
            policy_id,
            scenario_tag,
            status,
            filed_on,
            last_updated
        FROM claims
        WHERE claim_id = ?
        """,
        (claim_id,)
    )

    claim = cursor.fetchone()
    conn.close()

    if not claim:
        return {
            "error": f"Claim '{claim_id}' not found"
        }

    return dict(claim)


if __name__ == "__main__":
    mcp.run(transport="stdio")