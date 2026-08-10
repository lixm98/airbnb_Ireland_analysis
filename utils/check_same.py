import polars as pl

# 1. Enter the file path
reviews_file = "../data/out/reviews_cleaned.csv"   # your reviews file
listings_file = "../data/sample/listings_dublin_cleaned.csv"                  # your listings file

# 2. Read the reviews table and remove duplicates
reviews = pl.read_csv(reviews_file)
unique_reviews = reviews.select("listing_id").unique()
print(f"Number of unique properties in Reviews: {unique_reviews.height}")

# 3. Read the listings table and remove duplicates + rename ids
listings = pl.read_csv(listings_file)
unique_listings = listings.select("id").unique().rename({"id": "listing_id"})
print(f"Number of unique properties in Listings: {unique_listings.height}")

# 4. Left join: check which listing_id exists
joined = unique_reviews.join(unique_listings, on="listing_id", how="left")

# Listings that exist
exists = joined.filter(pl.col("listing_id").is_not_null())
# Property that does not exist
not_exists = joined.filter(pl.col("listing_id").is_null())

print(f"✅ Number of matched properties:{exists.height}")
print(f"❌ Number of listings that do not exist in the listings table:{not_exists.height}")

# 5. Save results
exists.write_csv("../data/out/reviews_listings_matched.csv")
not_exists.write_csv("../data/out/reviews_listings_not_found.csv")

print("Results saved: reviews_listings_matched.csv and reviews_listings_not_found.csv")