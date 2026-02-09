import pandas as pd
import os

def analyze_frequency_simple():
    industry_path = r'd:\git_rk\project\25_121_ulsan\CSV\업종_raw data.csv'
    job_path = r'd:\git_rk\project\25_121_ulsan\CSV\직종_raw data.csv'
    mid_mapping_path = r'd:\git_rk\project\25_121_ulsan\CSV\표준산업분류_중분류.csv'
    output_dir = r'd:\git_rk\project\25_121_ulsan\REPORT'
    os.makedirs(output_dir, exist_ok=True)

    df_ind = pd.read_csv(industry_path, encoding='utf-8')
    df_mid = pd.read_csv(mid_mapping_path, encoding='utf-8')
    
    # Process s3
    def clean_s3(val):
        try:
            if pd.isna(val) or val == '알수없음': return '알수없음'
            return str(int(float(val))).zfill(2)
        except: return '알수없음'
    
    df_ind['s3_code'] = df_ind['s3'].apply(clean_s3)
    df_mid['코드'] = df_mid['코드'].astype(str).str.zfill(2)
    df_ind_merged = df_ind.merge(df_mid, left_on='s3_code', right_on='코드', how='left')
    df_ind_merged['중분류명'] = df_ind_merged['중분류명'].fillna('알수없음')
    ind_freq = df_ind_merged['중분류명'].value_counts().reset_index()
    ind_freq.columns = ['항목', '빈도']

    df_job = pd.read_csv(job_path, encoding='utf-8')
    job_freq = df_job['KECO2_NM'].dropna().value_counts().reset_index()
    job_freq.columns = ['항목', '빈도']

    # Generate Markdown Summary
    report_content = "# [분석 리포트] 업종 및 직종 빈도 분석\n\n"
    report_content += "## 1. 업종별 중분류 빈도 (상위 10)\n"
    report_content += ind_freq.head(10).to_markdown(index=False) + "\n\n"
    report_content += "## 2. 직종별 대분류 빈도 (상위 10)\n"
    report_content += job_freq.head(10).to_markdown(index=False) + "\n\n"
    
    print(report_content)
    
    with open(os.path.join(output_dir, 'ANALYSIS_SUMMARY.md'), 'w', encoding='utf-8') as f:
        f.write(report_content)

if __name__ == "__main__":
    analyze_frequency_simple()
