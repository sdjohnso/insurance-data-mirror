"""Initialize the insurance database and seed DP-3 reference data."""

import sqlite3
from config import DB_PATH, SCHEMA_PATH, SEED_PATH


def init_database():
    """Create tables and seed DP-3 data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create schema
    with open(SCHEMA_PATH, "r") as f:
        cursor.executescript(f.read())
    print(f"Schema created at {DB_PATH}")

    # Seed DP-3 data
    with open(SEED_PATH, "r") as f:
        cursor.executescript(f.read())
    print("DP-3 reference data seeded")

    # Verify
    cursor.execute("SELECT property_type_label, base_annual_premium_mid FROM dp3_base_rates")
    print("\nDP-3 Base Rates:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: ${row[1]:,.0f}")

    cursor.execute("SELECT age_bracket_label, multiplier FROM dp3_age_multipliers ORDER BY year_range_start")
    print("\nAge Multipliers:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}x")

    cursor.execute("SELECT pending_rate_case, rate_case_details FROM dp3_rate_case WHERE id=1")
    row = cursor.fetchone()
    if row and row[0]:
        print(f"\nPending Rate Case: {row[1]}")

    cursor.execute("SELECT flood_zone_label, discount_percentage FROM crs_discounts")
    print("\nCRS Discounts:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}%")

    conn.commit()
    conn.close()
    print(f"\nDatabase ready: {DB_PATH}")


if __name__ == "__main__":
    init_database()
