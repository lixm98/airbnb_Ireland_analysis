import pandas as pd

# Load raw listings file
df = pd.read_csv("../data/sample/listings_dublin_cleaned.csv")

# Count missing values in "price" column
null_count = df["price"].isna().sum()
total = len(df)

print(f"Total rows: {total}")
print(f"Rows with empty price: {null_count}")
print(f"Missing percentage: {null_count / total:.2%}")