import pandas as pd
import os

# 원천 파일 경로
input_path = r'd:\git_rk\data\seoul hospital\HIRA_강남언니_결합_최종.csv'
# 출력 파일 경로
output_path = r'd:\git_rk\data\seoul hospital\강남구_추출_데이터.csv'

print(f"Reading data from {input_path}...")
try:
    df = pd.read_csv(input_path, encoding='utf-8')
except:
    df = pd.read_csv(input_path, encoding='cp949')

print(f"Original data size: {len(df)} rows")

# 필터링 조건 설정
target_sigungu = '강남구'
target_types = ['의원', '병원', '종합병원', '상급종합']

# 필터링 수행
filtered_df = df[(df['시군구코드명'] == target_sigungu) & (df['종별코드명'].isin(target_types))]

print(f"Filtered data size: {len(filtered_df)} rows")

# 결과 저장 (UTF-8-SIG for Excel compatibility with CJK)
print(f"Saving to {output_path}...")
filtered_df.to_csv(output_path, index=False, encoding='utf-8-sig')

print("Extraction Complete")
