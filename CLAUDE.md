# Insurance Data Mirror

## Purpose
Public mirror of insurance cost data for Pitt County NC residential properties. Feeds into Reilize Intelligence Hub for property insurance estimation.

## Architecture
- **Database:** SQLite at `db/insurance.db`
- **API source:** OpenFEMA NFIP Policies API (no auth, OData v4)
- **Manual source:** NC Rate Bureau DP-3 dwelling rates (entered via docs/entry.html)
- **Estimation:** `scripts/estimate_insurance.py` combines both sources

## Key Rules
- Never delete or overwrite existing data on API failure
- NFIP data is aggregated (not raw policies) - we store averages, medians, counts by ZIP+occupancy
- DP-3 rates are manually curated - always include source citation and last-verified date
- Rate case monitoring is informational only - flag changes, don't auto-update rates

## Database Tables
- `nfip_aggregates` - Aggregated flood insurance stats by ZIP and occupancy type
- `dp3_base_rates` - Base annual premiums by property type
- `dp3_age_multipliers` - Year-built adjustment factors
- `dp3_rate_case` - Pending regulatory rate case tracking
- `crs_discounts` - CRS flood discount percentages by zone

## ZIP Codes (Pitt County)
27834, 27835, 27858, 27828, 27829, 27837, 27863, 27880, 27886

## Occupancy Types (NFIP)
- 1 = Single family
- 2 = Two-to-four unit residential
- 3 = Other residential
