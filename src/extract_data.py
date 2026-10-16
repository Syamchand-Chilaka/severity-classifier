"""Extract credit card complaints with narratives from CFPB monthly archives."""

import pandas as pd

SOURCES = [
    "data/ccdb_july2026.zip",
    "data/ccdb_june2026.zip",
    "data/ccdb_may2026.zip",
]
OUT = "data/credit_card_narratives.csv"
TARGET = 5000
CHUNK_ROWS = 100_000

KEEP = [
    "Complaint ID",
    "Date received",
    "Product",
    "Issue",
    "Sub-issue",
    "Consumer complaint narrative",
]


def main() -> None:
    pieces = []
    kept = 0
    for source in SOURCES:
        scanned = 0
        for chunk in pd.read_csv(source, chunksize=CHUNK_ROWS, dtype=str):
            scanned += len(chunk)
            mask = (
                chunk["Product"].str.contains("Credit card", na=False)
                & chunk["Consumer complaint narrative"].notna()
            )
            hits = chunk.loc[mask, KEEP]
            if len(hits):
                pieces.append(hits)
                kept += len(hits)
            if kept >= TARGET:
                break
        print(f"{source}: scanned {scanned:,}, running total kept {kept:,}")
        if kept >= TARGET:
            break
    out = pd.concat(pieces).head(TARGET)
    out.to_csv(OUT, index=False)
    print(f"saved {len(out):,} rows to {OUT}")


if __name__ == "__main__":
    main()
