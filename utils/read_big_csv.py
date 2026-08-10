import pandas as pd
import polars as pl

# Use chunksize to read in chunks to avoid loading into memory at once
chunksize = 100000  # Read 100,000 rows at a time
file_path = "../data/sample/reviews_sample_1000.csv"

# First read the first 10 rows to see the column structure
df_head = pd.read_csv(file_path, nrows=10)
print(df_head.head())

# Read in chunks and count rows
row_count = 0
for chunk in pd.read_csv(file_path, chunksize=chunksize):
    row_count += len(chunk)
print("Total rows:", row_count)

# Read only the first 5 rows and quickly view column names
df_head = pl.read_csv(file_path, n_rows=5)
print(df_head.columns)
print(df_head.head())