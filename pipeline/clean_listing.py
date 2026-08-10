import polars as pl
import unicodedata

# 1 Paths
SRC = "../data/sample/listings_dublin_cleaned.csv"   # Input Airbnb listings dataset
OUT = "../data/out/listings_with_isDublin_cleaned.csv"   # Output cleaned dataset

# 2 Load data
df = pl.read_csv(SRC)

# 3 Text normalization
def normalize_text(s: str) -> str:
    """Normalize text: remove accents, lowercase, strip spaces"""
    if s is None:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.lower().strip()

# 4 Dublin keywords (fallback match)
dublin_keywords = [
    "dublin","lucan","tallaght","swords","blanchardstown","clondalkin",
    "dundrum","rathmines","drumcondra","howth","malahide","portmarnock",
    "dun laoghaire","blackrock","stillorgan","sandyford","leopardstown",
    "donnybrook","ballsbridge","rathfarnham","castleknock","santry",
    "ballymun","finglas","cabra","phibsborough","ranelagh","clontarf",
    "terenure","walkinstown","inchicore","raheny","fairview","foxrock",
    "monkstown","booterstown","ballyfermot","temple bar","portobello",
    "d01","d02","d03","d04","d05","d06","d07","d08","d09",
    "d10","d11","d12","d13","d14","d15","d16","d17","d18","d20","d22","d24","d6w"
]

def match_neighbourhood(s: str) -> bool:
    """Return True if text contains any Dublin keyword"""
    if not s:
        return False
    for k in dublin_keywords:
        if k in s:
            return True
    return False

# 5 Define Dublin bounding box
LAT_MIN, LAT_MAX = 53.2, 53.45
LON_MIN, LON_MAX = -6.5, -6.0

# 6 Add is_Dublin column
df = df.with_columns([
    pl.col("neighbourhood").cast(pl.Utf8).map_elements(normalize_text, return_dtype=pl.Utf8).alias("_neigh_norm")
])

df = df.with_columns([
    pl.when(
        (pl.col("latitude").is_not_null()) & (pl.col("longitude").is_not_null()) &
        (pl.col("latitude") >= LAT_MIN) & (pl.col("latitude") <= LAT_MAX) &
        (pl.col("longitude") >= LON_MIN) & (pl.col("longitude") <= LON_MAX)
    ).then(1)
    .when(pl.col("_neigh_norm").map_elements(match_neighbourhood, return_dtype=pl.Boolean))
    .then(1)
    .otherwise(0)
    .alias("is_Dublin")
])

df = df.drop("_neigh_norm")  # Drop helper column

# 7 Drop URL columns
url_cols = [c for c in df.columns if "url" in c.lower()]
if url_cols:
    df = df.drop(url_cols)
    print("Dropped URL columns:", url_cols)

# 8 Remove null/duplicate IDs
if "id" in df.columns:
    df = df.filter(pl.col("id").is_not_null())
    df = df.unique(subset=["id"], keep="first", maintain_order=True)

# 9 Price cleaning
if "price" in df.columns:
    df = df.with_columns(
        pl.col("price").cast(pl.Utf8).str.replace_all(r"[\$,]", "").cast(pl.Float64).alias("price")
    )
    df = df.filter((pl.col("price").is_not_null()) & (pl.col("price") > 0) & (pl.col("price") <= 5000))

# 10 Remove abnormal values
if "minimum_nights" in df.columns:
    df = df.filter(pl.col("minimum_nights") <= 3650)

# 11 Save output
df.write_csv(OUT)

print("Cleaning done ->", OUT)
print(f"Final shape: rows={df.height:,}, cols={df.width}")
print(df.select(["id","latitude","longitude","price","minimum_nights","is_Dublin"]).head(10))