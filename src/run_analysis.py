
import duckdb
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import os
from collections import Counter
import re

# Settings
plt.rcParams['font.family'] = 'Malgun Gothic' # Windows standard Korean font
plt.rcParams['axes.unicode_minus'] = False

base_dir = Path(r'd:\git_rk')
parquet_path = base_dir / 'data' / 'processed' / 'gangnam_reviews.parquet'
figures_dir = base_dir / 'output' / 'figures'
artifacts_dir = base_dir / 'output' / 'artifacts'

os.makedirs(figures_dir, exist_ok=True)
os.makedirs(artifacts_dir, exist_ok=True)

con = duckdb.connect(':memory:')

def run_analysis():
    print("Loading data for analysis...")
    
    # 1. Rating Distribution
    print("Analyzing Rating Distribution...")
    df_rating = con.execute(f"SELECT rating, count(*) as count FROM '{parquet_path}' GROUP BY rating ORDER BY rating").fetchdf()
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df_rating, x='rating', y='count', palette='viridis')
    plt.title('Rating Distribution')
    plt.xlabel('Rating')
    plt.ylabel('Count')
    plt.savefig(figures_dir / 'rating_distribution.png')
    plt.close()
    
    # 2. Time Trend (Monthly)
    print("Analyzing Time Trend...")
    query_time = f"""
        SELECT 
            strftime(review_date, '%Y-%m') as month,
            count(*) as count
        FROM '{parquet_path}'
        WHERE review_date IS NOT NULL
        GROUP BY 1
        ORDER BY 1
    """
    df_time = con.execute(query_time).fetchdf()
    
    plt.figure(figsize=(12, 6))
    # Convert month string to datetime for better plotting
    df_time['month'] = pd.to_datetime(df_time['month'])
    sns.lineplot(data=df_time, x='month', y='count')
    plt.title('Reviews over Time')
    plt.xlabel('Date')
    plt.ylabel('Review Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(figures_dir / 'reviews_over_time.png')
    plt.close()

    # 3. Top Treatments
    print("Analyzing Treatments...")
    # Treatments might be comma separated or single. Assuming simple string for now.
    # Grouping by the exact string in 'treatments' column.
    query_treatments = f"""
        SELECT treatments, count(*) as count, avg(rating) as avg_rating
        FROM '{parquet_path}'
        WHERE treatments IS NOT NULL
        GROUP BY 1
        ORDER BY count DESC
        LIMIT 20
    """
    df_treat = con.execute(query_treatments).fetchdf()
    
    plt.figure(figsize=(12, 8))
    sns.barplot(data=df_treat, y='treatments', x='count', palette='magma')
    plt.title('Top 20 Treatments by Review Count')
    plt.xlabel('Count')
    plt.ylabel('Treatment')
    plt.tight_layout()
    plt.savefig(figures_dir / 'top_treatments.png')
    plt.close()

    # 4. Simple NLP Sampling
    print("Performing NLP Sampling...")
    
    def get_top_keywords(rating_val, label):
        # Sample 2000 reviews
        query_sample = f"""
            SELECT content 
            FROM '{parquet_path}' 
            WHERE rating = {rating_val} AND content IS NOT NULL
            USING SAMPLE 2000
        """
        reviews = con.execute(query_sample).fetchall() # list of tuples
        
        text = " ".join([r[0] for r in reviews])
        # Simple regex split for Korean (and English)
        words = re.findall(r'\w+', text)
        
        # Filter short words
        words = [w for w in words if len(w) > 1]
        
        counter = Counter(words)
        return counter.most_common(20)

    top_bad = get_top_keywords(1, "Bad (1.0)")
    top_good = get_top_keywords(5, "Good (5.0)")
    
    with open(artifacts_dir / 'nlp_insights.txt', 'w', encoding='utf-8') as f:
        f.write("=== Top Keywords for Rating 1.0 ===\n")
        for word, count in top_bad:
            f.write(f"{word}: {count}\n")
        
        f.write("\n=== Top Keywords for Rating 5.0 ===\n")
        for word, count in top_good:
            f.write(f"{word}: {count}\n")
            
    print("Analysis Complete. Figures and Artifacts saved.")

if __name__ == "__main__":
    run_analysis()
