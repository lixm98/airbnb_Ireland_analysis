import pandas as pd

# Only the first 10 lines are read and no memory is occupied
df = pd.read_csv("../data/sample/listings_dublin_cleaned.csv", nrows=100)
print(df.head())