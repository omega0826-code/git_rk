import pandas as pd
import json
import os

path = r'd:\git_rk\data\seoul hospital\HIRA_강남언니_결합_최종.csv'
print(f"Loading data from {path}...")
try:
    df = pd.read_csv(path, encoding='utf-8')
    print("Loaded with utf-8")
except:
    df = pd.read_csv(path, encoding='cp949')
    print("Loaded with cp949")

print(f"Total rows: {len(df)}")
stats = {}
stats['overview'] = {'rows': len(df), 'cols': len(df.columns)}

print("Calculating numerical stats...")
num_cols = [c for c in ['총의사수', 'rating', 'review_count', 'event_count', '매칭_신뢰도', '진료과목_개수'] if c in df.columns]
if num_cols:
    stats['numerical'] = df[num_cols].describe().to_dict()

print("Calculating categorical stats...")
cat_cols = [c for c in ['종별코드명', '시군구코드명', '설립구분코드명', '강남언니_등록', '매칭_유형'] if c in df.columns]
stats['categorical'] = {col: df[col].value_counts().head(10).to_dict() for col in cat_cols}

print("Calculating missing values...")
stats['missing'] = df.isnull().sum().sort_values(ascending=False).head(20).to_dict()

output_file = 'stats_output.json'
print(f"Saving to {output_file}...")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

print("Analysis Complete")

