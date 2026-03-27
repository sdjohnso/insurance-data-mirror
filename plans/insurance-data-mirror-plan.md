# Insurance Data Mirror
**Branch:** `main`
**Created:** 2026-03-27
**Status:** In Progress - Phase 1, Step 1.3
**Next Action:** Create GitHub repo, push initial code, and deploy entry page via GitHub Pages
**Purpose:** Public mirror of Pitt County NC insurance cost data (NFIP flood + DP-3 dwelling rates) for Reilize property analysis
**Security:** secaudit required before any step touching DB, APIs, endpoints, or user input is marked complete

## Context

Scott wants to add an insurance estimation layer to Reilize. Two data sources: (1) FEMA's OpenFEMA NFIP Policies API for flood insurance aggregates, and (2) manually curated NC Rate Bureau DP-3 dwelling rates. This project mirrors the pattern of the NCDOT transportation mirror - a standalone public data repo with GitHub Actions automation that Reilize consumes. The Reilize AI integration will be handled separately.

## Architecture

```
insurance-data-mirror/
├── db/
│   ├── schema.sql          # Table definitions
│   ├── seed_dp3.sql        # Initial DP-3 rate data
│   └── insurance.db        # SQLite database (generated)
├── scripts/
│   ├── config.py           # API URLs, ZIP codes, constants
│   ├── init_db.py          # Create tables + seed data
│   ├── fetch_nfip.py       # OpenFEMA API fetcher + aggregator
│   ├── estimate_insurance.py  # Estimation engine
│   └── test_estimates.py   # Verification script
├── docs/
│   └── entry.html          # GitHub Pages DP-3 rate entry form
├── .github/workflows/
│   ├── update-nfip.yml     # Monthly NFIP data refresh
│   └── monitor-rate-case.yml  # Weekly NCDOI press release monitor
└── README.md
```

**Database tables:**
- `nfip_aggregates` - NFIP data aggregated by ZIP + occupancy type
- `dp3_base_rates` - Base annual premiums by property type
- `dp3_age_multipliers` - Year-built adjustment factors
- `dp3_rate_case` - Pending rate case tracking
- `crs_discounts` - CRS flood discount percentages

**Data flow:**
- OpenFEMA API -> fetch_nfip.py -> nfip_aggregates table (automated monthly)
- NC Rate Bureau filings -> entry.html -> generates SQL -> run against db (manual)
- estimate_insurance.py reads both tables to produce estimates
- Reilize will consume the estimation function (separate integration project)

## Files to Modify

| File | Why It's Being Modified |
|------|------------------------|
| `db/schema.sql` | DONE - Table definitions |
| `db/seed_dp3.sql` | DONE - Initial rate data |
| `scripts/config.py` | DONE - Configuration |
| `scripts/init_db.py` | DONE - DB initialization |
| `scripts/fetch_nfip.py` | DONE - API fetcher |
| `scripts/estimate_insurance.py` | DONE - Estimation engine |
| `scripts/test_estimates.py` | DONE - Verification |
| `docs/entry.html` | DONE - Data entry page |
| `.github/workflows/update-nfip.yml` | DONE - Monthly NFIP workflow |
| `.github/workflows/monitor-rate-case.yml` | DONE - Weekly rate case monitor |
| `README.md` | DONE - Project documentation |
| `CLAUDE.md` | DONE - AI context |

## Success Criteria

1. `test_estimates.py` produces correct math for all property types and age brackets
2. `fetch_nfip.py` successfully pulls and aggregates real NFIP data for all 9 Pitt County ZIPs
3. Entry page generates valid SQL for updating DP-3 rates
4. GitHub Actions workflows pass on push
5. GitHub Pages serves the entry page at a public URL
6. estimation function returns complete dict with dp3 low/mid/high, flood estimate, combined values, and monthly midpoint

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-27 | Use `ratedFloodZone` field from API, not `floodZone` | API research confirmed this is the correct field name |
| 2026-03-27 | Aggregate NFIP data rather than storing raw policies | 72M+ total policies in dataset; raw storage impractical and unnecessary |
| 2026-03-27 | Entry page generates SQL rather than direct DB writes | Keeps it simple - no backend needed, SQL can be reviewed before execution |
| 2026-03-27 | Flood fallback uses $1500 AE / $500 X when no NFIP data | Reasonable defaults until real data is pulled |

