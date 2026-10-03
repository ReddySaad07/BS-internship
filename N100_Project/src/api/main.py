from pathlib import Path
import sqlite3

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "db" / "nifty100.db"


app = FastAPI(
    title="N100 Financial Intelligence API",
    version="1.0.0",
    description="API for the N100 Financial Intelligence Platform.",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def query(sql, params=()):
    if not DB_PATH.exists():
        return []

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute(
            sql,
            params,
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]


@app.get("/")
def root():
    return {
        "name": "N100 Financial Intelligence API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database_exists": DB_PATH.exists(),
    }


@app.get("/companies")
def companies():
    return query(
        "SELECT * FROM companies"
    )


@app.get("/companies/{company_id}")
def company(company_id: str):
    return query(
        """
        SELECT *
        FROM companies
        WHERE UPPER(company_id)=UPPER(?)
        """,
        (company_id,),
    )


@app.get("/screener")
def screener(
    min_score: float = 0,
):
    return query(
        """
        SELECT *
        FROM financial_ratios
        WHERE 1=1
        """,
    )


@app.get("/sectors")
def sectors():
    return query(
        "SELECT * FROM sectors"
    )


@app.get("/peers")
def peers():
    return query(
        "SELECT * FROM peer_groups"
    )


@app.get("/valuation")
def valuation():
    path = ROOT / "output" / "valuation_flags.csv"

    if not path.exists():
        return []

    import pandas as pd

    return pd.read_csv(path).fillna(
        ""
    ).to_dict(orient="records")


@app.get("/portfolio")
def portfolio():
    path = ROOT / "output" / "portfolio_stats.csv"

    if not path.exists():
        return []

    import pandas as pd

    return pd.read_csv(path).fillna(
        ""
    ).to_dict(orient="records")


@app.get("/documents")
def documents():
    return query(
        "SELECT * FROM documents"
    )


@app.get("/ratios/{company_id}")
def ratios(company_id: str):
    return query(
        """
        SELECT *
        FROM financial_ratios
        WHERE UPPER(company_id)=UPPER(?)
        ORDER BY year
        """,
        (company_id,),
    )


@app.get("/cashflow/{company_id}")
def cashflow(company_id: str):
    return query(
        """
        SELECT
            company_id,
            year,
            cfo,
            capex,
            fcf,
            fcf_conversion_pct,
            cfo_quality
        FROM financial_ratios
        WHERE UPPER(company_id)=UPPER(?)
        ORDER BY year
        """,
        (company_id,),
    )


@app.get("/health/database")
def database_health():
    if not DB_PATH.exists():
        return {
            "database": "missing"
        }

    tables = query(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name
        """
    )

    return {
        "database": "available",
        "tables": tables,
    }


@app.get("/peer-percentiles/{company_id}")
def peer_percentiles(company_id: str):
    return query(
        """
        SELECT *
        FROM peer_percentiles
        WHERE UPPER(company_id)=UPPER(?)
        """,
        (company_id,),
    )


@app.get("/cluster/{company_id}")
def cluster(company_id: str):
    import pandas as pd

    path = (
        ROOT
        / "output"
        / "cluster_labels.csv"
    )

    if not path.exists():
        return []

    df = pd.read_csv(path)

    return df.loc[
        df["company_id"].astype(str).str.upper()
        == company_id.upper()
    ].fillna("").to_dict(
        orient="records"
    )


@app.get("/pros-cons/{company_id}")
def pros_cons(company_id: str):
    import pandas as pd

    path = (
        ROOT
        / "output"
        / "pros_cons.csv"
    )

    if not path.exists():
        return []

    df = pd.read_csv(path)

    return df.loc[
        df["company_id"].astype(str).str.upper()
        == company_id.upper()
    ].fillna("").to_dict(
        orient="records"
    )


@app.get("/financial-summary/{company_id}")
def financial_summary(company_id: str):
    return query(
        """
        SELECT
            company_id,
            year,
            net_profit_margin,
            operating_profit_margin,
            roe,
            roce,
            roa,
            debt_to_equity,
            interest_coverage,
            net_debt,
            revenue_cagr_5y,
            fcf_cagr_5y,
            fcf,
            fcf_conversion_pct,
            cfo_quality
        FROM financial_ratios
        WHERE UPPER(company_id)=UPPER(?)
        ORDER BY year DESC
        """,
        (company_id,),
    )


@app.get("/api-info")
def api_info():
    return {
        "endpoints": [
            "/",
            "/health",
            "/companies",
            "/companies/{company_id}",
            "/screener",
            "/sectors",
            "/peers",
            "/valuation",
            "/portfolio",
            "/documents",
            "/ratios/{company_id}",
            "/cashflow/{company_id}",
            "/health/database",
            "/peer-percentiles/{company_id}",
            "/cluster/{company_id}",
            "/pros-cons/{company_id}",
            "/financial-summary/{company_id}",
        ]
    }
