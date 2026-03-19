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
TARGET_FILE = os.path.join(BASE_DIR, "260318_1536", "company_electronics_iot_employees_10_and_over_F_260318_1536.csv")
KEYWORD_FILE = r"d:\git_rk\project\26_supply_demand\industry_classification\(keyword)home_appliance_IoT\iot_reclassified_cleaned_F(claud).csv"

TIMESTAMP = datetime.now().strftime('%y%m%d_%H%M')
OUTPUT_DIR = os.path.join(BASE_DIR, TIMESTAMP)
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"[INFO] Output directory: {OUTPUT_DIR}")

# ========================================
# 파일 로드
# ========================================
print("[INFO] Loading files...")
df_target = pd.read_csv(TARGET_FILE, encoding='utf-8-sig')
df_kw = pd.read_csv(KEYWORD_FILE, encoding='utf-8-sig')

print(f"[INFO] Target rows: {len(df_target)}")
print(f"[INFO] Keyword entries: {len(df_kw)}")

# ========================================
# 컬럼명 변경: 기존자료(IoT) → 기존자료(전자)
# ========================================
if '기존자료(IoT)' in df_target.columns:
    df_target = df_target.rename(columns={'기존자료(IoT)': '기존자료(전자)'})
    print("[INFO] '기존자료(IoT)' -> '기존자료(전자)' renamed")

# IoT → 가전IoT
if 'IoT' in df_target.columns:
    df_target = df_target.rename(columns={'IoT': '가전IoT'})
    print("[INFO] 'IoT' -> '가전IoT' renamed")

# ========================================
# 키워드 사전 구축 (4단계 등급: 확정/예상/모호/자료없음)
# ========================================
print("\n[STEP 1] Building keyword dictionary...")

# 판정결과별 등급 매핑
# 해당 → 예상, 해당(예상) → 모호, 모호 → 모호, 비해당 → None
grade_map = {
    '해당': '예상',
    '해당(예상)': '모호',
    '모호': '모호',
    '비해당': None
}
grade_order = {None: 0, '모호': 1, '예상': 2, '확정': 3}

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
    
    # nan 정리
    if new_major == 'nan':
        new_major = ''
    if new_detail == 'nan':
        new_detail = ''
    
    grade = grade_map.get(new_result, None)
    key = product_name.lower().strip()
    
    if key and key != 'nan':
        if key in keyword_dict:
            existing_grade = keyword_dict[key][0]
            if grade_order.get(existing_grade, 0) >= grade_order.get(grade, 0):
                continue
        keyword_dict[key] = (grade, new_major, new_detail, new_result, product_name)

total_kw = len(keyword_dict)
grade_counts = {}
for v in keyword_dict.values():
    g = v[0] if v[0] else 'None'
    grade_counts[g] = grade_counts.get(g, 0) + 1

print(f"[INFO] Keyword dict size: {total_kw}")
for g, cnt in sorted(grade_counts.items()):
    print(f"[INFO]   {g}: {cnt}")

# ========================================
# 가전IoT_예상, 예상_근거 컬럼 추가
# ========================================
print("\n[STEP 2] Adding columns...")

iot_col = '가전IoT'
insert_pos = df_target.columns.get_loc(iot_col) + 1
df_target.insert(insert_pos, '가전IoT_예상', '')
df_target.insert(insert_pos + 1, '예상_근거', '')
print(f"[INFO] Inserted '가전IoT_예상' at index {insert_pos}")
print(f"[INFO] Inserted '예상_근거' at index {insert_pos + 1}")

# 비고 컬럼 확인
if '비고' not in df_target.columns:
    df_target['비고'] = ''

