# -*- coding: utf-8 -*-
import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd

f = r'd:\git_rk\data\factory_on\202601\company_list\electronics_iot\260318_1622\company_electronics_iot_employees_10_and_over_F_260318_1622.csv'
df = pd.read_csv(f, encoding='utf-8-sig', nrows=5)

print("=== All columns ===")
for i, c in enumerate(df.columns):
    print(f"  [{i}] {c}")

print("\n=== Sample 업종코드_전체 ===")
print(df['업종코드_전체'].head().to_string())

print("\n=== Sample 대표업종코드(중) ===")
print(df['대표업종코드(중)'].head().to_string())

print("\n=== Sample row 0 ===")
for c in df.columns:
    print(f"  {c}: {df.at[0, c]}")
