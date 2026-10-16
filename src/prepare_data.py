"""Derive severity labels from CFPB issue categories (weak supervision)."""

import pandas as pd

SRC = "data/credit_card_narratives.csv"
OUT = "data/labeled_complaints.csv"

FRAUD_SUB_ISSUE = "Card was charged for something you did not purchase with the card"

HIGH_ISSUES = {
    "Problem with fraud alerts or security freezes",
    "Improper use of your report",
    "Credit monitoring or identity theft protection services",
}
MEDIUM_ISSUES = {
    "Problem with a purchase shown on your statement",
    "Fees or interest",
    "Problem when making payments",
    "Incorrect information on your report",
    "Problem with a company's investigation into an existing problem",
    "Struggling to pay your bill",
}
LOW_ISSUES = {
    "Other features, terms, or problems",
    "Getting a credit card",
    "Closing your account",
    "Advertising and marketing, including promotional offers",
    "Trouble using your card",
    "Unable to get your credit report or credit score",
}


def label_row(row) -> str:
    if row["Sub-issue"] == FRAUD_SUB_ISSUE:
        return "high"
    if row["Issue"] in HIGH_ISSUES:
        return "high"
    if row["Issue"] in MEDIUM_ISSUES:
        return "medium"
    if row["Issue"] in LOW_ISSUES:
        return "low"
    return "UNMAPPED"


def main() -> None:
    df = pd.read_csv(SRC)
    df["severity"] = df.apply(label_row, axis=1)
    print(df["severity"].value_counts())
    out = df[["Complaint ID", "Consumer complaint narrative", "severity"]].rename(
        columns={"Complaint ID": "complaint_id",
                 "Consumer complaint narrative": "text"}
    )
    out.to_csv(OUT, index=False)
    print(f"saved {len(out)} rows to {OUT}")


if __name__ == "__main__":
    main()
