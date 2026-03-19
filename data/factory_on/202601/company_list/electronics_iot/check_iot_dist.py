# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd

CSV = r"d:\git_rk\data\factory_on\202601\company_list\electronics_iot\260318_1634\company_electronics_iot_employees_10_and_over_F_260318_1634.csv"
df = pd.read_csv(CSV, encoding='utf-8-sig')

print(f"Total rows: {len(df)}")

# 관련 컬럼 인덱스
for i, c in enumerate(df.columns):
    if any(k in c for k in ['기존','전자','가전','IoT','KEA','예상','근거','업종']):
        print(f"  [{i}] {c}")

print("\n=== 가전IoT_예상 분포 ===")
print(df['가전IoT_예상'].value_counts(dropna=False).to_string())

print("\n=== KEA(추가) 분포 ===")
print(df['KEA(추가)'].value_counts(dropna=False).to_string())

print("\n=== 기존자료(가전IoT) 분포 ===")
print(df['기존자료(가전IoT)'].value_counts(dropna=False).to_string())

# KEA or 기존자료(가전IoT) 에서 O가 있는데 가전IoT_예상이 확정이 아닌 건
kea_o = df['KEA(추가)'].fillna('').str.strip().isin(['O','○'])
iot_o = df['기존자료(가전IoT)'].fillna('').str.strip().isin(['O','○'])
confirmed = df['가전IoT_예상'].fillna('').str.contains('확정')
needs_confirm = (kea_o | iot_o) & ~confirmed
print(f"\nKEA또는기존자료O이지만 미확정: {needs_confirm.sum()}")
if needs_confirm.sum() > 0:
    print(df.loc[needs_confirm, ['회사명','KEA(추가)','기존자료(가전IoT)','가전IoT_예상']].head(10).to_string())

print("\n=== 업종_가전IoT 분포 ===")
if '업종_가전IoT' in df.columns:
    print(df['업종_가전IoT'].value_counts(dropna=False).to_string())
