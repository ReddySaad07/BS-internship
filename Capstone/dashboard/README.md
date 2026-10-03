# Bluestock Mutual Fund Analytics Dashboard — completion package

## Contents
- `Dashboard.pdf`: four-page PDF report generated from the actual supplied CSV data.
- `dashboard_exports/Page_1_Industry_Overview.png` through `Page_4_SIP_Market_Trends.png`: four 16:9 PNG exports.
- `data/`: supplied processed CSVs used to produce the report.
- `powerbi_support/`: starter DAX, relationship guidance and importable Bluestock theme JSON.

## Important honesty note
A native `.pbix` was **not** generated or modified. Power BI Desktop is not available in this execution environment, and a valid PBIX cannot be fabricated by renaming another file. Use the supplied CSVs and support files to complete the native report in Power BI Desktop. The PDF/PNGs are genuine data-derived alternatives, not screenshots exported from Power BI.

## Dataset-derived dashboard figures
- AUM is summed across AMCs at the latest supplied snapshot on/before 31 Dec 2025.
- FY25 SIP inflow is the sum of monthly values from Apr 2024 to Mar 2025.
- Folios uses the latest supplied month on/before Dec 2025.
- Scheme count is the actual number of rows in `01_fund_master.csv`.

These values may not match the target values in the task brief because the supplied archive contains a limited dataset. No requested target KPI was copied without verification.

## Suggested Power BI completion steps
1. Open Power BI Desktop and import CSVs from `data/` (Text/CSV).
2. Import `powerbi_support/Bluestock_Theme.json` via View → Themes → Browse for themes.
3. Build relationships using `powerbi_support/Bluestock_Model_and_Relationships.md`; create a Date table and avoid fact-to-fact joins.
4. Add measures from `powerbi_support/Bluestock_DAX_Measures.dax` after checking names.
5. Build four report pages and add slicers/drill-through/tooltips.
6. Save as `bluestock_mf_dashboard.pbix`; export PDF and each page to PNG from Power BI Desktop if native exports are required.

## Data limitations that block exact completion
- Performance table date column is missing/invalid for 40 of 40 rows.
- NAV data extends beyond the requested 2022–2025 reporting window; exports filter to 2022–2025.
- Benchmark data extends beyond the requested 2022–2025 reporting window; exports filter to 2022–2025.
- Fund master contains 40 schemes, not the requested 1,908; dashboard must not imply full-universe coverage.
- Transaction data contains state, transaction type, date, amount, investor ID and scheme code, but no age group, city or city tier.
- Category inflow file covers Apr 2024–Mar 2025, enough for FY25 category views only.
- The fund performance file contains 40 rows and date is null in the 22-column version; check whether this field is required by the model.
- No existing PBIX was included in the uploaded archive, so there was no native report to inspect or preserve.

## Validation performed
- Read all 15 CSV files in the supplied archive.
- Checked row counts, duplicate rows, date ranges and invalid dates.
- Generated four visual pages from supplied data and combined them into `Dashboard.pdf`.
- This package has not been opened in Power BI Desktop; native visual interactions, DAX execution and PBIX export remain untested.
