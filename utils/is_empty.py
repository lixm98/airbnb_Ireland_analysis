import pandas as pd

# Read the original reference table
df = pd.read_csv("../data/sample/listings_dublin_cleaned.csv", dtype={"host_id": str})

# Statistics on missing host_id
null_count = df["host_id"].isna().sum()
total = len(df)

print(f"Total rows: {total}")
print(f"Rows with empty host_id: {null_count}")
print(f"Missing ratio: {null_count / total:.2%}")