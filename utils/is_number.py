import pandas as pd

# Load the file
df = pd.read_csv("../data/out/reviews_no_comments.csv")

# Find rows where sentiment_label contains digits
invalid_labels = df[df["sentiment_label"].astype(str).str.contains(r"\d")]

print("Number of rows where label column contains digits:", len(invalid_labels))
print(invalid_labels.head(10))  # Show the first 10 rows as a sample