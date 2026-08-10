import polars as pl   # Import Polars for large-scale CSV processing
import pandas as pd   # Import Pandas for appending results to CSV
import torch          # Import PyTorch for model inference
import time           # Import time for elapsed/ETA calculation
import os             # Import os for file handling
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
# Import tokenizer, model, and pipeline from Hugging Face

# 1. Input & Output paths
input_file = "../data/out/reviews_matched_dublin.csv"   # Input file
output_file = "../data/out/reviews_with_sentiment.csv"     # Output file
checkpoint_file = "../data/out/checkpoint.txt"             # Checkpoint file for resuming
log_file = "../data/out/run.log"                           # Log file

# Remove old output/logs if starting fresh
if not os.path.exists(checkpoint_file):
    for f in [output_file, log_file]:
        if os.path.exists(f):
            os.remove(f)

# 2. Count total rows
with open(input_file, "r", encoding="utf8") as f:
    total_rows = sum(1 for _ in f) - 1   # Subtract header
print(f"Total rows: {total_rows:,}")

# 3. Load model
local_dir = "./models/multilingual-sentiment"   # Local cache directory
tokenizer = AutoTokenizer.from_pretrained("tabularisai/multilingual-sentiment-analysis", cache_dir=local_dir)  # Load tokenizer
model = AutoModelForSequenceClassification.from_pretrained("tabularisai/multilingual-sentiment-analysis", cache_dir=local_dir)  # Load model
sentiment_model = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, device=0, batch_size=32)  # Create pipeline with GPU

# 4. Chunk settings & checkpoint
chunk_size = 5000          # Number of rows per chunk
start_time = time.time()    # Record start time

# Resume from checkpoint if exists
if os.path.exists(checkpoint_file):
    with open(checkpoint_file, "r") as f:
        offset = int(f.read().strip())
    print(f"⚡ Resuming from checkpoint: {offset}")
else:
    offset = 0
    print("Starting from scratch")

# Log function
def write_log(msg):
    with open(log_file, "a", encoding="utf8") as f:
        f.write(msg + "\n")

# 5. Label mapping with intensity
label_weights = {
    "very negative": -1.0,
    "negative": -0.5,
    "neutral": 0.0,
    "positive": 0.5,
    "very positive": 1.0,
    "mixed": 0.0
}

# Function to check if a comment exceeds 512 tokens
def is_too_long(text, tokenizer, max_len=512):
    if not text or not isinstance(text, str):
        return False
    tokens = tokenizer.encode(text, truncation=False, add_special_tokens=False)
    return len(tokens) > max_len

# 6. Chunk loop
while offset < total_rows:
    try:
        # Load data chunk using Polars lazy scan
        batch = pl.scan_csv(input_file).slice(offset, chunk_size).collect()

        if batch.is_empty():
            break

        if "comments" not in batch.columns:
            raise KeyError("Missing 'comments' column")

        # Clean comments: replace None or too-long comments with empty string
        comments = []
        for c in batch["comments"].to_list():
            if not c or not isinstance(c, str):
                comments.append("")
            elif is_too_long(c, tokenizer):
                comments.append("")   # Drop overly long comments
            else:
                comments.append(c)

        labels, scores = [], []
        # Mini-batch inference (avoid GPU OOM)
        for j in range(0, len(comments), 512):
            retries = 0
            # Retry up to 3 times if GPU runs out of memory
            while retries < 3:  
                try:
                    preds = sentiment_model(comments[j:j+512], truncation=True, max_length=512)
                    break
                except RuntimeError as e:
                    retries += 1
                    if retries >= 3:
                        raise e
                    time.sleep(10)

            for pred in preds:
                label = pred["label"].lower()
                labels.append(label)
                # Get intensity weight
                weight = label_weights.get(label, 0.0)
                # Compute intensity score   
                score = weight * pred["score"]           
                scores.append(score)

        # Add new columns to Polars DataFrame
        batch = batch.with_columns([
            pl.Series("sentiment_label", labels, dtype=pl.Utf8),
            pl.Series("sentiment_score", scores, dtype=pl.Float64)
        ])

        # Convert to Pandas and append to CSV
        batch_pd = batch.to_pandas()
        batch_pd.to_csv(output_file,
                        mode="a",
                        header=(offset == 0 and not os.path.exists(checkpoint_file)),
                        index=False,
                        encoding="utf8",
                        quoting=1)

        # Update progress
        processed = offset + batch.height
        elapsed = time.time() - start_time
        speed = processed / elapsed
        remaining = (total_rows - processed) / speed
        percent = (processed / total_rows) * 100

        msg = (f"Chunk offset={offset}: Processed {processed:,}/{total_rows:,} "
               f"({percent:.2f}%) | Elapsed {elapsed/60:.1f} min | ETA {remaining/60:.1f} min")
        print(msg); write_log(msg)

        # Save checkpoint
        offset += chunk_size
        with open(checkpoint_file, "w") as f:
            f.write(str(offset))

    except Exception as e:
        msg = f"Error offset={offset}: {e}, skipping"
        print(msg); write_log(msg)
        offset += chunk_size
        continue

# 7. Task finished
msg = "Sentiment analysis finished. Results saved to " + output_file
print(msg); write_log(msg)

if os.path.exists(checkpoint_file):
    os.remove(checkpoint_file)