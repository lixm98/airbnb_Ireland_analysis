import pandas as pd

# Read Excel
df = pd.read_excel("../data/out/reviews_filtered.xlsx")

# Format date column as dd-mm-yy
df["date"] = pd.to_datetime(df["date"]).dt.strftime("%d-%m-%y")

# Rewrite Excel and the date will become dd-mm-yy
df.to_excel("../data/out/reviews_filtered_ddmmyy.xlsx", index=False)