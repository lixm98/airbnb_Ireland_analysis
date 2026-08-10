# Data Cleaning and Processing

Notes written while working on the project, tidied up.

These notes cover my own Python implementation. The team submitted a teammate's R version of the cleaning and sentiment analysis — see the [README](../README.md).

```
reviews.csv ──┐
              ├─► clean_reviews.py ──┐
listings.csv ─┴─► clean_listing.py ──┴─► match_reviews.py
                                              │
                                              ▼
                                   sentiment_analysis_local.py
                                              │
                                              ▼
                                      remove_comments.py
                                              │
                                              ▼
                                     structured CSV → Tableau
```

Scripts read from `../data/sample/` and write to `../data/out/`. Run them from this folder.

## Tools

Sentiment model:

- **HuggingFace Inference API** — remote multilingual classification, returns labels and probabilities. Used it first while testing, then dropped it: too slow, and it kept hitting rate limits.
- **HuggingFace Transformers, local** — `AutoTokenizer` and `AutoModelForSequenceClassification` loaded offline. This is the version I ended up using. It made batch processing of the whole review set possible.

Python packages:

| Package | Used for |
|---|---|
| `polars` | Chunked CSV loading and cleaning. Faster and lighter on memory than pandas at this size |
| `pandas` | Joining listings to reviews, appending results to CSV |
| `re` | Stripping HTML tags, normalising whitespace |
| `torch` | Runs the sentiment model |
| `transformers` | Tokeniser, model, sentiment pipeline |
| `time` / `os` | Progress logging and checkpointing |
| `requests` | Calling the inference API during the testing phase |

## Step 1 — Clean `reviews.csv`

Goal: valid, clean review text for the sentiment work.

Script: `clean_reviews.py`

1. Keep reviews dated 2020-01-01 to 2024-12-31.
2. Drop rows missing `date` or `comments`.
3. Deduplicate on `listing_id` + `reviewer_id` + `comments`, so repeat reviews don't skew anything.
4. Drop reviews shorter than 3 characters or longer than 2,000.
5. Strip HTML tags, collapse repeated whitespace and line breaks.

On the date range: 2020–2024 is what the team had agreed when I wrote this. We revised the analytical window later, after settling on the R implementation, and the submitted analysis uses the revised range. I've left the filter here as it was rather than editing it after the fact.

## Step 2 — Clean `listings.csv`

Goal: a clean set of Dublin-area listings, to look at what drives booking performance.

Script: `clean_listing.py`

1. Drop the URL columns (`listing_url`, `picture_url`, `host_url`, `host_thumbnail_url`, `host_picture_url`). They add size and nothing else.
2. Work out which listings are in Dublin. A latitude/longitude bounding box (roughly 53.2–53.45 N, -6.5 to -6.0 E) handles most of it. Where coordinates are missing, fall back to matching Dublin district names and postcodes against the `neighbourhood` text. Result goes into a new `is_Dublin` column.
3. Keep only the columns the analysis needs — listing attributes (`id`, `name`, `neighbourhood`, `room_type`, `accommodates`, `beds`, `price`), host attributes (`host_id`, `host_is_superhost`, `host_response_time`, `host_response_rate`), availability (`availability_365`, `minimum_nights`, `maximum_nights`), ratings (`number_of_reviews`, `review_scores_rating`, `review_scores_cleanliness`, `review_scores_location`).
4. Validation: drop rows where `price` is missing or at or below zero; drop `minimum_nights` over 3650 (stays longer than ten years); drop rows missing `id`, `room_type`, `price` or `availability_365`; deduplicate on `id`, keeping the first.

The fallback in step 2 is there because a bounding box on its own drops every listing with no coordinates, without telling you.

## Step 3 — Match listings to reviews

Goal: keep only reviews belonging to Dublin listings.

Script: `match_reviews.py`

1. `reviews.listing_id` joins to `listings.id`.
2. Inner join on that key.
3. Keep rows where `is_Dublin == 1`. Rename the clashing keys: `id_x` to `review_id`, `id_y` to `source_listing_id`.
4. Write out the Dublin-only review set.

## Step 4 — Sentiment analysis

Goal: turn review text into something Tableau can use.

Scripts: `sentiment_analysis_api.py` (first version) and `sentiment_analysis_local.py` (the one used)

1. Pick a multilingual HuggingFace model. The reviews aren't all in English, so this matters.
2. Generate two columns: `sentiment_label` (positive, negative, neutral, very positive, very negative) and `sentiment_score` (numeric, -1 to 1).
3. Drop the `comments` column, which leaves a fully structured dataset (`remove_comments.py`).

`sentiment_score` is an expected valence calculated from the softmax probabilities and the category weights. Above 0 is positive, below 0 is negative, magnitude reflects confidence. It isn't an intensity scale — 0.8 isn't twice as positive as 0.4.

## Why I switched off the API

The first version sent one HTTP request per review. At this volume that's slow, rate limits get in the way, and a dropped connection loses the batch you were partway through. Running the model locally took the network out of the loop and let me batch properly. `sentiment_analysis_local.py` also writes a checkpoint file and picks up from it, so a run that dies doesn't start over.

Both versions are still here.
