-- Seed DP-3 Rate Data
-- Source: North Carolina Rate Bureau dwelling rate filing, 2023 settlement
-- Verified: March 2026

-- Base annual premiums by property type
INSERT OR REPLACE INTO dp3_base_rates (property_type, property_type_label, base_annual_premium_mid, last_verified, source_citation) VALUES
('single_family_detached', 'Single Family Detached', 1600.0, '2026-03-27', 'North Carolina Rate Bureau dwelling rate filing 2023 settlement, verified March 2026'),
('attached_townhome', 'Attached Fee-Simple Townhome', 1550.0, '2026-03-27', 'North Carolina Rate Bureau dwelling rate filing 2023 settlement, verified March 2026'),
('condo_unit', 'Condo Unit', 650.0, '2026-03-27', 'North Carolina Rate Bureau dwelling rate filing 2023 settlement, verified March 2026'),
('vacant_flip', 'Vacant / Flip', 2100.0, '2026-03-27', 'North Carolina Rate Bureau dwelling rate filing 2023 settlement, verified March 2026');

-- Age bracket multipliers
INSERT OR REPLACE INTO dp3_age_multipliers (age_bracket, age_bracket_label, multiplier, year_range_start, year_range_end) VALUES
('pre_1980', 'Pre-1980', 1.70, NULL, 1979),
('1980s', '1980s', 1.40, 1980, 1989),
('1990s', '1990s', 1.15, 1990, 1999),
('2000s', '2000s', 1.00, 2000, 2009),
('2010s', '2010s', 0.85, 2010, 2019),
('2020_plus', '2020+', 0.70, 2020, NULL);

-- Pending rate case
INSERT OR REPLACE INTO dp3_rate_case (id, pending_rate_case, rate_case_details, last_verified, source_citation) VALUES
(1, 1, 'NCRB filed 68.3% average dwelling rate increase October 30, 2025. NCDOI hearing May 4, 2026. Outcome pending.', '2026-03-27', 'North Carolina Rate Bureau dwelling rate filing 2023 settlement, verified March 2026');

-- CRS discounts for Pitt County
INSERT OR REPLACE INTO crs_discounts (flood_zone_category, flood_zone_label, discount_percentage) VALUES
('AE', 'AE Zone (Special Flood Hazard Area)', 10.0),
('X_B_C', 'X, B, and C Zones (Moderate/Low Risk)', 5.0);
