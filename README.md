# Insurance Data Mirror

Public mirror of insurance cost data for North Carolina residential properties, focused on Pitt County. Designed to support property insurance estimation for real estate investors.

## Data Sources

### 1. FEMA NFIP Policies (Automated)
- **Source:** [OpenFEMA API v2](https://www.fema.gov/api/open/v2/FimaNfipPolicies)
- **Coverage:** Pitt County NC ZIP codes (27834, 27835, 27858, 27828, 27829, 27837, 27863, 27880, 27886)
- **Update frequency:** Monthly via GitHub Actions
- **No API key required**

### 2. NC DP-3 Dwelling Rates (Manual)
- **Source:** North Carolina Rate Bureau approved dwelling rate filings
- **Coverage:** Pitt County base rates, age multipliers, CRS flood discounts
- **Update frequency:** As rate filings are approved (use the [data entry page](docs/entry.html))
- **Last verified:** March 2026

## Insurance Estimation

The estimation engine combines both sources to produce DP-3 dwelling insurance and flood insurance estimates for any residential property given:
- Property type (SFD, townhome, condo, vacant/flip)
- Year built
- Estimated value
- Flood zone (optional)

```bash
# Run the test script to see sample estimates
python scripts/test_estimates.py
```

## Database

SQLite database at `db/insurance.db` with tables:
- `nfip_aggregates` - Aggregated NFIP policy data by ZIP and occupancy type
- `dp3_base_rates` - DP-3 base annual premiums by property type
- `dp3_age_multipliers` - Age bracket multipliers
- `dp3_rate_case` - Pending rate case tracking
- `crs_discounts` - Community Rating System flood zone discounts

## GitHub Actions

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| `update-nfip.yml` | Monthly (1st, 6 AM EST) | Fetch and aggregate NFIP data |
| `monitor-rate-case.yml` | Weekly (Monday, 8 AM EST) | Check NCDOI for rate case updates |

## Setup

```bash
pip install -r requirements.txt
python scripts/init_db.py      # Create database and seed DP-3 data
python scripts/fetch_nfip.py   # Pull NFIP data from OpenFEMA
python scripts/test_estimates.py  # Verify estimation math
```

## License

Public domain data. FEMA NFIP data is US government work. NC Rate Bureau rates are published regulatory filings.
