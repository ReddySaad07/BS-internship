from pathlib import Path
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "db" / "nifty100.db"
OUTPUT_DIR = ROOT / "output"
TEARSHEET_DIR = ROOT / "reports" / "tearsheets"


def load_data():
    with sqlite3.connect(DB_PATH) as conn:
        companies = pd.read_sql_query(
            "SELECT * FROM companies",
            conn,
        )

        ratios = pd.read_sql_query(
            "SELECT * FROM financial_ratios",
            conn,
        )

    return companies, ratios


def company_name(row):
    for column in [
        "company_name",
        "name",
        "company",
    ]:
        if column in row.index:
            return str(row[column])

    return str(row.get("company_id", "Company"))


def create_tearsheet(row, styles):
    company_id = str(row["company_id"])

    path = (
        TEARSHEET_DIR
        / f"{company_id}_tearsheet.pdf"
    )

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    elements = []

    elements.append(
        Paragraph(
            f"N100 Financial Tearsheet — "
            f"{company_name(row)}",
            styles["Title"],
        )
    )

    elements.append(
        Spacer(1, 12)
    )

    elements.append(
        Paragraph(
            f"Company ID: {company_id}",
            styles["Normal"],
        )
    )

    elements.append(
        Paragraph(
            f"Latest financial year: "
            f"{row.get('year', '')}",
            styles["Normal"],
        )
    )

    elements.append(
        Spacer(1, 15)
    )

    metrics = [
        ("Revenue", row.get("revenue", "")),
        ("Net Profit", row.get("net_profit", "")),
        ("Net Profit Margin", row.get("net_profit_margin", "")),
        ("Operating Margin", row.get("operating_profit_margin", "")),
        ("ROE", row.get("roe", "")),
        ("ROCE", row.get("roce", "")),
        ("ROA", row.get("roa", "")),
        ("Debt / Equity", row.get("debt_to_equity", "")),
        ("Interest Coverage", row.get("interest_coverage", "")),
        ("Net Debt", row.get("net_debt", "")),
        ("Revenue CAGR 5Y", row.get("revenue_cagr_5y", "")),
        ("FCF CAGR 5Y", row.get("fcf_cagr_5y", "")),
        ("FCF", row.get("fcf", "")),
        ("FCF Conversion", row.get("fcf_conversion_pct", "")),
        ("CFO Quality", row.get("cfo_quality", "")),
    ]

    table_data = [
        ["Metric", "Value"]
    ]

    for metric, value in metrics:
        table_data.append([
            metric,
            str(value),
        ])

    table = Table(
        table_data,
        colWidths=[220, 260],
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0),
             colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5,
             colors.grey),
            ("FONTNAME", (0, 0), (-1, 0),
             "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1),
             "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ])
    )

    elements.append(table)

    elements.append(
        Spacer(1, 20)
    )

    elements.append(
        Paragraph(
            "This tearsheet is generated directly "
            "from the project's loaded source data. "
            "No missing values are interpreted as "
            "investment conclusions.",
            styles["Normal"],
        )
    )

    doc.build(elements)


def generate_reports():
    TEARSHEET_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    companies, ratios = load_data()

    if ratios.empty:
        raise RuntimeError(
            "No financial ratio data available."
        )

    latest = (
        ratios.sort_values(
            ["company_id", "year"]
        )
        .drop_duplicates(
            "company_id",
            keep="last",
        )
    )

    if not companies.empty:
        companies.columns = [
            str(c).strip().lower()
            for c in companies.columns
        ]

        if "company_id" in companies.columns:
            companies["company_id"] = (
                companies["company_id"]
                .astype(str)
                .str.strip()
                .str.upper()
            )

            latest = latest.merge(
                companies,
                on="company_id",
                how="left",
                suffixes=("", "_company"),
            )

    styles = getSampleStyleSheet()

    count = 0

    for _, row in latest.iterrows():
        create_tearsheet(
            row,
            styles,
        )
        count += 1

    print(
        f"Generated {count} company tearsheets."
    )


if __name__ == "__main__":
    generate_reports()
