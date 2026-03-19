# -*- coding: utf-8 -*-
import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import re
import os
from datetime import datetime

# ========================================
# 파일 경로 설정
# ========================================
BASE_DIR = r"d:\git_rk\data\factory_on\202601\company_list\electronics_iot"
TARGET_FILE = os.path.join(BASE_DIR, "260318_1614", "company_electronics_iot_employees_10_and_over_F_260318_1614.csv")
KEYWORD_FILE = r"d:\git_rk\project\26_supply_demand\industry_classification\(keyword)home_appliance_IoT\iot_reclassified_cleaned_F(claud).csv"

TIMESTAMP = datetime.now().strftime('%y%m%d_%H%M')
OUTPUT_DIR = os.path.join(BASE_DIR, TIMESTAMP)
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"[INFO] Output directory: {OUTPUT_DIR}")

# ========================================
# 파일 로드
# ========================================
print("[INFO] Loading files...")
df = pd.read_csv(TARGET_FILE, encoding='utf-8-sig')
df_kw = pd.read_csv(KEYWORD_FILE, encoding='utf-8-sig')
print(f"[INFO] Rows: {len(df)}")

# ========================================
# 1. 컬럼명 변경
# ========================================
print("\n[STEP 1] Renaming columns...")

# 순서 주의: 기존자료(전자)를 먼저 바꿔야 기존자료(가전)→기존자료(전자) 충돌 방지
rename_map = {}

# 기존자료(전자) → 기존자료(가전IoT)  (원래 기존자료(IoT)였던 것)
if '기존자료(전자)' in df.columns:
    rename_map['기존자료(전자)'] = '기존자료(가전IoT)'

# 기존자료(가전) → 기존자료(전자)
if '기존자료(가전)' in df.columns:
    rename_map['기존자료(가전)'] = '기존자료(전자)'

# 전자산업 → 업종_전자산업
if '전자산업' in df.columns:
    rename_map['전자산업'] = '업종_전자산업'

# 가전IoT → 업종_가전IoT
if '가전IoT' in df.columns:
    rename_map['가전IoT'] = '업종_가전IoT'

df = df.rename(columns=rename_map)
for old, new in rename_map.items():
    print(f"  '{old}' -> '{new}'")

# ========================================
# 2. 키워드 사전 구축 (재분류용)
# ========================================
print("\n[STEP 2] Building keyword dict for reclassification...")

grade_map = {
    '해당': '예상',
    '해당(예상)': '모호',
    '모호': '모호',
    '비해당': None
}
grade_order = {None: 0, '모호': 1, '예상': 2}

keyword_dict = {}
for _, row in df_kw.iterrows():
    product_name = str(row['정제_생산품목명']).strip()
    new_result = str(row.get('신규_판정결과', '')).strip()
    new_major = str(row.get('신규_대분류', '')).strip()
    new_detail = str(row.get('신규_세부분류', '')).strip()
    if new_result in ('nan', ''):
        new_result = str(row.get('원본_판정결과', '')).strip()
        new_major = str(row.get('원본_대분류', '')).strip()
        new_detail = str(row.get('원본_세부분류', '')).strip()
    if new_major == 'nan': new_major = ''
    if new_detail == 'nan': new_detail = ''
    grade = grade_map.get(new_result, None)
    key = product_name.lower().strip()
    if key and key != 'nan':
        if key in keyword_dict:
            if grade_order.get(keyword_dict[key][0], 0) >= grade_order.get(grade, 0):
                continue
        keyword_dict[key] = (grade, new_major, new_detail, new_result, product_name)

print(f"[INFO] Keyword dict: {len(keyword_dict)} entries")

def classify_product(product_str):
    if pd.isna(product_str) or str(product_str).strip() == '':
        return (None, '')
    products = re.split(r'[,，、/]', str(product_str))
    products = [p.strip() for p in products if p.strip()]
    best_grade = None
    best_reasons = []
    for prod in products:
        prod_lower = prod.lower().strip()
        if not prod_lower: continue
        if prod_lower in keyword_dict:
            g, maj, det, res, orig = keyword_dict[prod_lower]
            if g is not None:
                if grade_order.get(g, 0) > grade_order.get(best_grade, 0):
                    best_grade = g
                cat = f"{maj}/{det}" if maj and det else (maj or det or '미분류')
                best_reasons.append(f"{prod}→{cat}({res})")
            continue
        for kw, (g, maj, det, res, orig) in keyword_dict.items():
            if g is None or len(kw) <= 1: continue
            if kw in prod_lower or (len(prod_lower) >= 2 and prod_lower in kw):
                if grade_order.get(g, 0) > grade_order.get(best_grade, 0):
                    best_grade = g
                cat = f"{maj}/{det}" if maj and det else (maj or det or '미분류')
                r = f"{prod}~{orig}→{cat}({res})"
                if r not in best_reasons: best_reasons.append(r)
                if best_grade == '예상' and len(best_reasons) >= 3: break
        if best_grade == '예상' and len(best_reasons) >= 3: break
    if best_grade is None:
        return (None, '')
    return (best_grade, '; '.join(best_reasons[:3]))

