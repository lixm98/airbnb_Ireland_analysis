import pandas as pd

# 1. File path
main_file = "../data/out/neighbourhoods_cleaned.xlsx"   # Master data (missing host_id)
ref_file = "../data/sample/listings_dublin_cleaned.csv"                  # Reference data (with host_id)
output_file = "../data/out/neighbourhoods_with_hostid.xlsx"           # output file

# 2. Read data
main_df = pd.read_excel(main_file, dtype={"id": str})     # Force id to be a string
ref_df = pd.read_csv(ref_file, dtype={"id": str, "host_id": str})

# 3. Merge host_id (maintain the order of the original table)
merged = pd.merge(
    main_df,
    ref_df[["id", "host_id"]],
    on="id",
    how="left",
    sort=False
)

# 4. Match statistics
matched_count = merged["host_id"].notna().sum()
unmatched_count = merged["host_id"].isna().sum()
print(f"✅ Matched: {matched_count} rows, unmatched {unmatched_count} rows")

# 5. Save results
merged.to_excel(output_file, index=False, engine="openpyxl")
print(f"✅ Completed! Results saved to {output_file}, total {len(merged)} rows")