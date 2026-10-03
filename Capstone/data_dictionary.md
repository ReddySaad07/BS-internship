# Bluestock MF — Day 2 Data Dictionary

## Project

Bluestock Mutual Fund analytics pipeline.

The Day-2 pipeline cleans selected source datasets, creates a SQLite
star schema, loads cleaned data, and provides analytical SQL queries.

---

# Source Datasets

## 01_fund_master.csv

Master information about mutual fund schemes.

| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| amfi_code | TEXT | AMFI identifier for the scheme | 01_fund_master.csv |
| scheme_name | TEXT | Name of the mutual fund scheme | 01_fund_master.csv |
| fund_house | TEXT | Asset management company/fund house | 01_fund_master.csv |
| category / scheme_category | TEXT | Broad scheme category | 01_fund_master.csv |
| sub_category / scheme_type | TEXT | Scheme sub-category/type | 01_fund_master.csv |
| risk_category / risk_grade | TEXT | Risk classification where supplied | 01_fund_master.csv |

---

## 02_nav_history.csv

Historical NAV observations.

| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| amfi_code | TEXT | AMFI scheme identifier | 02_nav_history.csv |
| date | DATE | NAV observation date | 02_nav_history.csv |
| nav | REAL | Net asset value of the scheme | 02_nav_history.csv |

Day-2 transformations:

- Dates parsed to datetime.
- Records sorted by AMFI code and date.
- Duplicate AMFI/date observations removed.
- NAV validated as greater than zero.
- Missing NAV values are forward-filled within the same AMFI code where a previous valid NAV exists.

---

## 03_aum_by_fund_house.csv

Fund-house-level AUM data.

| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| date | DATE | Reporting date | 03_aum_by_fund_house.csv |
| fund_house | TEXT | Mutual fund house/AMC | 03_aum_by_fund_house.csv |
| aum_lakh_crore | REAL | AUM expressed in lakh crore units | 03_aum_by_fund_house.csv |
| aum_crore | REAL | AUM expressed in crore units | 03_aum_by_fund_house.csv |
| num_schemes | INTEGER/REAL | Number of schemes reported for the fund house | 03_aum_by_fund_house.csv |

This dataset is treated as fund-house-level AUM.
It is not treated as scheme-level AUM.

---

## 04_monthly_sip_inflows.csv

Monthly SIP inflow data.

No Day-2 transformation rule was specified, so the dataset is copied
to data/processed without modification.

---

## 05_category_inflows.csv

Category-level inflow data.

No Day-2 transformation rule was specified, so the dataset is copied
to data/processed without modification.

---

## 06_industry_folio_count.csv

Industry folio-count data.

No Day-2 transformation rule was specified, so the dataset is copied
to data/processed without modification.

---

## 07_scheme_performance.csv

Scheme-level performance information.

| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| amfi_code | TEXT | AMFI scheme identifier | 07_scheme_performance.csv |
| return_1y | REAL | One-year scheme return | 07_scheme_performance.csv |
| return_3y | REAL | Three-year scheme return | 07_scheme_performance.csv |
| return_5y | REAL | Five-year scheme return | 07_scheme_performance.csv |
| expense_ratio | REAL | Scheme expense ratio | 07_scheme_performance.csv |
| aum_crore | REAL | Scheme-level AUM in crore, where supplied | 07_scheme_performance.csv |

Day-2 transformations:

- Return fields converted to numeric values.
- Invalid/non-numeric return values are flagged.
- Expense ratio converted to numeric.
- Expense ratio is checked against the specified 0.1%–2.5% range.
- Anomaly status and anomaly reasons are retained in the cleaned output.
- A separate anomaly CSV is also produced.

No additional return anomaly threshold is invented because the Day-2
description only requires numeric validation and anomaly flagging.

---

## 08_investor_transactions.csv

Investor transaction records.

| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| transaction_id | TEXT | Unique transaction identifier | 08_investor_transactions.csv |
| investor_id | TEXT | Investor identifier | 08_investor_transactions.csv |
| amfi_code | TEXT | AMFI scheme identifier | 08_investor_transactions.csv |
| date | DATE | Transaction date | 08_investor_transactions.csv |
| transaction_type | TEXT | SIP, Lumpsum, or Redemption | 08_investor_transactions.csv |
| amount | REAL | Transaction amount | 08_investor_transactions.csv |
| kyc_status | TEXT | Investor KYC status | 08_investor_transactions.csv |
| state | TEXT | Investor state where supplied | 08_investor_transactions.csv |

