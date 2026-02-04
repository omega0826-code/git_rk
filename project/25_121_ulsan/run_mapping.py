import pandas as pd
import os
from datetime import datetime

# Paths
raw_data_path = r'd:\git_rk\project\25_121_ulsan\CSV\업종_raw data.csv'
sic_ref_path = r'd:\git_rk\project\25_121_ulsan\CSV\표준산업분류_중분류.csv'
report_dir = r'd:\git_rk\project\25_121_ulsan\REPORT'

def run_mapping():
    try:
        # Load data
        # Using encoding='utf-8' or 'cp949' depending on the file content (the view_file showed readable Korean, likely utf-8 or system default)
        # Based on previous context, user wants utf-8.
        df_raw = pd.read_csv(raw_data_path)
        df_ref = pd.read_csv(sic_ref_path)

        # Mapping dictionary
        mapping_dict = dict(zip(df_ref['중분류'], df_ref['코드']))

        # Apply mapping
        df_raw['s3'] = df_raw['s1'].map(mapping_dict)
        
        # Replace NaN with '알수없음'
        df_raw['s3'] = df_raw['s3'].fillna('알수없음')
        
        # If the code should be string/int, we can format it. 
        # But '알수없음' makes it an object column.
        
        # Save updated CSV
        df_raw.to_csv(raw_data_path, index=False, encoding='utf-8-sig')
        
        # Generate Report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(report_dir, f'SIC_Mapping_Report_{timestamp}.md')
        
        success_count = (df_raw['s3'] != '알수없음').sum()
        fail_count = (df_raw['s3'] == '알수없음').sum()
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f'# SIC Code Mapping 결과 리포트\n\n')
            f.write(f'- 실행 일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'- 대상 파일: `업종_raw data.csv`\n')
            f.write(f'- 매핑 성공: {success_count}건\n')
            f.write(f'- 매핑 실패 (알수없음): {fail_count}건\n\n')
            f.write(f'## 상위 10개 결과 샘플\n\n')
            f.write(df_raw.head(10).to_markdown(index=False))
            
        print(f"Successfully processed {len(df_raw)} rows.")
        return report_path
    except Exception as e:
        print(f"Error during mapping: {e}")
        return None

if __name__ == "__main__":
    run_mapping()
