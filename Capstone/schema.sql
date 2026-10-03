PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code       TEXT PRIMARY KEY,
    scheme_name     TEXT NOT NULL,
    fund_house      TEXT,
    scheme_category TEXT,
    scheme_type     TEXT,
    risk_grade      TEXT,
    is_active       INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id      TEXT PRIMARY KEY,
    year         INTEGER NOT NULL,
    quarter      INTEGER NOT NULL,
    month        INTEGER NOT NULL,
    month_name   TEXT NOT NULL,
    day          INTEGER NOT NULL,
    day_of_week  TEXT NOT NULL,
    is_weekend   INTEGER NOT NULL,
    is_holiday   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS dim_investor (
    investor_id TEXT PRIMARY KEY,
    state       TEXT,
    kyc_status  TEXT
);

CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code   TEXT NOT NULL,
    date_id     TEXT NOT NULL,
    nav         REAL NOT NULL CHECK (nav > 0),

    FOREIGN KEY (amfi_code)
        REFERENCES dim_fund(amfi_code),

    FOREIGN KEY (date_id)
        REFERENCES dim_date(date_id),

    UNIQUE(amfi_code, date_id)
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id   TEXT PRIMARY KEY,
    investor_id      TEXT NOT NULL,
    amfi_code        TEXT NOT NULL,
    date_id          TEXT NOT NULL,

    transaction_type TEXT NOT NULL
        CHECK (
            transaction_type
            IN ('SIP', 'Lumpsum', 'Redemption')
        ),

    amount REAL NOT NULL CHECK (amount > 0),

    FOREIGN KEY (investor_id)
        REFERENCES dim_investor(investor_id),

    FOREIGN KEY (amfi_code)
        REFERENCES dim_fund(amfi_code),

    FOREIGN KEY (date_id)
        REFERENCES dim_date(date_id)
);

CREATE TABLE IF NOT EXISTS fact_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,

    amfi_code      TEXT NOT NULL,
    date_id        TEXT,

    return_1y      REAL,
    return_3y      REAL,
    return_5y      REAL,

    expense_ratio REAL
        CHECK (
            expense_ratio
            BETWEEN 0.1 AND 2.5
        ),

    aum_crore REAL,

    is_anomaly INTEGER DEFAULT 0,

    FOREIGN KEY (amfi_code)
        REFERENCES dim_fund(amfi_code),

    FOREIGN KEY (date_id)
        REFERENCES dim_date(date_id),

    UNIQUE(amfi_code, date_id)
);

CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id      INTEGER PRIMARY KEY AUTOINCREMENT,

    amfi_code   TEXT,
    fund_house  TEXT NOT NULL,
    date_id     TEXT NOT NULL,

    aum_crore   REAL,
    aum_lakh_crore REAL,
    num_schemes INTEGER,

    FOREIGN KEY (amfi_code)
        REFERENCES dim_fund(amfi_code),

    FOREIGN KEY (date_id)
        REFERENCES dim_date(date_id)
);

CREATE INDEX IF NOT EXISTS idx_nav_amfi_date
ON fact_nav(amfi_code, date_id);

CREATE INDEX IF NOT EXISTS idx_transaction_amfi_date
ON fact_transactions(amfi_code, date_id);

CREATE INDEX IF NOT EXISTS idx_transaction_investor
ON fact_transactions(investor_id);

CREATE INDEX IF NOT EXISTS idx_performance_amfi_date
ON fact_performance(amfi_code, date_id);

CREATE INDEX IF NOT EXISTS idx_aum_fund_house_date
ON fact_aum(fund_house, date_id);