Day-2 transformations:

- Transaction types standardised to SIP, Lumpsum, and Redemption.
- Amount validated as greater than zero.
- Dates parsed to datetime.
- KYC status checked against the supported enum values.
- Duplicate transaction IDs removed.

---

## 09_portfolio_holdings.csv

Portfolio holding information.

No Day-2 transformation rule was specified, so the dataset is copied
to data/processed without modification.

---

## 10_benchmark_indices.csv

Benchmark index information.

No Day-2 transformation rule was specified, so the dataset is copied
to data/processed without modification.

---

# SQLite Star Schema

## dim_fund

| Column | Type | Definition |
|---|---|---|
| amfi_code | TEXT PK | Unique AMFI scheme identifier |
| scheme_name | TEXT | Scheme name |
| fund_house | TEXT | Fund house |
| scheme_category | TEXT | Scheme category |
| scheme_type | TEXT | Scheme type/sub-category |
| risk_grade | TEXT | Risk classification |
| is_active | INTEGER | Active flag |

---

## dim_date

| Column | Type | Definition |
|---|---|---|
| date_id | TEXT PK | Date in YYYY-MM-DD format |
| year | INTEGER | Calendar year |
| quarter | INTEGER | Calendar quarter |
| month | INTEGER | Calendar month |
| month_name | TEXT | Month name |
| day | INTEGER | Day of month |
| day_of_week | TEXT | Day name |
| is_weekend | INTEGER | Weekend flag |
| is_holiday | INTEGER | Holiday flag; no holiday calendar supplied |

---

## dim_investor

| Column | Type | Definition |
|---|---|---|
| investor_id | TEXT PK | Unique investor identifier |
| state | TEXT | Investor state |
| kyc_status | TEXT | KYC status |

---

## fact_nav

| Column | Type | Definition |
|---|---|---|
| nav_id | INTEGER PK | Surrogate NAV record ID |
| amfi_code | TEXT FK | Fund identifier |
| date_id | TEXT FK | Observation date |
| nav | REAL | NAV value; must be greater than zero |

---

## fact_transactions

| Column | Type | Definition |
|---|---|---|
| transaction_id | TEXT PK | Transaction identifier |
| investor_id | TEXT FK | Investor identifier |
| amfi_code | TEXT FK | Fund identifier |
| date_id | TEXT FK | Transaction date |
| transaction_type | TEXT | SIP, Lumpsum, or Redemption |
| amount | REAL | Transaction amount |

---

## fact_performance

| Column | Type | Definition |
|---|---|---|
| performance_id | INTEGER PK | Surrogate performance record ID |
| amfi_code | TEXT FK | Fund identifier |
| date_id | TEXT FK | Performance date where supplied |
| return_1y | REAL | One-year return |
| return_3y | REAL | Three-year return |
| return_5y | REAL | Five-year return |
| expense_ratio | REAL | Expense ratio |
| aum_crore | REAL | Scheme-level AUM |
| is_anomaly | INTEGER | Anomaly flag |

---

## fact_aum

| Column | Type | Definition |
|---|---|---|
| aum_id | INTEGER PK | Surrogate AUM record ID |
| amfi_code | TEXT FK/NULL | Scheme identifier when applicable |
| fund_house | TEXT | Fund-house identifier/name |
| date_id | TEXT FK | AUM reporting date |
| aum_crore | REAL | AUM in crore |
| aum_lakh_crore | REAL | AUM in lakh crore |
| num_schemes | INTEGER/REAL | Number of schemes |

The current 03_aum_by_fund_house.csv dataset is fund-house-level,
so amfi_code is intentionally NULL for those records.

---

# Deliverables

The pipeline creates:

- data/processed/01_fund_master.csv
- data/processed/02_nav_history_clean.csv
- data/processed/03_aum_by_fund_house.csv
- data/processed/04_monthly_sip_inflows.csv
- data/processed/05_category_inflows.csv
- data/processed/06_industry_folio_count.csv
- data/processed/07_scheme_performance_clean.csv
- data/processed/08_investor_transactions_clean.csv
- data/processed/09_portfolio_holdings.csv
- data/processed/10_benchmark_indices.csv
- data/processed/02_nav_history_rejects.csv where required
- data/processed/08_investor_transactions_rejects.csv where required
- data/processed/07_scheme_performance_anomalies.csv where required
- bluestock_mf.db
- schema.sql
- queries.sql
- data_dictionary.md