## Phase 1: Foundation (Core Code + Database)

**Goal:** All core scripts written, database initialized, estimation math verified.

- [x] **Step 1.1: Database schema and seed data**
  - Resources: `db/schema.sql`, `db/seed_dp3.sql`
  - [x] Create schema with all 5 tables
  - [x] Seed DP-3 rates, age multipliers, rate case, CRS discounts
  - Validation: `init_db.py` runs and prints all seeded values correctly
  - DONE - Verified 2026-03-27

- [x] **Step 1.2: Estimation engine and tests**
  - Resources: `scripts/estimate_insurance.py`, `scripts/test_estimates.py`, `scripts/config.py`
  - [x] Estimation function with value scaling, age multipliers, flood zone handling
  - [x] Test script with 5 sample properties
  - [x] Math verification output
  - Validation: Test output matches manual calculation (verified: $3,264.00 for 1965 SFR)
  - DONE - Verified 2026-03-27

- [ ] **Step 1.3: GitHub repo + Pages deployment**
  - Resources: All project files
  - [ ] Initialize git repo
  - [ ] Create GitHub repo (public, matching NCDOT mirror pattern)
  - [ ] Enable GitHub Pages on docs/ folder
  - [ ] Push initial commit
  - Validation: Entry page accessible at GitHub Pages URL
  - **Next Session Prompt:** I'm on branch `main`. Core code is written and tested. Review `plans/insurance-data-mirror-plan.md` and continue with Step 1.3 - create the GitHub repo and enable Pages.

## Phase 2: Live Data (NFIP API Pull)

**Goal:** Real NFIP flood insurance data pulled and stored.

- [ ] **Step 2.1: Fetch NFIP data from OpenFEMA**
  - Resources: `scripts/fetch_nfip.py`, `scripts/config.py`, `db/insurance.db`
  - [ ] Run fetch_nfip.py against all 9 Pitt County ZIPs
  - [ ] Verify aggregates stored correctly
  - [ ] Re-run test_estimates.py to confirm flood estimates use real data
  - Validation: nfip_aggregates table has rows for each ZIP+occupancy combo, flood estimates in test output reflect real averages
  - **Next Session Prompt:** I'm on branch `main`. GitHub repo is set up. Review `plans/insurance-data-mirror-plan.md` and continue with Step 2.1 - run the NFIP data fetch.

- [ ] **Step 2.2: Verify GitHub Actions workflows**
  - Resources: `.github/workflows/update-nfip.yml`, `.github/workflows/monitor-rate-case.yml`
  - [ ] Manually trigger update-nfip workflow
  - [ ] Manually trigger monitor-rate-case workflow
  - [ ] Verify both pass and produce summary output
  - Validation: Both workflows complete successfully in GitHub Actions tab
  - **Next Session Prompt:** I'm on branch `main`. NFIP data is pulled. Review `plans/insurance-data-mirror-plan.md` and continue with Step 2.2 - verify the GitHub Actions workflows.

## Phase 3: Polish + Handoff

**Goal:** Everything documented, reminder set, ready for Reilize integration.

- [ ] **Step 3.1: Set reminder for NCDOI rate case hearing**
  - [ ] Calendar reminder for May 4, 2026 NCDOI hearing
  - [ ] Include link to entry page and NCDOI dwelling rates page
  - Validation: Reminder appears on calendar

- [ ] **Step 3.2: Final verification and commit**
  - [ ] Ensure db/insurance.db has both NFIP and DP-3 data
  - [ ] Run full test suite one more time
  - [ ] Push final state
  - Validation: All tests pass, repo is clean

## Follow-Up Plans

- **Reilize Integration** - Wire estimate_insurance.py into Reilize Intelligence Hub API tools. The Reilize AI will handle this separately.
- **Multi-County Expansion** - Extend to additional NC counties beyond Pitt.
- **Rate Case Auto-Update** - When NCDOI ruling comes in, auto-generate new seed SQL from the entry page.
