import pandas as pd
import re
from collections import Counter

# Read Excel
df = pd.read_excel("../data/out/reviews_with_sentiment.xlsx")

# Convert date column to string (some may be numbers or NaN)
dates_str = df["date"].astype(str)

patterns = []

# Simply use regular expressions to identify common formats
for d in dates_str:
    if re.match(r"^\d{4}-\d{2}-\d{2}$", d):   # Yyyy mm dd
        patterns.append("YYYY-MM-DD")
    elif re.match(r"^\d{2}/\d{2}/\d{4}$", d): # DD/MM/YYYY or MM/DD/YYYY
        patterns.append("DD/MM/YYYY or MM/DD/YYYY")
    elif re.match(r"^\d{4}/\d{2}/\d{2}$", d): # Yyyy/mm/dd
        patterns.append("YYYY/MM/DD")
    elif re.match(r"^\d{2}-\d{2}-\d{4}$", d): # Dd mm yyyy
        patterns.append("DD-MM-YYYY")
    elif d.lower() == "nan":                  # Missing values
        patterns.append("NaN")
    else:
        patterns.append("Other/Unrecognized")

# Count the number of occurrences of each pattern
counts = Counter(patterns)

print("Date format statistical results:")
for fmt, cnt in counts.items():
    print(f"{fmt}: {cnt} rows")

# Optional: Print a few lines of abnormal data to see
print("\n Example exception date:")
print(dates_str[patterns.index("Other/Unrecognized")])