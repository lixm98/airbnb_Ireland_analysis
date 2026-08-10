import pandas as pd

# Load Excel file
df = pd.read_excel("../data/out/reviews_with_sentiment.xlsx")

# Parse dates in DD/MM/YY format
df["date"] = pd.to_datetime(df["date"], format="%d/%m/%y", errors="coerce")

# Check date range
print("Date range:", df["date"].min(), "→", df["date"].max())

# Filter rows from 2023 onwards
df_recent = df[df["date"] >= "2022-01-01"]

# Save result
df_recent.to_excel("../data/out/reviews_filtered.xlsx", index=False)

print("✅ Dates parsed and filtered! Saved to reviews_2022_onwards.xlsx")