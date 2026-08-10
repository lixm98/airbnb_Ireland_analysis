import polars as pl   # Import Polars, a high-performance library for handling large CSV files (faster than pandas)
import requests       # Import requests library to send HTTP requests to Hugging Face API
import os             # Import os library for file and directory operations

# Hugging Face API configuration
API_URL = "https://api-inference.huggingface.co/models/tabularisai/multilingual-sentiment-analysis"  
# API_URL: The endpoint of the Hugging Face model (multilingual sentiment analysis)

headers = {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}  
# Reads the token from the HF_TOKEN environment variable - never hard-code a key.
# headers: HTTP request headers, containing authorization info (Bearer token).  
# Variable name clearly indicates it holds HTTP headers.

# Define a function to send a request to the API and return sentiment prediction
def query(text):
    try:
        # Send a POST request with the review text as "inputs"
        response = requests.post(API_URL, headers=headers, json={"inputs": text})
        result = response.json()  # Parse response into JSON format
        # Check if the result is valid and extract the first label
        if isinstance(result, list) and len(result) > 0:
            return result[0][0]["label"]  # Return sentiment label (Positive/Neutral/Negative)
        else:
            return "error"  # Return "error" if response is invalid
    except:
        return "error"  # Return "error" if request fails

# Input file and output directory
input_file = "reviews.csv"             # input_file: Path to the input review file
output_dir = "sentiment_results"       # output_dir: Folder to store output results
os.makedirs(output_dir, exist_ok=True) # Create the directory if not existing, safe if already exists

# Chunking parameters
batch_size = 50000   # Number of rows per chunk (to avoid memory issues). Name "batch_size" indicates batch size.
offset = 0           # Starting row index for reading. Name "offset" indicates shift/starting point.
chunk_id = 1         # Counter for output file naming. Name "chunk_id" indicates chunk identifier.

# Loop to process the entire file until finished
while True:
    # Read one chunk of CSV with Polars
    df_chunk = pl.read_csv(
        input_file,
        has_header=True,              # The first row is treated as header
        skip_rows_after_header=offset,# Skip rows after the header according to current offset
        n_rows=batch_size             # Read only batch_size rows at a time
    )
    if df_chunk.is_empty():  # If no data read, end of file reached
        break

    # Perform sentiment analysis on reviews
    sentiments = [query(str(x)) for x in df_chunk["comments"]]  
    # Apply query function on each review text in "comments" column
    df_chunk = df_chunk.with_columns(pl.Series(name="sentiment", values=sentiments))  
    # Add new column "sentiment" with the predicted labels

    # Save result to small CSV file
    output_file = os.path.join(output_dir, f"reviews_sentiment_part{chunk_id}.csv")  
    # Output files named reviews_sentiment_part1.csv, part2.csv, etc.
    df_chunk.select(["comments", "sentiment"]).write_csv(output_file)  
    # Save only "comments" and "sentiment" columns

    print(f"Saved {output_file}")  # Print progress info for user
    offset += batch_size  # Move offset forward for next chunk
    chunk_id += 1         # Increment chunk ID for output file naming

print("All chunks processed successfully!")  # Final message when all chunks processed