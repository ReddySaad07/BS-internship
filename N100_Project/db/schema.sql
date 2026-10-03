PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS peer_percentiles;
DROP TABLE IF EXISTS financial_ratios;
DROP TABLE IF EXISTS market_cap;
DROP TABLE IF EXISTS stock_prices;
DROP TABLE IF EXISTS peer_groups;
DROP TABLE IF EXISTS sectors;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS analysis;
DROP TABLE IF EXISTS pros_cons;
DROP TABLE IF EXISTS cash_flow;
DROP TABLE IF EXISTS balance_sheet;
DROP TABLE IF EXISTS profit_loss;
DROP TABLE IF EXISTS companies;

CREATE TABLE companies (
    id TEXT PRIMARY KEY,
    company_logo TEXT,
    company_name TEXT,
    chart_link TEXT,
    about_company TEXT,
    website TEXT,
    nse_profile TEXT,
    bse_profile TEXT,
    face_value REAL,
    book_value REAL,
    roce_percentage REAL,
    roe_percentage REAL
);

CREATE TABLE profit_loss (
    id TEXT,
    company_id TEXT NOT NULL,
    year INTEGER,
    sales REAL,
    expenses REAL,
    operating_profit REAL,
    opm_percentage REAL,
    other_income REAL,
    interest REAL,
    depreciation REAL,
    profit_before_tax REAL,
    tax_percentage REAL,
    net_profit REAL,
    eps REAL,
    dividend_payout REAL
);

CREATE TABLE balance_sheet (
    id TEXT,
    company_id TEXT NOT NULL,
    year INTEGER,
    equity_capital REAL,
    reserves REAL,
    borrowings REAL,
    other_liabilities REAL,
    total_liabilities REAL,
    fixed_assets REAL,
    cwip REAL,
    investments REAL,
    other_asset REAL,
    total_assets REAL
);

CREATE TABLE cash_flow (
    id TEXT,
    company_id TEXT NOT NULL,
    year INTEGER,
    operating_activity REAL,
    investing_activity REAL,
    financing_activity REAL,
    net_cash_flow REAL
);

CREATE TABLE documents (
    id TEXT,
    company_id TEXT NOT NULL,
    year INTEGER,
    annual_report TEXT
);

CREATE TABLE pros_cons (
    id TEXT,
    company_id TEXT NOT NULL,
    pros TEXT,
    cons TEXT
);

CREATE TABLE analysis (
    id TEXT,
    company_id TEXT NOT NULL,
    compounded_sales_growth REAL,
    compounded_profit_growth REAL,
    stock_price_cagr REAL,
    roe REAL
);

CREATE TABLE financial_ratios (
    id TEXT,
    company_id TEXT NOT NULL,
    year INTEGER,
    net_profit_margin_pct REAL,
    operating_profit_margin_pct REAL,
    return_on_equity_pct REAL,
    debt_to_equity REAL,
    interest_coverage REAL,
    asset_turnover REAL,
    free_cash_flow_cr REAL,
    capex_cr REAL,
    earnings_per_share REAL,
    book_value_per_share REAL,
    dividend_payout_ratio_pct REAL,
    total_debt_cr REAL,
    cash_from_operations_cr REAL
);

CREATE TABLE market_cap (
    id TEXT,
    company_id TEXT NOT NULL,
    year INTEGER,
    market_cap_crore REAL,
    enterprise_value_crore REAL,
    pe_ratio REAL,
    pb_ratio REAL,
    ev_ebitda REAL,
    dividend_yield_pct REAL
);

CREATE TABLE peer_groups (
    id TEXT,
    peer_group_name TEXT,
    company_id TEXT NOT NULL,
    is_benchmark TEXT
);

CREATE TABLE sectors (
    id TEXT,
    company_id TEXT NOT NULL,
    broad_sector TEXT,
    sub_sector TEXT,
    index_weight_pct REAL,
    market_cap_category TEXT
);

CREATE TABLE stock_prices (
    id TEXT,
    company_id TEXT NOT NULL,
    date TEXT,
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    volume REAL,
    adjusted_close REAL
);

CREATE TABLE peer_percentiles (
    peer_group_name TEXT,
    company_id TEXT,
    metric TEXT,
    percentile REAL
);

CREATE INDEX idx_profit_loss_company_year
    ON profit_loss(company_id, year);

CREATE INDEX idx_balance_sheet_company_year
    ON balance_sheet(company_id, year);

CREATE INDEX idx_cash_flow_company_year
    ON cash_flow(company_id, year);

CREATE INDEX idx_financial_ratios_company_year
    ON financial_ratios(company_id, year);

CREATE INDEX idx_market_cap_company_year
    ON market_cap(company_id, year);

CREATE INDEX idx_stock_prices_company_date
    ON stock_prices(company_id, date);

CREATE INDEX idx_peer_groups_company
    ON peer_groups(company_id);

CREATE INDEX idx_sectors_company
    ON sectors(company_id);

CREATE INDEX idx_documents_company_year
    ON documents(company_id, year);

CREATE INDEX idx_peer_percentiles_company
    ON peer_percentiles(company_id);