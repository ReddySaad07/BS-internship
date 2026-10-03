-- ============================================================
-- BLUESTOCK MF - DAY 2 ANALYTICAL QUERIES
-- ============================================================


-- 1. Top 5 funds by scheme-level AUM
-- AUM comes from 07_scheme_performance.csv.

SELECT
    f.amfi_code,
    f.scheme_name,
    p.aum_crore
FROM fact_performance p
JOIN dim_fund f
    ON p.amfi_code = f.amfi_code
WHERE p.aum_crore IS NOT NULL
ORDER BY p.aum_crore DESC
LIMIT 5;


-- ============================================================
-- 2. Average NAV per month
-- ============================================================

SELECT
    substr(n.date_id, 1, 7) AS month,
    ROUND(AVG(n.nav), 4) AS average_nav
FROM fact_nav n
GROUP BY substr(n.date_id, 1, 7)
ORDER BY month;


-- ============================================================
-- 3. SIP year-over-year growth
-- ============================================================

WITH yearly_sip AS (

    SELECT
        d.year,
        SUM(t.amount) AS sip_amount
    FROM fact_transactions t
    JOIN dim_date d
        ON t.date_id = d.date_id
    WHERE t.transaction_type = 'SIP'
    GROUP BY d.year
),

growth AS (

    SELECT
        year,
        sip_amount,
        LAG(sip_amount)
            OVER (
                ORDER BY year
            ) AS previous_year_sip
    FROM yearly_sip
)

SELECT
    year,
    ROUND(sip_amount, 2) AS sip_amount,
    ROUND(previous_year_sip, 2)
        AS previous_year_sip,

    ROUND(
        CASE
            WHEN previous_year_sip IS NULL
                 OR previous_year_sip = 0
            THEN NULL

            ELSE
                (
                    (sip_amount - previous_year_sip)
                    / previous_year_sip
                ) * 100
        END,
        2
    ) AS yoy_growth_pct

FROM growth
ORDER BY year;


-- ============================================================
-- 4. Transactions by state
-- ============================================================

SELECT
    i.state,
    COUNT(t.transaction_id)
        AS transaction_count,
    ROUND(
        SUM(t.amount),
        2
    ) AS total_amount
FROM fact_transactions t
JOIN dim_investor i
    ON t.investor_id = i.investor_id
GROUP BY i.state
ORDER BY total_amount DESC;


-- ============================================================
-- 5. Funds with expense ratio below 1%
-- ============================================================

SELECT
    f.amfi_code,
    f.scheme_name,
    p.expense_ratio
FROM fact_performance p
JOIN dim_fund f
    ON p.amfi_code = f.amfi_code
WHERE p.expense_ratio < 1.0
ORDER BY p.expense_ratio ASC;


-- ============================================================
-- 6. Top 5 funds by transaction amount
-- ============================================================

SELECT
    f.amfi_code,
    f.scheme_name,
    COUNT(t.transaction_id)
        AS transaction_count,
    ROUND(
        SUM(t.amount),
        2
    ) AS total_transaction_amount
FROM fact_transactions t
JOIN dim_fund f
    ON t.amfi_code = f.amfi_code
GROUP BY
    f.amfi_code,
    f.scheme_name
ORDER BY total_transaction_amount DESC
LIMIT 5;


-- ============================================================
-- 7. Latest NAV for each fund
-- ============================================================

SELECT
    f.amfi_code,
    f.scheme_name,
    n.date_id,
    n.nav
FROM fact_nav n
JOIN dim_fund f
    ON n.amfi_code = f.amfi_code
WHERE n.date_id = (
    SELECT MAX(n2.date_id)
    FROM fact_nav n2
    WHERE n2.amfi_code = n.amfi_code
)
ORDER BY n.nav DESC;


-- ============================================================
-- 8. Fund performance and expense ratio
-- ============================================================

SELECT
    f.amfi_code,
    f.scheme_name,
    p.return_1y,
    p.return_3y,
    p.return_5y,
    p.expense_ratio
FROM fact_performance p
JOIN dim_fund f
    ON p.amfi_code = f.amfi_code
ORDER BY p.return_1y DESC;


-- ============================================================
-- 9. Fund-house AUM
-- ============================================================

SELECT
    fund_house,
    ROUND(
        SUM(aum_crore),
        2
    ) AS total_aum_crore,
    SUM(num_schemes)
        AS total_schemes
FROM fact_aum
GROUP BY fund_house
ORDER BY total_aum_crore DESC;


-- ============================================================
-- 10. Transaction count and amount by KYC status
-- ============================================================

SELECT
    i.kyc_status,
    COUNT(t.transaction_id)
        AS transaction_count,
    ROUND(
        SUM(t.amount),
        2
    ) AS total_amount
FROM fact_transactions t
JOIN dim_investor i
    ON t.investor_id = i.investor_id
GROUP BY i.kyc_status
ORDER BY total_amount DESC;
