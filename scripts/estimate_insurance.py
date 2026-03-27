"""Insurance estimation engine combining DP-3 rates and NFIP flood data."""

import sqlite3
from config import DB_PATH, VALUE_ANCHOR, PROPERTY_TYPE_MAP


def get_age_bracket(year_built: int) -> str:
    """Determine age bracket from year built."""
    if year_built < 1980:
        return "pre_1980"
    elif year_built < 1990:
        return "1980s"
    elif year_built < 2000:
        return "1990s"
    elif year_built < 2010:
        return "2000s"
    elif year_built < 2020:
        return "2010s"
    else:
        return "2020_plus"


def estimate_insurance(
    property_type: str,
    year_built: int,
    estimated_value: float,
    flood_zone: str | None = None,
    db_path: str = DB_PATH,
) -> dict:
    """
    Estimate insurance costs for a property.

    Args:
        property_type: One of 'single_family_detached', 'attached_townhome',
                       'condo_unit', 'vacant_flip'
        year_built: Year the property was constructed
        estimated_value: Estimated property value in dollars
        flood_zone: Optional flood zone (e.g., 'AE', 'X', 'A')

    Returns:
        Dictionary with dp3 and flood estimates including low/mid/high ranges.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get base rate for property type
    cursor.execute(
        "SELECT base_annual_premium_mid FROM dp3_base_rates WHERE property_type = ?",
        (property_type,)
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Unknown property type: {property_type}")
    base_mid = row["base_annual_premium_mid"]

    # Get age multiplier
    age_bracket = get_age_bracket(year_built)
    cursor.execute(
        "SELECT multiplier FROM dp3_age_multipliers WHERE age_bracket = ?",
        (age_bracket,)
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Unknown age bracket: {age_bracket}")
    age_multiplier = row["multiplier"]

    # Value scaling: anchor at $150k
    value_multiplier = estimated_value / VALUE_ANCHOR

    # DP-3 estimate
    dp3_mid = round(base_mid * age_multiplier * value_multiplier, 2)
    dp3_low = round(dp3_mid * 0.70, 2)
    dp3_high = round(dp3_mid * 1.45, 2)

    result = {
        "property_type": property_type,
        "year_built": year_built,
        "estimated_value": estimated_value,
        "age_bracket": age_bracket,
        "age_multiplier": age_multiplier,
        "value_multiplier": round(value_multiplier, 4),
        "dp3_low": dp3_low,
        "dp3_mid": dp3_mid,
        "dp3_high": dp3_high,
    }

    # Flood estimate if zone provided
    if flood_zone:
        # Look up NFIP average for the corresponding occupancy type
        occupancy_type = PROPERTY_TYPE_MAP.get(property_type, 1)
        cursor.execute("""
            SELECT avg_premium, median_premium, policy_count
            FROM nfip_aggregates
            WHERE occupancy_type = ?
            ORDER BY policy_count DESC
            LIMIT 1
        """, (occupancy_type,))
        nfip_row = cursor.fetchone()

        # Get CRS discount
        if flood_zone.upper() in ("AE", "A", "AO", "AH", "VE", "V"):
            crs_category = "AE"
        else:
            crs_category = "X_B_C"

        cursor.execute(
            "SELECT discount_percentage FROM crs_discounts WHERE flood_zone_category = ?",
            (crs_category,)
        )
        crs_row = cursor.fetchone()
        crs_discount = crs_row["discount_percentage"] / 100 if crs_row else 0

        if nfip_row and nfip_row["avg_premium"]:
            flood_base = nfip_row["avg_premium"]
            flood_estimate = round(flood_base * (1 - crs_discount), 2)
        else:
            # Fallback: rough estimate based on zone
            flood_base = 1500 if crs_category == "AE" else 500
            flood_estimate = round(flood_base * (1 - crs_discount), 2)

        result["flood_zone"] = flood_zone
        result["flood_estimate"] = flood_estimate
        result["crs_discount_pct"] = crs_discount * 100

        # Combined estimates
        result["combined_low"] = round(dp3_low + flood_estimate, 2)
        result["combined_mid"] = round(dp3_mid + flood_estimate, 2)
        result["combined_high"] = round(dp3_high + flood_estimate, 2)
        result["combined_monthly_midpoint"] = round((dp3_mid + flood_estimate) / 12, 2)
    else:
        result["flood_estimate"] = None
        result["combined_low"] = dp3_low
        result["combined_mid"] = dp3_mid
        result["combined_high"] = dp3_high
        result["combined_monthly_midpoint"] = round(dp3_mid / 12, 2)

    # Check for pending rate case
    cursor.execute("SELECT pending_rate_case, rate_case_details FROM dp3_rate_case WHERE id=1")
    rate_case = cursor.fetchone()
    if rate_case and rate_case["pending_rate_case"]:
        result["rate_case_warning"] = rate_case["rate_case_details"]

    conn.close()
    return result
