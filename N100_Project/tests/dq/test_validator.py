from src.etl.validator import validate_dataframe


def test_empty_dataframe():
    failures = validate_dataframe(
        __import__("pandas").DataFrame(),
        "test.xlsx",
    )

    assert any(
        f["issue"] == "Dataset is empty"
        for f in failures
    )


def test_missing_company_id():
    import pandas as pd

    failures = validate_dataframe(
        pd.DataFrame(
            {"revenue": [100]}
        ),
        "test.xlsx",
    )

    assert any(
        "company_id" in f["issue"]
        for f in failures
    )
