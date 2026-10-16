"""Play: how TF-IDF turns sentences into numbers."""

from sklearn.feature_extraction.text import TfidfVectorizer

sentences = [
    "someone stole money from my card",
    "late fee charged on my card",
    "cannot close my card account",
]

vec = TfidfVectorizer()
matrix = vec.fit_transform(sentences)

words = vec.get_feature_names_out()
print("vocabulary:", list(words))
print()
for i, s in enumerate(sentences):
    print(f"sentence {i}: {s}")
    row = matrix[i].toarray()[0]
    pairs = sorted(zip(words, row), key=lambda p: -p[1])
    for w, score in pairs:
        if score > 0:
            print(f"   {w}: {score:.2f}")
    print()
