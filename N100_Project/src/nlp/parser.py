from pathlib import Path
import re
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
OUTPUT_DIR = ROOT / "output"


POSITIVE_WORDS = {
    "growth",
    "strong",
    "improved",
    "profit",
    "profitable",
    "cash",
    "healthy",
    "increase",
    "increased",
    "stable",
    "leadership",
    "expansion",
}

NEGATIVE_WORDS = {
    "decline",
    "declined",
    "loss",
    "losses",
    "debt",
    "weak",
    "risk",
    "fall",
    "fallen",
    "decrease",
    "decreased",
    "negative",
    "pressure",
}


def extract_sentences(text):
    if pd.isna(text):
        return []

    text = str(text)

    return [
        s.strip()
        for s in re.split(
            r"(?<=[.!?])\s+",
            text,
        )
        if s.strip()
    ]


def sentence_score(sentence):
    words = set(
        re.findall(
            r"[a-zA-Z]+",
            sentence.lower(),
        )
    )

    positive = len(
        words & POSITIVE_WORDS
    )

    negative = len(
        words & NEGATIVE_WORDS
    )

    return positive - negative


def extract_pros_cons(text):
    sentences = extract_sentences(text)

    scored = [
        (sentence_score(s), s)
        for s in sentences
    ]

    pros = [
        s for score, s in scored
        if score > 0
    ]

    cons = [
        s for score, s in scored
        if score < 0
    ]

    if not pros:
        pros = ["No explicit positive statement identified."]

    if not cons:
        cons = ["No explicit negative statement identified."]

    return pros[:5], cons[:5]


def process_pros_cons():
    source = RAW_DIR / "prosandcons.xlsx"

    if not source.exists():
        print(
            "prosandcons.xlsx not found; NLP step skipped."
        )
        return

    sheets = pd.read_excel(
        source,
        sheet_name=None,
        header=1,
    )

    records = []

    for sheet_name, df in sheets.items():

        df.columns = [
            str(c).strip().lower()
            for c in df.columns
        ]

        company_column = next(
            (
                c for c in df.columns
                if "company" in c
            ),
            None,
        )

        text_columns = [
            c for c in df.columns
            if c != company_column
            and (
                df[c].dtype == "object"
                or "text" in c
                or "description" in c
            )
        ]

        for _, row in df.iterrows():

            company_id = (
                str(row[company_column]).strip().upper()
                if company_column
                and pd.notna(row[company_column])
                else str(sheet_name).strip().upper()
            )

            text_parts = []

            for column in text_columns:
                if pd.notna(row[column]):
                    text_parts.append(
                        str(row[column])
                    )

            text = " ".join(text_parts)

            pros, cons = extract_pros_cons(
                text
            )

            records.append({
                "company_id": company_id,
                "pros": " | ".join(pros),
                "cons": " | ".join(cons),
            })

    result = pd.DataFrame(records)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_DIR / "pros_cons.csv",
        index=False,
    )

    print(
        f"NLP pros/cons created: "
        f"{len(result)} companies"
    )


if __name__ == "__main__":
    process_pros_cons()
