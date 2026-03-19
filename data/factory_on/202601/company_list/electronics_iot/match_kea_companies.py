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
TARGET_FILE = os.path.join(BASE_DIR, "260318_1524", "company_electronics_iot_employees_10_and_over_F_260318_1524.csv")
SOURCE_FILE = os.path.join(BASE_DIR, "company_electronics_iot_extracted_F_260310.csv")
KEA_FILE = r"d:\git_rk\project\26_supply_demand\industry_classification\(KEA) home_appliance_IoT.csv"

TIMESTAMP = datetime.now().strftime('%y%m%d_%H%M')
OUTPUT_DIR = os.path.join(BASE_DIR, TIMESTAMP)
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"[INFO] Output directory: {OUTPUT_DIR}")

# ========================================
# 파일 로드
# ========================================
print("[INFO] Loading files...")
df_target = pd.read_csv(TARGET_FILE, encoding='utf-8-sig')
df_source = pd.read_csv(SOURCE_FILE, encoding='utf-8-sig')
df_kea = pd.read_csv(KEA_FILE, encoding='utf-8-sig')

print(f"[INFO] Target rows (before): {len(df_target)}")
print(f"[INFO] Source rows: {len(df_source)}")
print(f"[INFO] KEA entries: {len(df_kea)}")

# ========================================
# 회사명 정규화 함수
# ========================================
def normalize_name(val):
    if pd.isna(val):
        return ''
    s = str(val).strip()
    s = re.sub(r'\s+', '', s)
    s = s.replace('\u321c', '(주)')  # ㈜
    s = s.replace('(주)', '').replace('(유)', '').replace('주식회사', '')
    s = s.replace('(합)', '').replace('(사)', '')
    for suf in ['1공장', '2공장', '3공장', '본사', '공장', '서울사무소', '천안공장',
                '광주공장', '인동공장', '동해공장', '구미공장', '경주공장', '양산공장',
                '천안사업장', '울산사업장', '동탄사업장', '문지동사업장', '평택디지털파크',
                '진량공장', '성산공장', '안산공장', '서탄공장', '안산1공장',
                '광주1,2공장', '충주공장', '스마트센타', '지점', '세종사업장',
                '동탄점', '창원공장', '전주공장', '문경공장', '플렉스타워',
                '진해구', '구미지점']:
        s = s.replace(suf, '')
    s = s.strip()
    return s

# ========================================
# KEA 기업 정규화 및 중복 제거
# ========================================
df_kea['기업명_정규'] = df_kea['기업명'].apply(normalize_name)
# 중복 제거 (네트워크코리아, 다원디엔에스 등)
kea_unique = df_kea.drop_duplicates(subset='기업명_정규')
print(f"[INFO] KEA unique companies: {len(kea_unique)}")

# 소스파일 정규화
df_source['회사명_정규_temp'] = df_source['회사명'].apply(normalize_name)

# 종업원규모 산출 함수
def calc_employee_scale(n):
    if pd.isna(n):
        return ''
    n = int(n)
    if n < 10:
        return '10인 미만'
    elif n < 30:
        return '10~29인'
    elif n < 100:
        return '30~99인'
    elif n < 300:
        return '100~299인'
    else:
        return '300인 이상'

# ========================================
# KEA(추가) 컬럼 생성 - KEA(한국전자정보통신산업진흥회) 옆
# ========================================
kea_col_name = 'KEA(한국전자정보통신산업진흥회)'
new_col_name = 'KEA(추가)'

# 기존 KEA 컬럼 위치 찾기
kea_col_idx = df_target.columns.get_loc(kea_col_name)
print(f"[INFO] KEA column index: {kea_col_idx}")

# KEA(추가) 컬럼을 KEA 기존 컬럼 바로 뒤에 삽입
df_target.insert(kea_col_idx + 1, new_col_name, '')

# 비고 컬럼 확인
if '비고' not in df_target.columns:
    df_target['비고'] = ''
else:
    df_target['비고'] = df_target['비고'].fillna('')

# ========================================
# 1단계: 타겟파일에서 KEA 기업 매칭
# ========================================
print("\n[STEP 1] Matching KEA companies in target file...")

# 타겟 정규화
df_target['회사명_정규_temp'] = df_target['회사명'].apply(normalize_name)

matched_in_target = 0
not_in_target = []

for _, kea_row in kea_unique.iterrows():
    kea_norm = kea_row['기업명_정규']
    kea_name = kea_row['기업명']
    
    mask = df_target['회사명_정규_temp'] == kea_norm
    if mask.sum() > 0:
        df_target.loc[mask, new_col_name] = '○'
        matched_in_target += 1
    else:
        not_in_target.append(kea_row)

