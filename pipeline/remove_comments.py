import pandas as pd  # Import pandas for data manipulation

# 1. Define input and output file paths
# Input file (contains comments)
input_file = "../data/out/reviews_with_sentiment.csv"   
# Output file (comments removed)    
output_file = "../data/out/reviews_no_comments.csv"         

# 2. Read the CSV file
df = pd.read_csv(input_file)

# 3. Check and drop the comments column if it exists
# If the comments column exists
if "comments" in df.columns:  
    # Drop it 
    df = df.drop(columns=["comments"])  

# 4. Save the cleaned file
df.to_csv(output_file, index=False, encoding="utf-8-sig")  
# index=False → do not save row index
# encoding="utf-8-sig" → ensures Excel displays text correctly (especially for non-English characters)

# 5. Print summary
print(f" Done. New file saved as {output_file}, rows={len(df)}, cols={len(df.columns)}")