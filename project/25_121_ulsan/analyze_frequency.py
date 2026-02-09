import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
import os

def analyze_frequency():
    # Paths
    industry_path = r'd:\git_rk\project\25_121_ulsan\CSV\업종_raw data.csv'
    job_path = r'd:\git_rk\project\25_121_ulsan\CSV\직종_raw data.csv'
    mid_mapping_path = r'd:\git_rk\project\25_121_ulsan\CSV\표준산업분류_중분류.csv'
    output_dir = r'd:\git_rk\project\25_121_ulsan\REPORT'
    os.makedirs(output_dir, exist_ok=True)

    print("Analyzing Industry (업종) Frequency...")
    df_ind = pd.read_csv(industry_path, encoding='utf-8')
    df_mid = pd.read_csv(mid_mapping_path, encoding='utf-8')
    
    # Pre-process s3 to match mapping code (ensure 2 digits string)
    def clean_s3(val):
        try:
            if pd.isna(val) or val == '알수없음': return '알수없음'
            return str(int(float(val))).zfill(2)
        except:
            return '알수없음'
    
    df_ind['s3_code'] = df_ind['s3'].apply(clean_s3)
    df_mid['코드'] = df_mid['코드'].astype(str).str.zfill(2)
    
    # Merge names
    df_ind_merged = df_ind.merge(df_mid, left_on='s3_code', right_on='코드', how='left')
    df_ind_merged['중분류명'] = df_ind_merged['중분류명'].fillna('알수없음')
    
    # Frequency count
    ind_freq = df_ind_merged['중분류명'].value_counts().reset_index()
    ind_freq.columns = ['항목', '빈도']
    
    print("Analyzing Job (직종) Frequency...")
    df_job = pd.read_csv(job_path, encoding='utf-8')
    # Use KECO2_NM (Broad category name)
    job_freq = df_job['KECO2_NM'].dropna().value_counts().reset_index()
    job_freq.columns = ['항목', '빈도']

    # Visualization
    plt.figure(figsize=(12, 12))
    
    # Industry Plot
    plt.subplot(2, 1, 1)
    top_ind = ind_freq.head(15)
    plt.barh(top_ind['항목'], top_ind['빈도'], color='skyblue')
    plt.title('업종별 중분류 분포 (Top 15)')
    plt.xlabel('하위 항목 수')
    plt.gca().invert_yaxis()

    # Job Plot
    plt.subplot(2, 1, 2)
    top_job = job_freq.head(15)
    plt.barh(top_job['항목'], top_job['빈도'], color='salmon')
    plt.title('직종별 대분류 분포 (Top 15)')
    plt.xlabel('하위 항목 수')
    plt.gca().invert_yaxis()

    plt.tight_layout()
    plot_path = os.path.join(output_dir, 'frequency_analysis.png')
    plt.savefig(plot_path)
    print(f"Plot saved to {plot_path}")

    # Save CSV tables
    ind_freq.to_csv(os.path.join(output_dir, 'industry_frequency.csv'), index=False, encoding='utf-8-sig')
    job_freq.to_csv(os.path.join(output_dir, 'job_frequency.csv'), index=False, encoding='utf-8-sig')
    
    print("\n[Industry Frequency Top 5]")
    print(ind_freq.head(5))
    print("\n[Job Frequency Top 5]")
    print(job_freq.head(5))

if __name__ == "__main__":
    analyze_frequency()
