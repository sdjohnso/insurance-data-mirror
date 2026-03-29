"""Fetch NFIP policy data from OpenFEMA API and aggregate by ZIP + occupancy type."""

import json
import sqlite3
import statistics
import time
from collections import defaultdict

import requests

from config import (
    DB_PATH,
    NFIP_SELECT_FIELDS,
    OCCUPANCY_LABELS,
    OPENFEMA_BASE_URL,
    OPENFEMA_DELAY_SECONDS,
    OPENFEMA_PAGE_SIZE,
    OPENFEMA_TIMEOUT,
    PITT_COUNTY_ZIPS,
)


def fetch_policies_for_zip(zip_code: str, max_retries: int = 3) -> list[dict]:
    """Fetch all NFIP policies for a given ZIP code with pagination and retry."""
    all_records = []
    skip = 0
    select = ",".join(NFIP_SELECT_FIELDS)

    while True:
        url = (
            f"{OPENFEMA_BASE_URL}"
            f"?$filter=reportedZipCode eq '{zip_code}'"
            f"&$select={select}"
            f"&$top={OPENFEMA_PAGE_SIZE}"
            f"&$skip={skip}"
            f"&$count=true"
        )
        print(f"  Fetching ZIP {zip_code} (offset {skip})...")

        # Retry logic for FEMA's flaky connections
        resp = None
        for attempt in range(1, max_retries + 1):
            try:
                resp = requests.get(url, timeout=OPENFEMA_TIMEOUT)
                resp.raise_for_status()
                break
            except (requests.RequestException, requests.ConnectionError) as e:
                if attempt < max_retries:
                    wait = 10 * attempt
                    print(f"    Attempt {attempt} failed, retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    raise

        data = resp.json()

        records = data.get("FimaNfipPolicies", [])
        if not records:
            break

        all_records.extend(records)
        total = data.get("metadata", {}).get("count", 0)

        if len(all_records) >= total or len(records) < OPENFEMA_PAGE_SIZE:
            break

        skip += OPENFEMA_PAGE_SIZE
        time.sleep(OPENFEMA_DELAY_SECONDS)

    return all_records


def aggregate_policies(records: list[dict]) -> dict:
    """Aggregate policies by occupancy type. Returns dict keyed by occupancy_type."""
    by_occupancy = defaultdict(list)

    for r in records:
        occ = r.get("occupancyType")
        premium = r.get("totalInsurancePremiumOfThePolicy")
        if occ is not None and premium is not None and premium > 0:
            by_occupancy[occ].append(r)

    results = {}
    for occ_type, policies in by_occupancy.items():
        if occ_type not in OCCUPANCY_LABELS:
            continue

        premiums = [p["totalInsurancePremiumOfThePolicy"] for p in policies]
        building_covs = [p.get("totalBuildingInsuranceCoverage", 0) or 0 for p in policies]
        contents_covs = [p.get("totalContentsInsuranceCoverage", 0) or 0 for p in policies]

        # Flood zone distribution
        zone_counts = defaultdict(int)
        for p in policies:
            zone = p.get("ratedFloodZone", "Unknown") or "Unknown"
            zone_counts[zone] += 1

        results[occ_type] = {
            "policy_count": len(policies),
            "avg_premium": round(statistics.mean(premiums), 2),
            "median_premium": round(statistics.median(premiums), 2),
            "min_premium": min(premiums),
            "max_premium": max(premiums),
            "avg_building_coverage": round(statistics.mean(building_covs), 2),
            "avg_contents_coverage": round(statistics.mean(contents_covs), 2),
            "flood_zone_distribution": dict(zone_counts),
        }

    return results


def upsert_aggregates(conn: sqlite3.Connection, zip_code: str, aggregates: dict):
    """Upsert aggregated data into the database."""
    cursor = conn.cursor()
    for occ_type, agg in aggregates.items():
        cursor.execute("""
            INSERT INTO nfip_aggregates (
                zip_code, occupancy_type, occupancy_label, policy_count,
                avg_premium, median_premium, min_premium, max_premium,
                avg_building_coverage, avg_contents_coverage,
                flood_zone_distribution, fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(zip_code, occupancy_type) DO UPDATE SET
                policy_count = excluded.policy_count,
                avg_premium = excluded.avg_premium,
                median_premium = excluded.median_premium,
                min_premium = excluded.min_premium,
                max_premium = excluded.max_premium,
                avg_building_coverage = excluded.avg_building_coverage,
                avg_contents_coverage = excluded.avg_contents_coverage,
                flood_zone_distribution = excluded.flood_zone_distribution,
                fetched_at = excluded.fetched_at
        """, (
            zip_code,
            occ_type,
            OCCUPANCY_LABELS.get(occ_type, f"Type {occ_type}"),
            agg["policy_count"],
            agg["avg_premium"],
            agg["median_premium"],
            agg["min_premium"],
            agg["max_premium"],
            agg["avg_building_coverage"],
            agg["avg_contents_coverage"],
            json.dumps(agg["flood_zone_distribution"]),
        ))
    conn.commit()


def run():
    """Main fetch and aggregate pipeline."""
    conn = sqlite3.connect(DB_PATH)

    print("Fetching NFIP policies for Pitt County ZIP codes...\n")
    total_policies = 0

    for zip_code in PITT_COUNTY_ZIPS:
        try:
            records = fetch_policies_for_zip(zip_code)
            if not records:
                print(f"  ZIP {zip_code}: No records found\n")
                continue

            aggregates = aggregate_policies(records)
            upsert_aggregates(conn, zip_code, aggregates)

            zip_total = sum(a["policy_count"] for a in aggregates.values())
            total_policies += zip_total
            print(f"  ZIP {zip_code}: {zip_total} policies across {len(aggregates)} occupancy types\n")

            time.sleep(OPENFEMA_DELAY_SECONDS)
        except requests.RequestException as e:
            print(f"  ZIP {zip_code}: API error - {e}\n")
            continue

    print(f"\nDone. {total_policies} total policies aggregated across {len(PITT_COUNTY_ZIPS)} ZIP codes.")
    conn.close()


if __name__ == "__main__":
    run()
