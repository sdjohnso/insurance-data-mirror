-- Insurance Data Mirror Schema
-- Tables for NFIP flood insurance aggregates and DP-3 dwelling rate reference data

-- ============================================================
-- NFIP Aggregated Policy Data (from OpenFEMA API)
-- ============================================================

CREATE TABLE IF NOT EXISTS nfip_aggregates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zip_code TEXT NOT NULL,
    occupancy_type INTEGER NOT NULL,  -- 1=SFR, 2=2-4 unit, 3=other residential
    occupancy_label TEXT NOT NULL,
    policy_count INTEGER NOT NULL DEFAULT 0,
    avg_premium REAL,
    median_premium REAL,
    min_premium REAL,
    max_premium REAL,
    avg_building_coverage REAL,
    avg_contents_coverage REAL,
    flood_zone_distribution TEXT,  -- JSON: {"AE": 45, "X": 30, "A": 10, ...}
    fetched_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(zip_code, occupancy_type)
);

CREATE INDEX IF NOT EXISTS idx_nfip_zip ON nfip_aggregates(zip_code);
CREATE INDEX IF NOT EXISTS idx_nfip_occupancy ON nfip_aggregates(occupancy_type);

-- ============================================================
-- DP-3 Dwelling Insurance Base Rates (manually curated)
-- ============================================================

CREATE TABLE IF NOT EXISTS dp3_base_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_type TEXT NOT NULL UNIQUE,  -- 'single_family_detached', 'attached_townhome', 'condo_unit', 'vacant_flip'
    property_type_label TEXT NOT NULL,
    base_annual_premium_mid REAL NOT NULL,
    last_verified TEXT NOT NULL,
    source_citation TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- DP-3 Age Bracket Multipliers
-- ============================================================

CREATE TABLE IF NOT EXISTS dp3_age_multipliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    age_bracket TEXT NOT NULL UNIQUE,  -- 'pre_1980', '1980s', '1990s', '2000s', '2010s', '2020_plus'
    age_bracket_label TEXT NOT NULL,
    multiplier REAL NOT NULL,
    year_range_start INTEGER,
    year_range_end INTEGER,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- DP-3 Rate Case Tracking
-- ============================================================

CREATE TABLE IF NOT EXISTS dp3_rate_case (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pending_rate_case INTEGER NOT NULL DEFAULT 0,  -- boolean: 0=false, 1=true
    rate_case_details TEXT,
    last_verified TEXT NOT NULL,
    source_citation TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- CRS (Community Rating System) Flood Discounts for Pitt County
-- ============================================================

CREATE TABLE IF NOT EXISTS crs_discounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flood_zone_category TEXT NOT NULL UNIQUE,  -- 'AE', 'X_B_C'
    flood_zone_label TEXT NOT NULL,
    discount_percentage REAL NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
