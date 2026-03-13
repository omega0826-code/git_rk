# -*- coding: utf-8 -*-
import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd

csv_path = r"d:\git_rk\database\company_database\raw_data\factory_on\202601\output\factory_cleaned_260304_1810.csv"
df = pd.read_csv(csv_path, encoding="utf-8-sig", nrows=5000)

eng_mask = df["회사명_비고"].notna() & df["회사명_비고"].str.contains("[영문포함]", na=False, regex=False)
eng_df = df[eng_mask][["회사명", "회사명_정규화", "회사명_영문"]].head(40)

print("=== v1.2 sample (40) ===")
for _, row in eng_df.iterrows():
    print(f"  {row['회사명']:35s} | norm: {row['회사명_정규화']:20s} | eng: {row['회사명_영문']}")

print(f"\n--- total: {eng_mask.sum()} ---")