print(f"[INFO] Matched in target: {matched_in_target}")
print(f"[INFO] Not in target: {len(not_in_target)}")

# ========================================
# 2단계: 타겟에 없는 KEA 기업 → 소스에서 가져와 추가
# ========================================
print("\n[STEP 2] Adding missing KEA companies from source...")

target_cols = [c for c in df_target.columns if c != '회사명_정규_temp']
new_rows = []
src_matched = 0
src_unmatched = 0
under10 = 0
over300 = 0

for kea_row in not_in_target:
    kea_norm = kea_row['기업명_정규']
    kea_name = kea_row['기업명']
    kea_product = kea_row.get('주요 제품', '')
    kea_area = kea_row.get('IoT 가전 연관 영역', '')
    
    # 소스에서 매칭
    src_mask = df_source['회사명_정규_temp'] == kea_norm
    
    if src_mask.sum() > 0:
        src_row = df_source[src_mask].iloc[0]
        new_row = {}
        for col in target_cols:
            if col in df_source.columns:
                new_row[col] = src_row.get(col, '')
            else:
                new_row[col] = ''
        
        emp_count = src_row.get('종업원합계', 0)
        emp_count = int(emp_count) if not pd.isna(emp_count) else 0
        new_row['종업원규모'] = calc_employee_scale(emp_count)
        new_row[new_col_name] = '○'
        
        # 비고 작성
        note_parts = ['KEA 목록 추가']
        if emp_count < 10:
            note_parts.append(f'종업원 {emp_count}인 - 10인 미만')
            under10 += 1
        elif emp_count >= 300:
            note_parts.append(f'종업원 {emp_count}인 - 300인 이상')
            over300 += 1
        new_row['비고'] = '(' + ', '.join(note_parts) + ')'
        
        new_rows.append(new_row)
        src_matched += 1
    else:
        # 소스 매칭 실패
        new_row = {col: '' for col in target_cols}
        new_row['회사명'] = kea_name
        new_row['회사명_정규화'] = kea_norm
        new_row[new_col_name] = '○'
        new_row['비고'] = '(KEA 목록 추가, 공장DB 미등록)'
        new_rows.append(new_row)
        src_unmatched += 1
    
    print(f"  {'[SRC O]' if src_mask.sum() > 0 else '[SRC X]'} {kea_name} ({kea_norm})")

print(f"\n[INFO] Source matched: {src_matched}")
print(f"[INFO] Source unmatched: {src_unmatched}")
print(f"[INFO]   - Under 10 employees: {under10}")
print(f"[INFO]   - Over 300 employees: {over300}")

# ========================================
# 새 행 추가 및 저장
# ========================================
if new_rows:
    df_new = pd.DataFrame(new_rows)
    if '회사명_정규_temp' in df_new.columns:
        df_new = df_new.drop(columns=['회사명_정규_temp'])
    
    df_target_clean = df_target.drop(columns=['회사명_정규_temp'])
    
    for col in df_target_clean.columns:
        if col not in df_new.columns:
            df_new[col] = ''
    df_new = df_new[df_target_clean.columns]
    
    df_result = pd.concat([df_target_clean, df_new], ignore_index=True)
else:
    df_result = df_target.drop(columns=['회사명_정규_temp'])

# ========================================
# 결과 통계
# ========================================
print("\n" + "=" * 80)
print("[RESULT SUMMARY]")
print("=" * 80)
print(f"원본 행 수: {len(df_target)}")
print(f"추가 행 수: {len(new_rows)}")
print(f"최종 행 수: {len(df_result)}")

kea_total = (df_result[new_col_name] == '○').sum()
print(f"\nKEA(추가) ○ count: {kea_total}")
print(f"KEA 고유기업 수: {len(kea_unique)}")
print(f"매칭률: {kea_total}/{len(kea_unique)} ({kea_total/len(kea_unique)*100:.1f}%)")

# 비고 분포
note_dist = df_result['비고'].value_counts()
kea_notes = {k: v for k, v in note_dist.items() if 'KEA' in str(k)}
if kea_notes:
    print("\n[KEA 관련 비고 분포]")
    for note, cnt in kea_notes.items():
        print(f"  {note}: {cnt}")

# ========================================
# 저장
# ========================================
output_filename = f"company_electronics_iot_employees_10_and_over_F_{TIMESTAMP}.csv"
output_path = os.path.join(OUTPUT_DIR, output_filename)
df_result.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\n[INFO] Result saved to: {output_path}")

if new_rows:
    added_path = os.path.join(OUTPUT_DIR, "kea_added_companies.csv")
    df_new.to_csv(added_path, index=False, encoding='utf-8-sig')
    print(f"[INFO] KEA added companies saved to: {added_path}")

print("\n[DONE]")
