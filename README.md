# Airbnb Ireland Market Analysis

MSc Business Analytics, Trinity College Dublin. Data Management and Visualisation module, October 2025.

Ireland brings in a mandatory national register for short-term rentals in May 2026. We looked at the Irish Airbnb market ahead of that change: how the market actually performs, and where the problems are. The Overview dashboard covers the whole country, down to county-level rankings.

## My part

Group project, six people. What I did:

- Conceptual ERD and logical relational model (`diagrams/`)
- The Overview dashboard in Tableau (`dashboard/`)
- The Python in this repo (`pipeline/`, `utils/`)

The Host and Customer dashboards were built by teammates and aren't included here.

One thing to be clear about: this Python pipeline is not what the team submitted. A teammate wrote the same pipeline in R and we went with that, since R was what the module taught. I've put mine up because it's my own work and it shows how I handle data at this size.

## Layout

| Folder | Contents |
|---|---|
| `diagrams/` | Conceptual ERD in Chen notation, and the logical data model with tables, types and PK/FK |
| `dashboard/` | Screenshot of the Overview dashboard. It's a shared workbook, so publishing it live wasn't my call alone |
| `pipeline/` | Clean, match, sentiment, strip text. See [`PROCESS.md`](pipeline/PROCESS.md) |
| `utils/` | Small scripts written along the way: missing-value counts, date-format checks, column inspection, ID backfills |
| `data/sample/` | Small extracts so the scripts run without downloading gigabytes |
| `data/out/` | Empty. Scripts write here |

## What the pipeline does

Detail in [`pipeline/PROCESS.md`](pipeline/PROCESS.md). The pipeline is scoped to Dublin. The dashboard uses the team's Ireland-wide dataset.

**Reviews.** Filter by date. Drop rows with no `date` or `comments`. Deduplicate on `listing_id` + `reviewer_id` + `comments`. Remove reviews under 3 characters or over 2,000. Strip HTML tags and collapse whitespace. Read in chunks with `polars` — the file doesn't fit in memory.

**Listings.** Drop the URL columns, then work out which listings are in Dublin. A latitude/longitude bounding box does most of it. Where coordinates are missing, the script falls back to matching Dublin district names and postcodes against the `neighbourhood` text, otherwise those rows would just disappear. Then the usual checks: price above zero, `minimum_nights` under ten years, no duplicate IDs.

**Match.** Inner join reviews to listings on `listing_id` = `id`, keep the Dublin rows.

**Sentiment.** Classify each review with a multilingual HuggingFace model to get a label and a score. My first version called the hosted API once per review, which was too slow and kept hitting rate limits, so I switched to running the model locally with batching and a checkpoint file. Both versions are in `pipeline/`. Last step drops the `comments` column so Tableau gets a fully structured dataset.

## A note on `sentiment_score`

It's an expected valence worked out from the softmax probabilities and the category weights. Above 0 is positive, below 0 is negative, and the magnitude reflects confidence. It isn't a scale of intensity — 0.8 doesn't mean twice as positive as 0.4, so don't plot it as though it were.

## Data

Irish `listings.csv` and `reviews.csv` from [Inside Airbnb](https://insideairbnb.com/), CC BY 4.0. The raw files are hundreds of megabytes and aren't in the repo. `data/sample/` has small extracts instead.

## Running it

```bash
pip install polars pandas torch transformers langdetect
export HF_TOKEN=your_token_here   # only for sentiment_analysis_api.py
```

Paths are relative: scripts read from `../data/sample/` and write to `../data/out/`, so run them from inside `pipeline/` or `utils/`.
