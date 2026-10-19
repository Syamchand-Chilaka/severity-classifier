"""Play: does the model hold up on April 2026 data it never saw? (drift check)"""

import joblib
import pandas as pd
from sklearn.metrics import classification_report

from prepare_data import label_row

SOURCE = "data/ccdb_april2026.zip"

pieces = []
for chunk in pd.read_csv(SOURCE, chunksize=100_000, dtype=str):
    mask = (
        chunk["Product"].str.contains("Credit card", na=False)
        & chunk["Consumer complaint narrative"].notna()
    )
    pieces.append(chunk.loc[mask])

df = pd.concat(pieces)
print(f"april credit-card narratives: {len(df)}")

df["severity"] = df.apply(label_row, axis=1)
unmapped = (df["severity"] == "UNMAPPED").sum()
print(f"unmapped rows: {unmapped}")
df = df[df["severity"] != "UNMAPPED"]
print(df["severity"].value_counts())

bundle = joblib.load("models/baseline.joblib")
vec, model = bundle["vectorizer"], bundle["model"]
preds = model.predict(vec.transform(df["Consumer complaint narrative"]))
print(classification_report(df["severity"], preds, digits=2))
