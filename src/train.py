"""Train baseline severity classifier: TF-IDF + logistic regression."""

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

SRC = "data/labeled_complaints.csv"
OUT = "models/baseline.joblib"


def main() -> None:
    df = pd.read_csv(SRC)
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"],
        df["severity"],
        test_size=0.2,
        random_state=42,
        stratify=df["severity"],
    )
    print(f"train: {len(X_train)}, test: {len(X_test)}")

    vec = TfidfVectorizer()
    X_train_mat = vec.fit_transform(X_train)
    print(f"vocabulary size: {len(vec.get_feature_names_out())}")

    model = LogisticRegression(max_iter=1000, class_weight="balanced")
    model.fit(X_train_mat, y_train)

    joblib.dump(
        {"vectorizer": vec, "model": model, "X_test": X_test, "y_test": y_test},
        OUT,
    )
    print(f"saved{OUT}")


if __name__ == "__main__":
    main()
