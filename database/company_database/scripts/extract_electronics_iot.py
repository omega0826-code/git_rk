"""
전자산업 또는 IoT 컬럼이 'O'인 데이터를 추출하는 스크립트
"""
import pandas as pd
import os

# 경로 설정
input_dir = r"d:\git_rk\database\company_database\output\factory_on\202601"
input_file = os.path.join(input_dir, "company_cleaned_260307_1754F_classified.csv")
output_file = os.path.join(input_dir, "company_electronics_iot_extracted.csv")

# 데이터 로드
print(f"[1] 데이터 로드: {input_file}")
df = pd.read_csv(input_file, encoding="utf-8")
print(f"    전체 데이터: {len(df):,}건")

# 전자산업 또는 IoT가 'O'인 행 추출
mask = (df["전자산업"] == "O") | (df["IoT"] == "O")
df_extracted = df[mask].copy()

# 통계 출력
e_count = (df["전자산업"] == "O").sum()
iot_count = (df["IoT"] == "O").sum()
both_count = ((df["전자산업"] == "O") & (df["IoT"] == "O")).sum()
either_count = len(df_extracted)

print(f"\n[2] 추출 결과:")
print(f"    전자산업='O': {e_count:,}건")
print(f"    IoT='O':     {iot_count:,}건")
print(f"    둘 다 'O':   {both_count:,}건")
print(f"    전자산업 또는 IoT='O' (합계): {either_count:,}건")

# 저장
df_extracted.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"\n[3] 저장 완료: {output_file}")
print(f"    저장된 건수: {len(df_extracted):,}건")
