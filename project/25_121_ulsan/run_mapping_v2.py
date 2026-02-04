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
        df_raw = pd.read_csv(raw_data_path)
        df_ref = pd.read_csv(sic_ref_path)

        # Normalize industry names for better matching
        # Replace full-width semicolon '；' and others if needed
        def normalize(s):
            if pd.isna(s): return s
            return str(s).replace('；', ';').strip()

        df_raw['s1_norm'] = df_raw['s1'].apply(normalize)
        df_ref['중분류명_norm'] = df_ref['중분류명'].apply(normalize)

        # Mapping dictionary
        mapping_dict = dict(zip(df_ref['중분류명_norm'], df_ref['코드']))

        # Apply mapping
        df_raw['s3'] = df_raw['s1_norm'].map(mapping_dict)
        
        # Replace NaN with '알수없음'
        df_raw['s3'] = df_raw['s3'].fillna('알수없음')
        
        # Drop temp column
        df_raw = df_raw.drop(columns=['s1_norm'])
        
        # Save updated CSV
        df_raw.to_csv(raw_data_path, index=False, encoding='utf-8-sig')
        
        # Generate Report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(report_dir, f'SIC_Mapping_Report_Updated_{timestamp}.md')
        
        success_count = (df_raw['s3'] != '알수없음').sum()
        fail_count = (df_raw['s3'] == '알수없음').sum()
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f'# SIC Code 매핑 업데이트 리포트\n\n')
            f.write(f'- 실행 일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'- 대상 파일: `업종_raw data.csv`\n')
            f.write(f'- 참조 파일: `표준산업분류_중분류.csv` (업데이트됨)\n')
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
