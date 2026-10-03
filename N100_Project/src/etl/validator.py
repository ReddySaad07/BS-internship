from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class ValidationFailure:
    company_id: str | None
    field: str
    issue: str
    severity: str


def validate_dataframe(
    df: pd.DataFrame,
    required_columns: list[str],
    dataset_name: str,
) -> list[ValidationFailure]:
    """Run basic structural and data-quality checks."""
    failures: list[ValidationFailure] = []

    for column in required_columns:
        if column not in df.columns:
            failures.append(
                ValidationFailure(
                    company_id=None,
                    field=column,
                    issue=f"Missing required column in {dataset_name}",
                    severity="ERROR",
                )
            )

    if "company_id" in df.columns:
        missing_company = df["company_id"].isna()

        for index in df.index[missing_company]:
            failures.append(
                ValidationFailure(
                    company_id=None,
                    field="company_id",
                    issue=f"Missing company_id at row {index}",
                    severity="ERROR",
                )
            )

    if "year" in df.columns:
        missing_year = df["year"].isna()

        for index in df.index[missing_year]:
            company = (
                df.loc[index, "company_id"]
                if "company_id" in df.columns
                else None
            )

            failures.append(
                ValidationFailure(
                    company_id=company,
                    field="year",
                    issue=f"Missing/unparseable year at row {index}",
                    severity="WARNING",
                )
            )

    return failures


def failures_to_dataframe(
    failures: list[ValidationFailure],
) -> pd.DataFrame:
    """Convert validation failures to the required output structure."""
    return pd.DataFrame(
        [
            {
                "company_id": item.company_id,
                "field": item.field,
                "issue": item.issue,
                "severity": item.severity,
            }
            for item in failures
        ],
        columns=["company_id", "field", "issue", "severity"],
    )