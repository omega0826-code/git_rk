
import duckdb
from pathlib import Path
import os
import time

def run_conversion():
    base_dir = Path(r'd:\git_rk')
    raw_csv_path = base_dir / 'data' / 'gangnam_reviews_FINAL_ALL.csv'
    processed_dir = base_dir / 'data' / 'processed'
    output_parquet_path = processed_dir / 'gangnam_reviews.parquet'

    if not raw_csv_path.exists():
        print(f"Error: {raw_csv_path} not found.")
        return

    os.makedirs(processed_dir, exist_ok=True)

    print("Starting conversion...")
    start_time = time.time()
    
    con = duckdb.connect(database=':memory:')
    
    # Using read_csv with specific options to handle potential encoding or format issues
    # We use 'auto' but hint utf-8. If it fails, we might need latin-1 or cp949, 
    # but based on the check earlier, it's utf-8-sig.
    
    try:
        query = f"""
            COPY (
                SELECT 
                    hospital_id,
                    hospital_name,
                    review_id,
                    nickname,
                    try_cast(rating as FLOAT) as rating,
                    treatments,
                    content,
                    try_cast(date as DATE) as review_date,
                    has_photo
                FROM read_csv('{raw_csv_path}', 
                    auto_detect=true, 
                    ignore_errors=true,
                    sample_size=20000)
                WHERE rating IS NOT NULL
            ) TO '{output_parquet_path}' (FORMAT PARQUET, CODEC 'SNAPPY');
        """
        con.execute(query)
        print(f"Conversion finished in {time.time() - start_time:.2f} seconds.")
        
        # Verify
        count = con.execute(f"SELECT count(*) FROM parquet_scan('{output_parquet_path}')").fetchone()[0]
        print(f"Total rows in parquet: {count}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_conversion()
