import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "db" / "nifty100.db"


st.set_page_config(
    page_title="N100 Financial Intelligence",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def load_table(table):
    if not DB_PATH.exists():
        return pd.DataFrame()

    with sqlite3.connect(DB_PATH) as conn:
        try:
            return pd.read_sql_query(
                f"SELECT * FROM {table}",
                conn,
            )
        except Exception:
            return pd.DataFrame()


st.title("N100 Financial Intelligence Platform")

st.markdown(
    """
    ### Financial analysis dashboard

    This dashboard displays values calculated from the
    project's loaded source datasets. It does not invent
    missing financial information.
    """
)

ratios = load_table(
    "financial_ratios"
)

companies = load_table(
    "companies"
)

if ratios.empty:
    st.warning(
        "No financial ratio data is available yet. "
        "Run the ETL and analytics pipeline first."
    )
    st.stop()

latest = (
    ratios.sort_values(
        ["company_id", "year"]
    )
    .drop_duplicates(
        "company_id",
        keep="last",
    )
)

st.sidebar.header("Filters")

company_ids = sorted(
    latest["company_id"]
    .dropna()
    .astype(str)
    .unique()
)

selected = st.sidebar.selectbox(
    "Company",
    ["All"] + company_ids,
)

if selected != "All":
    view = latest[
        latest["company_id"].astype(str)
        == selected
    ]
else:
    view = latest


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Companies",
    len(view),
)

col2.metric(
    "Average ROE",
    f"{pd.to_numeric(view.get('roe'), errors='coerce').mean():.2f}",
)

col3.metric(
    "Average Debt / Equity",
    f"{pd.to_numeric(view.get('debt_to_equity'), errors='coerce').mean():.2f}",
)

col4.metric(
    "Average Revenue CAGR",
    f"{pd.to_numeric(view.get('revenue_cagr_5y'), errors='coerce').mean():.2f}%",
)

st.subheader("Financial Metrics")

display_columns = [
    "company_id",
    "year",
    "net_profit_margin",
    "operating_profit_margin",
    "roe",
    "roce",
    "roa",
    "debt_to_equity",
    "interest_coverage",
    "revenue_cagr_5y",
    "fcf_cagr_5y",
    "fcf_conversion_pct",
]

display_columns = [
    c for c in display_columns
    if c in view.columns
]

st.dataframe(
    view[display_columns],
    use_container_width=True,
)

st.subheader("Company Profile")

if selected != "All":

    row = view.iloc[0]

    left, right = st.columns(2)

    with left:
        st.write(
            "**Company ID:**",
            row["company_id"],
        )
        st.write(
            "**Year:**",
            row["year"],
        )
        st.write(
            "**ROE:**",
            row.get("roe"),
        )
        st.write(
            "**ROCE:**",
            row.get("roce"),
        )

    with right:
        st.write(
            "**Debt / Equity:**",
            row.get("debt_to_equity"),
        )
        st.write(
            "**Revenue CAGR 5Y:**",
            row.get("revenue_cagr_5y"),
        )
        st.write(
            "**FCF:**",
            row.get("fcf"),
        )
        st.write(
            "**CFO Quality:**",
            row.get("cfo_quality"),
        )