# ========================================
# 생산품 기반 매칭 함수
# ========================================
def classify_product(product_str):
    """생산품 문자열 → (등급, 근거)"""
    if pd.isna(product_str) or str(product_str).strip() == '':
        return (None, '')
    
    products = re.split(r'[,，、/]', str(product_str))
    products = [p.strip() for p in products if p.strip()]
    
    best_grade = None
    best_reasons = []
    
    for prod in products:
        prod_lower = prod.lower().strip()
        if not prod_lower:
            continue
        
        # 1) 정확 매칭
        if prod_lower in keyword_dict:
            grade, major, detail, result, orig_kw = keyword_dict[prod_lower]
            if grade is not None:
                if grade_order.get(grade, 0) > grade_order.get(best_grade, 0):
                    best_grade = grade
                cat_str = f"{major}/{detail}" if major and detail else (major or detail or '미분류')
                best_reasons.append(f"{prod}→{cat_str}({result})")
            continue
        
        # 2) 부분문자열 매칭
        for kw, (grade, major, detail, result, orig_kw) in keyword_dict.items():
            if grade is None:
                continue
            if len(kw) <= 1:
                continue
            
            if kw in prod_lower or (len(prod_lower) >= 2 and prod_lower in kw):
                if grade_order.get(grade, 0) > grade_order.get(best_grade, 0):
                    best_grade = grade
                cat_str = f"{major}/{detail}" if major and detail else (major or detail or '미분류')
                reason = f"{prod}~{orig_kw}→{cat_str}({result})"
                if reason not in best_reasons:
                    best_reasons.append(reason)
                if best_grade == '예상' and len(best_reasons) >= 3:
                    break
        
        if best_grade == '예상' and len(best_reasons) >= 3:
            break
    
    if best_grade is None:
        return (None, '')
    
    return (best_grade, '; '.join(best_reasons[:3]))

# ========================================
# 전체 데이터 처리
# ========================================
print("\n[STEP 3] Processing...")

total = len(df_target)
counts = {'확정': 0, '예상': 0, '모호': 0, '자료없음': 0}

for idx in range(total):
    iot_val = df_target.at[idx, iot_col]
    product_str = df_target.at[idx, '생산품'] if '생산품' in df_target.columns else ''
    
    # 키워드 매칭
    kw_grade, kw_reason = classify_product(product_str)
    
    # 최종 등급 결정
    if str(iot_val).strip() == 'O':
        # 기존 IoT 조사 참여업체 → 확정
        final_grade = '확정'
        if kw_reason:
            final_reason = f"IoT조사참여 + {kw_reason}"
        else:
            final_reason = 'IoT조사참여업체'
    elif kw_grade == '예상':
        final_grade = '예상'
        final_reason = kw_reason
    elif kw_grade == '모호':
        final_grade = '모호'
        final_reason = kw_reason
    else:
        final_grade = '자료없음'
        final_reason = ''
    
    df_target.at[idx, '가전IoT_예상'] = final_grade
    df_target.at[idx, '예상_근거'] = final_reason
    counts[final_grade] += 1
    
    if (idx + 1) % 5000 == 0:
        print(f"  Progress: {idx + 1}/{total} ({(idx+1)/total*100:.1f}%)")

print(f"  Progress: {total}/{total} (100.0%)")

# ========================================
# 결과 통계
# ========================================
print("\n" + "=" * 80)
print("[RESULT SUMMARY]")
print("=" * 80)
print(f"Total: {total}")
print(f"\n가전IoT_예상 분포:")
for grade, cnt in counts.items():
    print(f"  {grade}: {cnt} ({cnt/total*100:.1f}%)")

# 가전IoT vs 가전IoT_예상 교차
print(f"\n[교차 검증]")
for iot_val in ['O', '(non-O)']:
    if iot_val == 'O':
        subset = df_target[df_target[iot_col] == 'O']
    else:
        subset = df_target[df_target[iot_col] != 'O']
    print(f"  가전IoT={iot_val} ({len(subset)} rows):")
    for g in ['확정', '예상', '모호', '자료없음']:
        cnt = (subset['가전IoT_예상'] == g).sum()
        print(f"    {g}: {cnt}")

# 샘플 출력
for g in ['확정', '예상', '모호']:
    sample = df_target[df_target['가전IoT_예상'] == g].head(3)
    print(f"\n[SAMPLE] {g} 등급:")
    for _, row in sample.iterrows():
        prod = str(row.get('생산품', ''))[:35]
        reason = str(row.get('예상_근거', ''))[:55]
        print(f"  {row['회사명']} | {prod} | {reason}")

# ========================================
# 저장
# ========================================
output_filename = f"company_electronics_iot_employees_10_and_over_F_{TIMESTAMP}.csv"
output_path = os.path.join(OUTPUT_DIR, output_filename)
df_target.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\n[INFO] Result saved to: {output_path}")

# 가전IoT 관련 기업 (확정+예상+모호)
iot_related = df_target[df_target['가전IoT_예상'].isin(['확정', '예상', '모호'])]
if len(iot_related) > 0:
    related_path = os.path.join(OUTPUT_DIR, "iot_appliance_related_companies.csv")
    iot_related.to_csv(related_path, index=False, encoding='utf-8-sig')
    print(f"[INFO] IoT related ({len(iot_related)} companies) saved to: {related_path}")

print("\n[DONE]")
