"""Test the insurance estimation function with sample properties."""

import json
import sys
import os

# Ensure we can import sibling modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from estimate_insurance import estimate_insurance
from init_db import init_database


def fmt_dollars(val):
    if val is None:
        return "N/A"
    return f"${val:,.2f}"


def print_estimate(label: str, est: dict):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(f"  Type:           {est['property_type']}")
    print(f"  Year Built:     {est['year_built']} ({est['age_bracket']}, {est['age_multiplier']}x)")
    print(f"  Value:          {fmt_dollars(est['estimated_value'])}")
    print(f"  Value Scale:    {est['value_multiplier']}x (anchor $150k)")
    print()
    print(f"  DP-3 Low:       {fmt_dollars(est['dp3_low'])}/yr")
    print(f"  DP-3 Mid:       {fmt_dollars(est['dp3_mid'])}/yr")
    print(f"  DP-3 High:      {fmt_dollars(est['dp3_high'])}/yr")

    if est.get("flood_zone"):
        print(f"\n  Flood Zone:     {est['flood_zone']}")
        print(f"  Flood Est:      {fmt_dollars(est['flood_estimate'])}/yr")
        print(f"  CRS Discount:   {est.get('crs_discount_pct', 0)}%")

    print(f"\n  Combined Low:   {fmt_dollars(est['combined_low'])}/yr")
    print(f"  Combined Mid:   {fmt_dollars(est['combined_mid'])}/yr")
    print(f"  Combined High:  {fmt_dollars(est['combined_high'])}/yr")
    print(f"  Monthly (mid):  {fmt_dollars(est['combined_monthly_midpoint'])}/mo")

    if est.get("rate_case_warning"):
        print(f"\n  WARNING: {est['rate_case_warning']}")


def main():
    # Ensure DB is initialized
    print("Initializing database...\n")
    init_database()

    test_cases = [
        {
            "label": "1965 SFR in AE flood zone, $180k value",
            "args": {
                "property_type": "single_family_detached",
                "year_built": 1965,
                "estimated_value": 180_000,
                "flood_zone": "AE",
            },
        },
        {
            "label": "2022 Townhome, $300k value, no flood zone",
            "args": {
                "property_type": "attached_townhome",
                "year_built": 2022,
                "estimated_value": 300_000,
            },
        },
        {
            "label": "2005 Condo, $150k value, X zone",
            "args": {
                "property_type": "condo_unit",
                "year_built": 2005,
                "estimated_value": 150_000,
                "flood_zone": "X",
            },
        },
        {
            "label": "1985 Vacant/Flip, $120k value, AE zone",
            "args": {
                "property_type": "vacant_flip",
                "year_built": 1985,
                "estimated_value": 120_000,
                "flood_zone": "AE",
            },
        },
        {
            "label": "2015 SFR, $250k value, no flood",
            "args": {
                "property_type": "single_family_detached",
                "year_built": 2015,
                "estimated_value": 250_000,
            },
        },
    ]

    print("\n" + "="*60)
    print("  INSURANCE ESTIMATION TEST RESULTS")
    print("="*60)

    for tc in test_cases:
        est = estimate_insurance(**tc["args"])
        print_estimate(tc["label"], est)

    # Verify math manually for first case
    print("\n" + "="*60)
    print("  MATH VERIFICATION (Case 1: 1965 SFR, $180k, AE)")
    print("="*60)
    print(f"  Base mid:       $1,600")
    print(f"  Age mult:       1.70x (pre-1980)")
    print(f"  Value mult:     180000/150000 = 1.2x")
    print(f"  DP3 mid:        1600 * 1.70 * 1.20 = ${1600 * 1.70 * 1.20:,.2f}")
    print(f"  DP3 low (70%):  ${1600 * 1.70 * 1.20 * 0.70:,.2f}")
    print(f"  DP3 high (145%):${1600 * 1.70 * 1.20 * 1.45:,.2f}")


if __name__ == "__main__":
    main()
