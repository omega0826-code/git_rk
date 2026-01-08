
import duckdb
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import os

# Settings
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", font='Malgun Gothic')

base_dir = Path(r'd:\git_rk')
parquet_path = base_dir / 'data' / 'processed' / 'gangnam_reviews.parquet'
figures_dir = base_dir / 'output' / 'figures'
report_path = base_dir / 'output' / 'reports' / 'eda_detailed_summary.md'

os.makedirs(figures_dir, exist_ok=True)

con = duckdb.connect(':memory:')

def analyze_photo_impact():
    print("1. Analyzing Photo vs Rating...")
    query = f"""
        SELECT 
            has_photo,
            AVG(rating) as avg_rating,
            COUNT(*) as review_count
        FROM '{parquet_path}'
        GROUP BY has_photo
    """
    df = con.execute(query).fetchdf() 
    
    # Plot
    plt.figure(figsize=(6, 5))
    sns.barplot(data=df, x='has_photo', y='avg_rating', palette='coolwarm')
    plt.title('Average Rating: With vs Without Photo')
    plt.ylim(0, 5.5)
    for index, row in df.iterrows():
        plt.text(index, row.avg_rating, f'{row.avg_rating:.2f}', color='black', ha="center", va="bottom")
    plt.savefig(figures_dir / 'eda_photo_impact.png')
    plt.close()
    return df

def analyze_review_length():
    print("2. Analyzing Review Length vs Rating...")
    # Calculate length in SQL (length of content)
    query = f"""
        SELECT 
            rating,
            AVG(length(content)) as avg_length
        FROM '{parquet_path}'
        WHERE content IS NOT NULL
        GROUP BY rating
        ORDER BY rating
    """
    df = con.execute(query).fetchdf() 
    
    plt.figure(figsize=(8, 5))
    sns.lineplot(data=df, x='rating', y='avg_length', marker='o', color='purple')
    plt.title('Average Review Length by Rating')
    plt.xlabel('Rating')
    plt.ylabel('Avg Character Count')
    plt.savefig(figures_dir / 'eda_review_length.png')
    plt.close()
    return df

def analyze_top_hospitals():
    print("3. Analyzing Top Hospitals (Volume vs Rating)...")
    # Top 20 hospitals by review count
    query = f"""
        SELECT 
            hospital_name,
            COUNT(*) as count,
            AVG(rating) as avg_rating
        FROM '{parquet_path}'
        WHERE hospital_name IS NOT NULL
        GROUP BY hospital_name
        ORDER BY count DESC
        LIMIT 20
    """
    df = con.execute(query).fetchdf() 
    
    # Dual axis plot
    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    sns.barplot(data=df, x='hospital_name', y='count', ax=ax1, alpha=0.6, color='blue')
    ax1.set_ylabel('Review Count', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
    
    ax2 = ax1.twinx()
    sns.lineplot(data=df, x='hospital_name', y='avg_rating', ax=ax2, marker='o', color='red', linewidth=2)
    ax2.set_ylabel('Average Rating', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.set_ylim(0, 5.5)
    
    plt.title('Top 20 Hospitals: Volume vs Rating')
    plt.tight_layout()
    plt.savefig(figures_dir / 'eda_top_hospitals.png')
    plt.close()
    return df

def analyze_day_of_week():
    print("4. Analyzing Day of Week Trends...")
    # 0=Sunday, 6=Saturday in DuckDB depending on version, or use strftime %w (0-6, Sunday is 0)
    query = f"""
        SELECT 
            strftime(review_date, '%w') as dow_num,
            CASE strftime(review_date, '%w')
                WHEN '0' THEN 'Sun'
                WHEN '1' THEN 'Mon'
                WHEN '2' THEN 'Tue'
                WHEN '3' THEN 'Wed'
                WHEN '4' THEN 'Thu'
                WHEN '5' THEN 'Fri'
                WHEN '6' THEN 'Sat'
            END as day_of_week,
            COUNT(*) as count
        FROM '{parquet_path}'
        WHERE review_date IS NOT NULL
        GROUP BY 1, 2
        ORDER BY 1
    """
    df = con.execute(query).fetchdf() 
    
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x='day_of_week', y='count', palette='pastel')
    plt.title('Review Frequency by Day of Week')
    plt.savefig(figures_dir / 'eda_dow.png')
    plt.close()
    return df

def main():
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 상세 EDA 분석 결과\n\n")
        
        # 1. Photo
        df_photo = analyze_photo_impact()
        f.write("## 1. 사진 유무에 따른 평점 차이\n")
        f.write(df_photo.to_markdown(index=False) + "\n\n")
        
        # 2. Length
        df_len = analyze_review_length()
        f.write("## 2. 평점별 평균 리뷰 길이\n")
        f.write(df_len.to_markdown(index=False) + "\n\n")
        
        # 3. Hospitals
        df_hosp = analyze_top_hospitals()
        f.write("## 3. 상위 20개 병원 현황\n")
        f.write("리뷰 수 상위 병원들의 평점 편차를 시각화했습니다. (eda_top_hospitals.png 참고)\n")
        f.write(df_hosp.head(5).to_markdown(index=False) + "\n\n")
        
        # 4. DOW
        df_dow = analyze_day_of_week()
        f.write("## 4. 요일별 리뷰 작성 빈도\n")
        f.write(df_dow.to_markdown(index=False) + "\n\n")

    print(f"Detailed EDA complete. Report saved to {report_path}")

if __name__ == "__main__":
    main()
