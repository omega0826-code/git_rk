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
# 파일 경로
# ========================================
BASE_DIR = r"d:\git_rk\data\factory_on\202601\company_list\electronics_iot"
TARGET_FILE = os.path.join(BASE_DIR, "260318_1622", "company_electronics_iot_employees_10_and_over_F_260318_1622.csv")
ELEC_CLASS = r"d:\git_rk\project\26_supply_demand\industry_classification\(classification)electronic.csv"
IOT_CLASS = r"d:\git_rk\project\26_supply_demand\industry_classification\(classification)home_appliance_IoT.csv"

TIMESTAMP = datetime.now().strftime('%y%m%d_%H%M')
OUTPUT_DIR = os.path.join(BASE_DIR, TIMESTAMP)
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"[INFO] Output: {OUTPUT_DIR}")

# ========================================
# 분류표 로드
# ========================================
df_elec = pd.read_csv(ELEC_CLASS, encoding='utf-8-sig')
df_iot = pd.read_csv(IOT_CLASS, encoding='utf-8-sig')

# 전자산업 KSIC5 코드 → 6대분류 매핑
# 할당표 기준:
# ① 전자부품: 262xx (인쇄회로기판, 전자축전기, 전자저항기, 전자코일, 전자감지장치등), 261xx(액정표시장치)
# ② 컴퓨터주변기기: 263xx
# ③ 방송통신장비: 264xx
# ④ 영상음향기기: 265xx, 266xx
# ⑤ 측정제어분석기기: 271xx(의료기기), 272xx
# ⑥ 전기장비: 28xxx
elec_6cat_map = {}
for _, row in df_elec.iterrows():
    code = str(row['KSIC5_code']).strip()
    if not code or code == 'nan': continue
    code_prefix = code[:3]
    if code_prefix in ('261', '262'):
        cat = '전자부품'
    elif code_prefix == '263':
        cat = '컴퓨터주변기기'
    elif code_prefix == '264':
        cat = '방송통신장비'
    elif code_prefix in ('265', '266'):
        cat = '영상음향기기'
    elif code_prefix in ('271', '272'):
        cat = '측정제어분석기기'
    elif code_prefix.startswith('28'):
        cat = '전기장비'
    else:
        cat = '기타'
    elec_6cat_map[code] = cat

print(f"[INFO] 전자산업 분류 코드: {len(elec_6cat_map)}")
# 분포 확인
cat_counts = {}
for c in elec_6cat_map.values():
    cat_counts[c] = cat_counts.get(c, 0) + 1
for c, n in sorted(cat_counts.items()):
    print(f"  {c}: {n}개 코드")

# 전자산업 코드셋
elec_codes = set(elec_6cat_map.keys())

# IoT가전 코드셋
iot_codes = set()
for _, row in df_iot.iterrows():
    code = str(row['KSIC5_code']).strip()
    if code and code != 'nan':
        iot_codes.add(code)
print(f"\n[INFO] IoT가전 분류 코드: {len(iot_codes)}")

# 겹치는 코드
overlap = elec_codes & iot_codes
print(f"[INFO] 전자+IoT 겹치는 코드: {len(overlap)}")

# ========================================
# 타겟 파일 로드
# ========================================
df = pd.read_csv(TARGET_FILE, encoding='utf-8-sig')
print(f"\n[INFO] Target rows: {len(df)}")

# ========================================
# 전자산업 6대분류 재매핑 (업종코드_전체 기준)
# ========================================
print("\n[STEP 1] 전자산업 6대분류 재매핑...")

# 업종_전자산업 컬럼 옆에 전자산업_대분류 컬럼 추가
elec_col = '업종_전자산업'
elec_idx = df.columns.get_loc(elec_col)

# 기존 전자산업_대분류 컬럼이 있으면 제거
if '전자산업_대분류' in df.columns:
    df = df.drop(columns=['전자산업_대분류'])

# 새 컬럼 삽입
df.insert(elec_idx + 1, '전자산업_대분류', '')

def map_elec_category(row):
    """업종코드_전체에서 전자산업 소분류 코드 매칭 → 6대분류"""
    codes_str = str(row.get('업종코드_전체', ''))
    if codes_str == 'nan' or not codes_str.strip():
        return ''
    
    # 쉼표로 분리
    codes = [c.strip() for c in codes_str.split(',')]
    
    # 대표업종도 확인
    rep_code = str(row.get('대표업종', '')).replace('.0', '').strip()
    if rep_code and rep_code != 'nan' and rep_code not in codes:
        codes.insert(0, rep_code)
    
    matched_cats = []
    for code in codes:
        code = code.strip()
        if code in elec_6cat_map:
            cat = elec_6cat_map[code]
            if cat not in matched_cats:
                matched_cats.append(cat)
    
    if not matched_cats:
        return ''
    
    # 대표업종 코드의 분류를 우선
    if rep_code in elec_6cat_map:
        primary = elec_6cat_map[rep_code]
        if primary in matched_cats:
            matched_cats.remove(primary)
            matched_cats.insert(0, primary)
    
    return matched_cats[0] if len(matched_cats) == 1 else '/'.join(matched_cats)

