"""Evaluate the baseline severity classifier on the held-out test set."""

import joblib
from sklearn.metrics import classification_report, confusion_matrix

SRC = "models/baseline.joblib"


def main() -> None:
    bundle = joblib.load(SRC)
    vec = bundle["vectorizer"]
    model = bundle["model"]
    X_test = bundle["X_test"]
    y_test = bundle["y_test"]

    preds = model.predict(vec.transform(X_test))

    print(classification_report(y_test, preds, digits=2))
    labels = ["high", "medium", "low"]
    print("confusion matrix (rows = true, cols = predicted):")
    print(labels)
    print(confusion_matrix(y_test, preds, labels=labels))


if __name__ == "__main__":
    main()
