import polars as pl
from langdetect import detect, DetectorFactory
from multiprocessing import Pool, cpu_count

DetectorFactory.seed = 0

input_file = "../data/out/reviews_cleaned.csv"
text_column = "comments"
batch_size = 100000
workers = cpu_count()

def process_chunk(args):
    offset, batch_size = args
    try:
        df_chunk = pl.read_csv(
            input_file,
            has_header=True,
            skip_rows_after_header=offset,
            n_rows=batch_size
        )
        if df_chunk.is_empty():
            return (0, 0)

        total = 0
        english = 0
        for text in df_chunk[text_column]:
            total += 1
            try:
                if detect(str(text)) == "en":
                    english += 1
            except:
                continue
        return (total, english)

    except Exception as e:
        print(f"Error in chunk {offset}: {e}")
        return (0, 0)

if __name__ == "__main__":
    total_rows = pl.scan_csv(input_file).collect().height
    print(f"Total rows in file: {total_rows}")

    tasks = [(offset, batch_size) for offset in range(0, total_rows, batch_size)]

    total = 0
    english = 0
    with Pool(workers) as pool:
        for t, e in pool.imap_unordered(process_chunk, tasks):
            total += t
            english += e
            print(f"Processed {total} rows...")

    if total > 0:
        english_percent = english / total * 100
        print(f"✅ Total rows: {total}")
        print(f"✅ English comments: {english}")
        print(f"✅ English percentage: {english_percent:.2f}%")