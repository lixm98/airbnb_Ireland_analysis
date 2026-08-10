import polars as pl
import datetime as dt

# 1. Read header to get column names
Big_data_path = "../data/sample/reviews_sample_1000.csv"
cols = pl.read_csv(Big_data_path, n_rows=0).columns
print("Original columns:", cols)

# 2. Count original rows (small eager read)
orig_count = pl.read_csv(Big_data_path).height
print(f"Original row count: {orig_count}")

# 3. Lazy-load the dataset
df = pl.scan_csv(Big_data_path)

# 4. Convert date
df = df.with_columns(
    pl.col("date").str.strptime(pl.Date, strict=False)
)

# 5. Filter by time range
start = dt.date(2020, 1, 1)
end   = dt.date(2024, 12, 31)
df = df.filter(pl.col("date").is_between(start, end, closed="both"))

# 6. Drop null values
df = df.drop_nulls(subset=["date", "comments"])

# 7. Clean text
df = df.with_columns(
    pl.col("comments")
      .str.strip_chars()
      .str.replace_all(r"<[^>]*>", "")
      .str.replace_all(r"\s+", " ")
      .alias("comments")
)

# 8. Filter out too short/long or empty comments
df = df.filter((pl.col("comments").str.len_chars() >= 3) & 
               (pl.col("comments").str.len_chars() <= 2000))

# 9. Deduplicate
if "id" in cols:
    df = df.unique(subset=["id"])
elif "reviewer_id" in cols:
    df = df.unique(subset=["listing_id", "reviewer_id", "comments"])
else:
    df = df.unique(subset=["listing_id", "comments"])

# 10. Collect and save
df_cleaned = df.collect()
df_cleaned.write_csv("../data/out/reviews_cleaned.csv")

# 11. Report
final_count = len(df_cleaned)
print("Cleaning done")
print(f"Original rows: {orig_count}")
print(f"Final rows: {final_count}")
print(f"Deleted ratio: {(orig_count - final_count) / orig_count:.2%}")