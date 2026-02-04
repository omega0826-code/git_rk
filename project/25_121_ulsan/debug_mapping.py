import pandas as pd
import os
import re

# Paths
base_dir = r'd:\git_rk\project\25_121_ulsan'
raw_path = os.path.join(base_dir, 'CSV', '직종_raw data.csv')
ref_path = os.path.join(base_dir, 'CSV', 'KECO.CSV')
out_path = os.path.join(base_dir, 'CSV', '직종_mapped_v3.csv')

def norm(t):
    return re.sub(r'[\s·\-,()\[\]]', '', str(t)) if pd.notna(t) else ''

try:
    df_raw = pd.read_csv(raw_path)
    df_ref = pd.read_csv(ref_path, header=None, names=['CD', 'NM']).dropna(subset=['NM'])
    
    mapping_cd = dict(zip(df_ref['NM'].apply(norm), df_ref['CD']))
    mapping_nm = dict(zip(df_ref['NM'].apply(norm), df_ref['NM']))
    
    df_raw['KECO2_CD'] = df_raw['KECO'].apply(norm).map(mapping_cd).fillna('알수없음')
    df_raw['KECO2_NM'] = df_raw['KECO'].apply(norm).map(mapping_nm).fillna('알수없음')
    
    if 'KECO2' in df_raw.columns:
        df_raw = df_raw.drop(columns=['KECO2'])
        
    df_raw.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f"SUCCESS: {out_path}")
except Exception as e:
    print(f"ERROR: {e}")
