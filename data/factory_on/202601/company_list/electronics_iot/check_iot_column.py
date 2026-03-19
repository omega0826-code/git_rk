# -*- coding: utf-8 -*-
import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd

f = r'd:\git_rk\data\factory_on\202601\company_list\electronics_iot\260318_1550\company_electronics_iot_employees_10_and_over_F_260318_1550.csv'
df = pd.read_csv(f, encoding='utf-8-sig')
print(f"Total rows: {len(df)}")

# Target columns
target_cols = [c for c in df.columns if '가전' in str(c) or '예상' in str(c) or '근거' in str(c)]
print(f"\n=== Target columns: {target_cols} ===\n")

for c in target_cols:
    print(f"--- [{c}] ---")
    total = len(df)
    nan_count = df[c].isna().sum()
    empty_str = (df[c].astype(str).str.strip() == '').sum() - nan_count  # pure empty strings
    print(f"  Total: {total}")
    print(f"  NaN: {nan_count}")
    print(f"  Empty string (non-NaN): {empty_str}")
    
    # Value distribution
    vc = df[c].value_counts(dropna=False)
    print(f"  Value distribution (top 10):")
    for val, cnt in vc.head(10).items():
        label = repr(val) if pd.notna(val) else 'NaN'
        print(f"    {label}: {cnt}")
    
    # Check unexpected values for 가전IoT_예상
    if '예상' in c:
        expected = {'상', '중', ''}
        filled = df[df[c].notna() & (df[c].astype(str).str.strip() != '')]
        unexpected = filled[~filled[c].isin(['상', '중'])]
        if len(unexpected) > 0:
            print(f"\n  ** UNEXPECTED VALUES: {len(unexpected)} rows **")
            uvc = unexpected[c].value_counts()
            for val2, cnt2 in uvc.head(10).items():
                print(f"    {repr(val2)}: {cnt2}")
        else:
            print(f"\n  OK: All filled values are '상' or '중' (no unexpected)")
        
        # Summary
        sang = (df[c] == '상').sum()
        jung = (df[c] == '중').sum()
        blank = total - sang - jung
        print(f"\n  Summary: 상={sang}, 중={jung}, 빈값(NaN+blank)={blank}")
    print()

# Cross-check: 가전IoT ○ vs 가전IoT_예상
if '가전IoT' in df.columns and '가전IoT_예상' in df.columns:
    print("=== Cross-check: 가전IoT vs 가전IoT_예상 ===")
    iot_o = df[df['가전IoT'] == 'O']
    iot_not_o = df[df['가전IoT'] != 'O']
    
    print(f"\n가전IoT=O ({len(iot_o)} rows):")
    print(f"  예상 상: {(iot_o['가전IoT_예상'] == '상').sum()}")
    print(f"  예상 중: {(iot_o['가전IoT_예상'] == '중').sum()}")
    blank_o = len(iot_o) - (iot_o['가전IoT_예상'] == '상').sum() - (iot_o['가전IoT_예상'] == '중').sum()
    print(f"  예상 빈: {blank_o}")
    
    print(f"\n가전IoT!=O ({len(iot_not_o)} rows):")
    print(f"  예상 상: {(iot_not_o['가전IoT_예상'] == '상').sum()}")
    print(f"  예상 중: {(iot_not_o['가전IoT_예상'] == '중').sum()}")
    blank_not = len(iot_not_o) - (iot_not_o['가전IoT_예상'] == '상').sum() - (iot_not_o['가전IoT_예상'] == '중').sum()
    print(f"  예상 빈: {blank_not}")

# Check 예상_근거 consistency
if '가전IoT_예상' in df.columns and '예상_근거' in df.columns:
    print("\n=== 예상_근거 consistency check ===")
    has_grade = df[df['가전IoT_예상'].isin(['상', '중'])]
    no_reason = has_grade[has_grade['예상_근거'].isna() | (has_grade['예상_근거'].astype(str).str.strip() == '')]
    print(f"등급 있는데 근거 없음: {len(no_reason)} rows")
    if len(no_reason) > 0:
        print("  ** ERROR: Grade without reason! **")
        for _, row in no_reason.head(5).iterrows():
            print(f"    {row['회사명']} | 예상={row['가전IoT_예상']} | 근거={repr(row['예상_근거'])}")
    
    no_grade = df[~df['가전IoT_예상'].isin(['상', '중'])]
    has_reason = no_grade[no_grade['예상_근거'].notna() & (no_grade['예상_근거'].astype(str).str.strip() != '')]
    print(f"등급 없는데 근거 있음: {len(has_reason)} rows")
    if len(has_reason) > 0:
        print("  ** WARNING: Reason without grade! **")
        for _, row in has_reason.head(5).iterrows():
            print(f"    {row['회사명']} | 예상={repr(row['가전IoT_예상'])} | 근거={row['예상_근거'][:50]}")

print("\n[DONE]")
