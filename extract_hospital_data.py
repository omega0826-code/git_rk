import pandas as pd
import os

def extract_hospital_data():
    source_path = r'd:\git_rk\data\seoul hospital\HIRA_강남언니_결합_최종.csv'
    output_dir = r'd:\git_rk\data\seoul hospital'
    output_path = os.path.join(output_dir, 'seoul_extraction.csv')
    
    # 1. Load data with multiple possible encodings
    try:
        df = pd.read_csv(source_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(source_path, encoding='cp949')
    
    print(f"Total rows loaded: {len(df)}")
    
    # 2. Filter by Medical Subject ("피부" included in 진료과목 or treatment_tags)
    # Note: Column names analyzed from sample
    subject_cols = ['진료과목', 'treatment_tags', '진료과목_개수'] # Added 진료과목_개수 just in case
    
    # Actually, based on the previous head() result, treatment_tags seems most reliable for "피부"
    # and 진료과목 might be a list of subjects.
    
    mask_subject = df.astype(str).apply(lambda row: row.str.contains('피부').any(), axis=1)
    
    # 3. Filter by Hospital Type
    allowed_types = ["의원", "병원", "종합병원", "상급종합병원"] # Added '상급종합병원' as it's common
    # Check what's actually in '종별코드명'
    mask_type = df['종별코드명'].isin(allowed_types)
    
    # Combine filters
    filtered_df = df[mask_subject & mask_type]
    
    print(f"Rows after filtering: {len(filtered_df)}")
    
    # 4. Save to CSV (UTF-8 as per user global rule)
    filtered_df.to_csv(output_path, index=False, encoding='utf-8-sig') # Added BOM for better Excel compatibility
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    extract_hospital_data()