# ========================================
# 3. 가전IoT_예상 재분류
# ========================================
print("\n[STEP 3] Reclassifying...")

total = len(df)
counts = {}

for idx in range(total):
    old_grade = str(df.at[idx, '가전IoT_예상']).strip()
    
    # 기존자료(가전IoT) ○ 여부 (원래 기존자료(IoT))
    iot_prev = str(df.at[idx, '기존자료(가전IoT)']).strip() if '기존자료(가전IoT)' in df.columns else ''
    has_iot_prev = (iot_prev == '○' or iot_prev == 'O')
    
    # KEA(추가) ○ 여부
    kea_val = str(df.at[idx, 'KEA(추가)']).strip() if 'KEA(추가)' in df.columns else ''
    has_kea = (kea_val == '○' or kea_val == 'O')
    
    if old_grade == '확정':
        if has_iot_prev:
            new_grade = '확정(이전조사)'
            old_reason = str(df.at[idx, '예상_근거']).strip()
            if old_reason == 'nan' or old_reason == '':
                new_reason = '기존 가전IoT 조사 참여업체'
            else:
                new_reason = old_reason
        elif has_kea:
            new_grade = '확정(KEA추가)'
            new_reason = 'KEA 회원사 추가'
        else:
            # 확정이었으나 기존자료(가전IoT)도 KEA도 아닌 경우 → 재분류
            product_str = df.at[idx, '생산품'] if '생산품' in df.columns else ''
            kw_grade, kw_reason = classify_product(product_str)
            if kw_grade:
                new_grade = kw_grade
                new_reason = kw_reason
            else:
                new_grade = '자료없음'
                new_reason = ''
    else:
        # 예상, 모호, 자료없음은 유지
        new_grade = old_grade if old_grade != 'nan' else '자료없음'
        new_reason = str(df.at[idx, '예상_근거']).strip()
        if new_reason == 'nan': new_reason = ''
    
    df.at[idx, '가전IoT_예상'] = new_grade
    df.at[idx, '예상_근거'] = new_reason
    
    counts[new_grade] = counts.get(new_grade, 0) + 1
    
    if (idx + 1) % 5000 == 0:
        print(f"  Progress: {idx + 1}/{total}")

print(f"  Progress: {total}/{total}")

# ========================================
# 결과 통계
# ========================================
print("\n" + "=" * 80)
print("[RESULT SUMMARY]")
print("=" * 80)
print(f"Total: {total}\n")

print("가전IoT_예상 분포:")
for grade in ['확정(이전조사)', '확정(KEA추가)', '예상', '모호', '자료없음']:
    cnt = counts.get(grade, 0)
    print(f"  {grade}: {cnt} ({cnt/total*100:.1f}%)")

# 컬럼명 확인
print(f"\n컬럼 목록:")
for i, c in enumerate(df.columns):
    if any(k in c for k in ['기존', '전자', '가전', 'IoT', 'KEA', '예상', '근거', '업종']):
        print(f"  [{i}] {c}")

# 업종_가전IoT 분포
if '업종_가전IoT' in df.columns:
    iot_o = (df['업종_가전IoT'] == 'O').sum()
    print(f"\n업종_가전IoT=O: {iot_o}")

# ========================================
# 저장
# ========================================
output_filename = f"company_electronics_iot_employees_10_and_over_F_{TIMESTAMP}.csv"
output_path = os.path.join(OUTPUT_DIR, output_filename)
df.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\n[INFO] Result saved to: {output_path}")

iot_related = df[df['가전IoT_예상'].str.contains('확정|예상|모호', na=False)]
if len(iot_related) > 0:
    related_path = os.path.join(OUTPUT_DIR, "iot_appliance_related_companies.csv")
    iot_related.to_csv(related_path, index=False, encoding='utf-8-sig')
    print(f"[INFO] IoT related ({len(iot_related)}) saved to: {related_path}")

print("\n[DONE]")
