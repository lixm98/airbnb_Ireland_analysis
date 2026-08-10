import polars as pl

df = pl.read_csv("../data/sample/listings_dublin_cleaned.csv")
print(df.columns)
print(len(df.columns))