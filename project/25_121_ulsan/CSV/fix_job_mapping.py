import pandas as pd
import os

def fix_and_map_job_data():
    job_path = r'd:\git_rk\project\25_121_ulsan\CSV\직종_raw data.csv'
    keco_path = r'd:\git_rk\project\25_121_ulsan\CSV\KECO.csv'

    print("Loading Job and KECO data...")
    # Read KECO mapping data
    # KECO.csv has no header, it's Code, Name
    df_keco = pd.read_csv(keco_path, header=None, encoding='utf-8', names=['code', 'name'])
    
    # Pre-process KECO names for mapping
    def normalize_text(text):
        if pd.isna(text): return ""
        text = str(text).replace('·', '').replace(',', '').replace(' ', '')
        return text

    df_keco['norm_name'] = df_keco['name'].apply(normalize_text)
    keco_dict = dict(zip(df_keco['norm_name'], df_keco['code']))

    # Read Job data
    df_job = pd.read_csv(job_path, encoding='utf-8')
    
    # 1. Cleaning: Remove empty rows
    df_job = df_job.dropna(subset=['KECO'], how='all')
    
    # 2. Fix Mapping based on KECO name
    # If KECO2_NM is missing or needs update, we use KECO column to find code in KECO.csv
    def update_mapping(row):
        keco_name = str(row['KECO']).strip()
        norm_keco = normalize_text(keco_name)
        
        # SPECIAL CASES for matching (some names are slightly different)
        if norm_keco == "기타": return "9999", "기타"
        if norm_keco == "-": return "알수없음", "알수없음"
        
        # Find in KECO dictionary
        code = keco_dict.get(norm_keco)
        if code:
            # Found exact match after normalization
            return str(code).zfill(4), keco_name
        
        # Fallback: if not found, keep existing or mark unknown
        if pd.notna(row['KECO2_CD']) and row['KECO2_CD'] != "":
            return row['KECO2_CD'], row['KECO2_NM']
        
        return "알수없음", "알수없음"

    # Apply mapping
    new_data = df_job['KECO'].apply(lambda x: update_mapping(pd.Series({'KECO': x, 'KECO2_CD': '', 'KECO2_NM': ''})))
    df_job['KECO2_CD'] = new_data.apply(lambda x: x[0])
    df_job['KECO2_NM'] = new_data.apply(lambda x: x[1])

    # 3. Final Sorting and Cleaning
    # Sorting by CD or logic? User mentioned "38행부터 이상하게 되어 있다"
    # Usually we want to keep the order or sort by CD
    def clean_cd(val):
        try:
            return int(float(val))
        except:
            return 9999

    df_job['sort_key'] = df_job['CD'].apply(clean_cd)
    df_job = df_job.sort_values(by='sort_key').drop(columns=['sort_key'])

    # Save results
    df_job.to_csv(job_path, index=False, encoding='utf-8')
    print(f"Successfully fixed and saved to {job_path}")

    # Show results
    print("\n[Job Mapping Result Sample]")
    print(df_job.tail(40))

if __name__ == "__main__":
    fix_and_map_job_data()
