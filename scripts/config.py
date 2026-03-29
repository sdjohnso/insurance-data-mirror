"""Configuration for insurance data mirror."""

import os

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "db", "insurance.db")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "db", "schema.sql")
SEED_PATH = os.path.join(PROJECT_ROOT, "db", "seed_dp3.sql")

# OpenFEMA API
OPENFEMA_BASE_URL = "https://www.fema.gov/api/open/v2/FimaNfipPolicies"
OPENFEMA_PAGE_SIZE = 1000
OPENFEMA_TIMEOUT = 300  # FEMA servers are slow - need 5 min timeout
OPENFEMA_DELAY_SECONDS = 5  # Generous delay between requests

# Pitt County ZIP codes
PITT_COUNTY_ZIPS = [
    "27834", "27835", "27858", "27828", "27829",
    "27837", "27863", "27880", "27886",
]

# Fields to fetch from OpenFEMA
NFIP_SELECT_FIELDS = [
    "reportedZipCode",
    "ratedFloodZone",
    "totalBuildingInsuranceCoverage",
    "totalContentsInsuranceCoverage",
    "totalInsurancePremiumOfThePolicy",
    "occupancyType",
]

# Occupancy type mapping
OCCUPANCY_LABELS = {
    1: "Single Family",
    2: "Two-to-Four Unit Residential",
    3: "Other Residential",
}

# DP-3 property type mapping to NFIP occupancy
PROPERTY_TYPE_MAP = {
    "single_family_detached": 1,
    "attached_townhome": 1,
    "condo_unit": 3,
    "vacant_flip": 1,
}

# Value scaling anchor for DP-3 estimation
VALUE_ANCHOR = 150_000
