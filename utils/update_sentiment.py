import polars as pl
import time
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# 1. Load the original results CSV
df = pl.read_csv("../data/out/reviews_with_sentiment.csv")

# 2. Select rows where sentiment_score == 0.0
subset = df.filter(pl.col("sentiment_score") == 0.0)
print(f"Number of reviews to re-analyze: {subset.height:,}")

# 3. Load model
local_dir = "./models/multilingual-sentiment"
tokenizer = AutoTokenizer.from_pretrained("tabularisai/multilingual-sentiment-analysis", cache_dir=local_dir)
model = AutoModelForSequenceClassification.from_pretrained("tabularisai/multilingual-sentiment-analysis", cache_dir=local_dir)
sentiment_model = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, device=0, batch_size=32)

# 4. Batch processing with progress bar
comments = subset["comments"].to_list()
new_scores = []
batch_size = 512
start_time = time.time()

for i in range(0, len(comments), batch_size):
    batch = comments[i:i+batch_size]
    preds = sentiment_model(batch, truncation=True, max_length=512)

    for pred in preds:
        label = pred["label"].lower()
        score = pred["score"]
        if "positive" in label:
            new_scores.append(score)
        elif "negative" in label:
            new_scores.append(-score)
        else:
            new_scores.append(0.0)

    # Progress output
    processed = i + len(batch)
    elapsed = time.time() - start_time
    speed = processed / elapsed
    remaining = (len(comments) - processed) / speed
    percent = (processed / len(comments)) * 100
    print(f"Progress: {processed}/{len(comments)} ({percent:.2f}%) | "
          f"Elapsed {elapsed/60:.1f} min | ETA {remaining/60:.1f} min")

# 5. Update scores
subset = subset.with_columns(pl.Series("sentiment_score", new_scores))

# 6. Merge back into original dataframe
df = df.join(subset.select(["id", "sentiment_score"]), on="id", how="left", suffix="_new")
df = df.with_columns(
    pl.when(pl.col("sentiment_score_new").is_not_null())
      .then(pl.col("sentiment_score_new"))
      .otherwise(pl.col("sentiment_score"))
      .alias("sentiment_score_final")
)

# 7. Save to new CSV
df = df.drop(["sentiment_score", "sentiment_score_new"]).rename({"sentiment_score_final": "sentiment_score"})
df.write_csv("reviews_with_sentiment_fixed.csv")

print("✅ Re-analysis complete, results saved to reviews_with_sentiment_fixed.csv")