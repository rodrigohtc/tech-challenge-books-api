import pandas as pd

df = pd.read_csv("data/books.csv")
# Exemplo simples de limpeza: normalizar preços e ratings
df["price"] = pd.to_numeric(df["price"], errors="coerce")
map_rating = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5,
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
}
if "rating" in df.columns:
    df["rating"] = df["rating"].apply(lambda r: map_rating.get(str(r), r))
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0).astype(int)

df.to_csv("data/books.csv", index=False)
print("Transform complete.")