for idx in range(len(df)):
    df.at[idx, '전자산업_대분류'] = map_elec_category(df.iloc[idx])
    if (idx + 1) % 5000 == 0:
        print(f"  Progress: {idx + 1}/{len(df)}")
print(f"  Progress: {len(df)}/{len(df)}")

print("\n전자산업_대분류 분포:")
vc = df['전자산업_대분류'].value_counts(dropna=False)
for v, c in vc.head(15).items():
    label = v if v else '(빈값)'
    print(f"  {label}: {c}")

# ========================================
# IoT가전 업종코드 매칭 → 비고에만 추가
# ========================================
print("\n[STEP 2] IoT가전 업종코드 매칭 → 비고 추가...")

iot_match_count = 0
for idx in range(len(df)):
    codes_str = str(df.at[idx, '업종코드_전체'])
    if codes_str == 'nan' or not codes_str.strip():
        continue
    
    codes = [c.strip() for c in codes_str.split(',')]
    rep_code = str(df.at[idx, '대표업종']).replace('.0', '').strip()
    if rep_code and rep_code != 'nan' and rep_code not in codes:
        codes.insert(0, rep_code)
    
    matched_iot = []
    for code in codes:
        if code in iot_codes:
            # 코드에 해당하는 업종명 찾기
            name_match = df_iot[df_iot['KSIC5_code'].astype(str).str.strip() == code]
            if len(name_match) > 0:
                matched_iot.append(f"{code}({name_match.iloc[0]['KSIC5_name'].strip()})")
            else:
                matched_iot.append(code)
    
    if matched_iot:
        iot_match_count += 1
        existing_bigo = str(df.at[idx, '비고']).strip()
        if existing_bigo == 'nan':
            existing_bigo = ''
        
        iot_note = f"[IoT가전분류] {'; '.join(matched_iot[:3])}"
        if existing_bigo:
            df.at[idx, '비고'] = f"{existing_bigo}; {iot_note}"
        else:
            df.at[idx, '비고'] = iot_note

print(f"  IoT가전 업종코드 매칭: {iot_match_count}건 (비고 추가)")

# ========================================
# 전자산업 규모별 크로스탭
# ========================================
print("\n" + "=" * 80)
print("[RESULT] 전자산업 6대분류 × 규모별 크로스탭")
print("=" * 80)

size_labels = ['10~29인', '30~99인', '100~299인', '300인 이상']
df_10plus = df[df['종업원규모'].isin(size_labels)]

# 전자산업 대분류가 있는 기업만
df_elec_mapped = df_10plus[df_10plus['전자산업_대분류'] != '']

# 복수 분류를 첫 번째 분류로 처리
df_elec_mapped = df_elec_mapped.copy()
df_elec_mapped['전자산업_1차'] = df_elec_mapped['전자산업_대분류'].apply(lambda x: x.split('/')[0] if '/' in str(x) else x)

ct = pd.crosstab(df_elec_mapped['전자산업_1차'], df_elec_mapped['종업원규모'], margins=True)
ct = ct.reindex(columns=['10~29인', '30~99인', '100~299인', '300인 이상', 'All'], fill_value=0)
ct = ct.reindex(['전자부품', '컴퓨터주변기기', '방송통신장비', '영상음향기기', '측정제어분석기기', '전기장비', 'All'], fill_value=0)
print(ct.to_string())

# 할당표 대비
print("\n할당표 대비:")
alloc = {
    '전자부품': [22, 13, 11, 17, 63],
    '컴퓨터주변기기': [12, 10, 4, 1, 27],
    '방송통신장비': [16, 9, 7, 5, 37],
    '영상음향기기': [12, 10, 7, 1, 30],
    '측정제어분석기기': [28, 14, 10, 8, 60],
    '전기장비': [55, 23, 23, 32, 133],
}
print(f"{'대분류':<12} {'할당':>6} {'보유':>6} {'배수':>8}")
for cat, vals in alloc.items():
    target = vals[4]
    actual = int(ct.loc[cat, 'All']) if cat in ct.index else 0
    ratio = f"{actual/target:.1f}×" if target > 0 else '-'
    print(f"  {cat:<12} {target:>5} {actual:>6} {ratio:>8}")

# ========================================
# 저장
# ========================================
output_filename = f"company_electronics_iot_employees_10_and_over_F_{TIMESTAMP}.csv"
output_path = os.path.join(OUTPUT_DIR, output_filename)
df.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\n[INFO] Saved: {output_path}")

print("\n[DONE]")
