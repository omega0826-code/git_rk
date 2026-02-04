import pandas as pd
import os
import re
from datetime import datetime

# Paths
base_dir = r'd:\git_rk\project\25_121_ulsan'
raw_data_path = os.path.join(base_dir, 'CSV', '직종_raw data.csv')
keco_ref_path = os.path.join(base_dir, 'CSV', 'KECO.CSV')
report_dir = os.path.join(base_dir, 'REPORT')

def normalize_text(text):
    if pd.isna(text):
        return ""
    # Remove spaces, dots, hyphens, commas, etc.
    return re.sub(r'[\s·\-,()\[\]]', '', str(text))

def run_keco2_mapping():
    try:
        print("Loading data...")
        # Load raw data
        df_raw = pd.read_csv(raw_data_path)
        
        # Load KECO reference (Code, Name) - no header
        df_ref = pd.read_csv(keco_ref_path, header=None, names=['Code', 'Name'])
        
        # Clean up reference data
        df_ref = df_ref.dropna(subset=['Name'])
        
        # Create normalization for matching
        df_raw['keco_norm'] = df_raw['KECO'].apply(normalize_text)
        df_ref['name_norm'] = df_ref['Name'].apply(normalize_text)
        
        # Create mapping dictionary for code and name
        mapping_dict_cd = dict(zip(df_ref['name_norm'], df_ref['Code']))
        mapping_dict_nm = dict(zip(df_ref['name_norm'], df_ref['Name']))
        
        print("Mapping KECO2 codes and names...")
        # Apply mapping
        df_raw['KECO2_CD'] = df_raw['keco_norm'].map(mapping_dict_cd)
        df_raw['KECO2_NM'] = df_raw['keco_norm'].map(mapping_dict_nm)
        
        # Handle cases where mapping failed
        df_raw['KECO2_CD'] = df_raw['KECO2_CD'].fillna('알수없음')
        df_raw['KECO2_NM'] = df_raw['KECO2_NM'].fillna('알수없음')
        
        # Drop temp column and possible old KECO2 column if exists
        cols_to_drop = ['keco_norm']
        if 'KECO2' in df_raw.columns:
            cols_to_drop.append('KECO2')
            
        df_final = df_raw.drop(columns=cols_to_drop)
        
        # Save updated CSV (using utf-8-sig for Korean Excel compatibility)
        df_final.to_csv(raw_data_path, index=False, encoding='utf-8-sig')
        print(f"Updated file saved to: {raw_data_path}")
        
        # Generate Report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f'KECO2_Mapping_Full_Report_{timestamp}.md'
        report_path = os.path.join(report_dir, report_filename)
        
        success_count = (df_final['KECO2_CD'] != '알수없음').sum()
        fail_count = (df_final['KECO2_CD'] == '알수없음').sum()
        
        # Collect failed items for report
        failed_items = df_final[df_final['KECO2_CD'] == '알수없음']['KECO'].unique().tolist()
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f'# KECO2 코드 및 명칭 매핑 결과 리포트\n\n')
            f.write(f'- 실행 일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'- 대상 파일: `직종_raw data.csv`\n')
            f.write(f'- 참조 파일: `KECO.CSV`\n')
            f.write(f'- 매핑 성공: {success_count}건\n')
            f.write(f'- 매핑 실패: {fail_count}건\n\n')
            
            if failed_items:
                f.write(f'## 매핑 실패 항목 리스트 (KECO 명칭 기준)\n')
                for item in failed_items:
                    f.write(f'- {item}\n')
                f.write('\n')
                
            f.write(f'## 상위 20개 결과 샘플\n\n')
            f.write(df_final.head(20).to_markdown(index=False))
            
        print(f"Report generated: {report_path}")
        return report_path
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    run_keco2_mapping()
                                                                                