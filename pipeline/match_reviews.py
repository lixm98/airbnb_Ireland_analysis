import pandas as pd

# 1. File paths
listings_file = "../data/out/listings_with_isDublin_cleaned.csv"  # Cleaned listings dataset
reviews_file = "../data/out/reviews_cleaned.csv" # Cleaned reviews dataset
output_file = "../data/out/reviews_matched_dublin.csv"     # Output file

# 2. Load data
listings = pd.read_csv(listings_file)   # Load listings data
reviews = pd.read_csv(reviews_file)     # Load reviews data
print("Listings columns:", listings.columns)
print("Reviews columns:", reviews.columns)

# 3. Match reviews with listings
matched = reviews.merge(
    listings[["id", "is_Dublin"]],   # Keep only id and is_Dublin from listings
    left_on="listing_id",            # Match reviews.listing_id
    right_on="id",                   # with listings.id
    how="inner"                      # Inner join: keep only matched rows
)

# 4. Filter: only keep listings in Dublin (is_Dublin == 1)
matched = matched[matched["is_Dublin"] == 1]

# 5. Rename columns for clarity
matched = matched.rename(columns={
    "id_x": "review_id",            # Review table id → review_id
    "id_y": "source_listing_id"     # Listings table id → source_listing_id
})

# 6. Drop is_Dublin (already filtered)
matched = matched.drop(columns=["is_Dublin"])

# 7. Save result
matched.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"Done. Matched Dublin reviews saved to {output_file}, rows={len(matched)}")