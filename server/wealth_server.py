import sqlite3
from fastmcp import FastMCP

DB_PATH = "meridian.db"

mcp = FastMCP("wealth_server")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool(
    name="get_portfolio_summary",
    description=(
        "Read-only portfolio lookup. Returns a minimized portfolio "
        "summary based on caller scope."
    )
)
def get_portfolio_summary(
    portfolio_id: str,
    caller_scope: str
):
    """
    Portfolio lookup with field minimization.
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    if caller_scope == "customer":

        cursor.execute(
            """
            SELECT
                portfolio_id,
                portfolio_number,
                status,
                total_value,
                holdings,
                last_valued_on
            FROM portfolios
            WHERE portfolio_id = ?
            """,
            (portfolio_id,)
        )

    elif caller_scope == "advisor":

        cursor.execute(
            """
            SELECT
                portfolio_id,
                customer_id,
                portfolio_number,
                status,
                total_value,
                holdings,
                last_valued_on
            FROM portfolios
            WHERE portfolio_id = ?
            """,
            (portfolio_id,)
        )

    else:

        cursor.execute(
            """
            SELECT
                portfolio_id,
                portfolio_number,
                status
            FROM portfolios
            WHERE portfolio_id = ?
            """,
            (portfolio_id,)
        )

    portfolio = cursor.fetchone()
    conn.close()

    if not portfolio:
        return {
            "error": f"Portfolio '{portfolio_id}' not found"
        }

    return dict(portfolio)


@mcp.tool(
    name="get_investment_product_details",
    description=(
        "Read-only lookup for a single investment product."
    )
)
def get_investment_product_details(product_id: str):
    """
    Retrieve investment product details.
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            product_id,
            name,
            asset_class,
            risk_level,
            min_investment,
            expense_ratio,
            description
        FROM investment_products
        WHERE product_id = ?
        """,
        (product_id,)
    )

    product = cursor.fetchone()
    conn.close()

    if not product:
        return {
            "error": f"Product '{product_id}' not found"
        }

    return dict(product)


@mcp.tool(
    name="check_product_suitability",
    description=(
        "Determines whether an investment product is suitable "
        "for a supplied risk profile. Read-only operation."
    )
)
def check_product_suitability(
    product_id: str,
    risk_profile: str
):
    """
    Product suitability check.
    No customer data used other than the supplied risk profile.
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            product_id,
            name,
            risk_level,
            suitable_risk_profiles
        FROM investment_products
        WHERE product_id = ?
        """,
        (product_id,)
    )

    product = cursor.fetchone()
    conn.close()

    if not product:
        return {
            "error": f"Product '{product_id}' not found"
        }

    suitable_profiles = {
        item.strip().lower()
        for item in (
            product["suitable_risk_profiles"] or ""
        ).split(",")
        if item.strip()
    }

    supplied_profile = risk_profile.lower().strip()

    is_suitable = supplied_profile in suitable_profiles

    return {
        "product_id": product["product_id"],
        "product_name": product["name"],
        "product_risk_level": product["risk_level"],
        "risk_profile": risk_profile,
        "suitable": is_suitable
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")