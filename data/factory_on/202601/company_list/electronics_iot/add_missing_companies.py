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
TARGET_FILE = os.path.join(BASE_DIR, "company_electronics_iot_employees_10_and_over_F_260310.csv")
SOURCE_FILE = os.path.join(BASE_DIR, "company_electronics_iot_extracted_F_260310.csv")
MISSING_FILE = os.path.join(BASE_DIR, "missing_companies_result.csv")
PRELIM_FILE = os.path.join(BASE_DIR, "preliminary_comany_list_dup_checked_260312_1617F.csv")

# 타임스탬프 출력 폴더
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
df_missing = pd.read_csv(MISSING_FILE, encoding='utf-8-sig')
df_prelim = pd.read_csv(PRELIM_FILE, encoding='utf-8-sig')

print(f"[INFO] Target rows (before): {len(df_target)}")
print(f"[INFO] Source rows: {len(df_source)}")
print(f"[INFO] Missing entries: {len(df_missing)}")

# 기존 기존자료 카운트
elec_before = (df_target['기존자료(가전)'] == '○').sum()
iot_before = (df_target['기존자료(IoT)'] == '○').sum()
print(f"[INFO] Before - 기존자료(가전) O count: {elec_before}")
print(f"[INFO] Before - 기존자료(IoT) O count: {iot_before}")

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

# 소스파일 정규화명 인덱스 구축
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
# 비고 컬럼 확인/추가
# ========================================
if '비고' not in df_target.columns:
    df_target['비고'] = ''
else:
    df_target['비고'] = df_target['비고'].fillna('')

# ========================================
# 유형 B: 파일2에 존재하나 가전/IoT 미표시 -> 기존 행 업데이트
# ========================================
print("\n[STEP 1] Processing Type B: Mark existing companies...")

# 타겟파일 정규화 인덱스
df_target['회사명_정규_temp'] = df_target['회사명'].apply(normalize_name)

type_b_count = 0
type_b_elec = 0
type_b_iot = 0

for _, row in df_missing.iterrows():
    if row['파일2_존재여부'] != 'O':
        continue

    norm_name = row['정규화명']
    category = row['구분']

    # 타겟에서 해당 회사 찾기
    mask = df_target['회사명_정규_temp'] == norm_name
    if mask.sum() == 0:
        # 정규화가 약간 다를 수 있으므로 직접 normalize로 재시도
        norm_name2 = normalize_name(row['사업체명'])
        mask = df_target['회사명_정규_temp'] == norm_name2
    
    if mask.sum() > 0:
        idxs = df_target[mask].index
        for idx in idxs:
            if '가전' in category or '전자' in category:
                if df_target.at[idx, '기존자료(가전)'] != '○':
                    df_target.at[idx, '기존자료(가전)'] = '○'
                    type_b_elec += 1
            if 'IoT' in category:
                if df_target.at[idx, '기존자료(IoT)'] != '○':
                    df_target.at[idx, '기존자료(IoT)'] = '○'
                    type_b_iot += 1
            
            # 비고 업데이트
            existing_note = str(df_target.at[idx, '비고']).strip()
            new_note = '기존자료 표시 누락'
            if existing_note and existing_note != 'nan' and existing_note != '':
                if new_note not in existing_note:
                    df_target.at[idx, '비고'] = existing_note + '; ' + new_note
            else:
                df_target.at[idx, '비고'] = new_note
            type_b_count += 1

print(f"[INFO] Type B processed: {type_b_count} updates")
print(f"[INFO]   - 기존자료(가전) added: {type_b_elec}")
print(f"[INFO]   - 기존자료(IoT) added: {type_b_iot}")

# ========================================
# 유형 A: 파일2에 미존재 -> 소스파일에서 정보 가져와 추가
# ========================================
print("\n[STEP 2] Processing Type A: Add missing companies...")

# 타겟파일 컬럼 목록 (비고, 임시컬럼 제외)
target_cols = [c for c in df_target.columns if c != '회사명_정규_temp']

# 소스파일에 있는 공통 컬럼
source_cols_available = [c for c in df_source.columns if c != '회사명_정규_temp']

# 타겟에만 있는 추가 컬럼 (중복_nid, 종업원규모 등)
target_extra_cols = ['중복_nid', 'KEA(한국전자정보통신산업진흥회)', '한국AI사물인터넷협회', 
                     'KES 2025(한국전자전)', '기존자료(가전)', '기존자료(IoT)', '종업원규모']

new_rows = []
type_a_matched = 0
type_a_unmatched = 0
type_a_under10 = 0
type_a_over300 = 0
type_a_normal = 0

# 이미 처리한 nid 추적 (중복 방지)
processed_nids = set()
processed_names = set()

for _, row in df_missing.iterrows():
    if row['파일2_존재여부'] == 'O':
        continue  # 유형 B는 이미 처리

    company_name = row['사업체명']
    norm_name = row['정규화명']
    category = row['구분']
    
    # 동일 회사 중복 추가 방지 (가전/IoT 양쪽 모두 누락인 경우)
    if norm_name in processed_names:
        # 이미 추가된 행에서 해당 컬럼만 업데이트
        for nr in new_rows:
            if nr.get('회사명_정규_temp', '') == norm_name:
                if '가전' in category or '전자' in category:
                    nr['기존자료(가전)'] = '○'
                if 'IoT' in category:
                    nr['기존자료(IoT)'] = '○'
                break
        continue
    
    # 소스파일에서 매칭
    src_mask = df_source['회사명_정규_temp'] == norm_name
    if src_mask.sum() == 0:
        norm_name2 = normalize_name(company_name)
        src_mask = df_source['회사명_정규_temp'] == norm_name2
    
    if src_mask.sum() > 0:
        # 소스에서 첫 번째 매칭 행 사용
        src_row = df_source[src_mask].iloc[0]
        nid = src_row.get('nid', '')
        
        if nid in processed_nids:
            continue
        processed_nids.add(nid)
        
        # 새 행 생성
        new_row = {}
        for col in target_cols:
            if col in source_cols_available:
                new_row[col] = src_row.get(col, '')
            else:
                new_row[col] = ''
        
        # 종업원합계
        emp_count = src_row.get('종업원합계', 0)
        emp_count = int(emp_count) if not pd.isna(emp_count) else 0
        
        # 종업원규모 산출
        new_row['종업원규모'] = calc_employee_scale(emp_count)
        
        # 기존자료 표시
        if '가전' in category or '전자' in category:
            new_row['기존자료(가전)'] = '○'
        if 'IoT' in category:
            new_row['기존자료(IoT)'] = '○'
        
        # 비고 작성
        if emp_count < 10:
            new_row['비고'] = f'기존자료 누락(종업원 {emp_count}인 - 10인 미만)'
            type_a_under10 += 1
        elif emp_count >= 300:
            new_row['비고'] = f'기존자료 누락(종업원 {emp_count}인 - 300인 이상)'
            type_a_over300 += 1
        else:
            new_row['비고'] = '기존자료 누락(정상 범위)'
            type_a_normal += 1
        
        new_row['회사명_정규_temp'] = norm_name
        new_rows.append(new_row)
        type_a_matched += 1
        processed_names.add(norm_name)
        
    else:
        # 소스파일 매칭 실패 - 최소 정보로 추가
        new_row = {col: '' for col in target_cols}
        new_row['회사명'] = company_name
        new_row['회사명_정규화'] = norm_name
        
        if '가전' in category or '전자' in category:
            new_row['기존자료(가전)'] = '○'
        if 'IoT' in category:
            new_row['기존자료(IoT)'] = '○'
        
        new_row['비고'] = '기존자료 누락(공장DB 미등록)'
        new_row['회사명_정규_temp'] = norm_name
        new_rows.append(new_row)
        type_a_unmatched += 1
        processed_names.add(norm_name)

print(f"[INFO] Type A - Source matched: {type_a_matched}")
print(f"[INFO] Type A - Source unmatched: {type_a_unmatched}")
print(f"[INFO]   - Under 10 employees: {type_a_under10}")
print(f"[INFO]   - Over 300 employees: {type_a_over300}")
print(f"[INFO]   - Normal range (10-299): {type_a_normal}")

# ========================================
# 새 행 추가 및 저장
# ========================================
if new_rows:
    df_new = pd.DataFrame(new_rows)
    # 임시 컬럼 제거
    if '회사명_정규_temp' in df_new.columns:
        df_new = df_new.drop(columns=['회사명_정규_temp'])
    
    df_target = df_target.drop(columns=['회사명_정규_temp'])
    
    # 컬럼 순서 맞추기
    for col in df_target.columns:
        if col not in df_new.columns:
            df_new[col] = ''
    df_new = df_new[df_target.columns]
    
    df_result = pd.concat([df_target, df_new], ignore_index=True)
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

elec_after = (df_result['기존자료(가전)'] == '○').sum()
iot_after = (df_result['기존자료(IoT)'] == '○').sum()
print(f"\n기존자료(가전) O count: {elec_before} -> {elec_after} (+{elec_after - elec_before})")
print(f"기존자료(IoT) O count: {iot_before} -> {iot_after} (+{iot_after - iot_before})")

# 비고 분포
note_dist = df_result['비고'].value_counts()
print("\n[비고 분포]")
for note, cnt in note_dist.items():
    if note and str(note) != 'nan' and str(note).strip() != '':
        print(f"  {note}: {cnt}")

# ========================================
# 저장
# ========================================
output_path = os.path.join(OUTPUT_DIR, "company_electronics_iot_employees_10_and_over_F_260310.csv")
df_result.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\n[INFO] Result saved to: {output_path}")

# 추가된 기업만 따로 저장
if new_rows:
    added_path = os.path.join(OUTPUT_DIR, "added_companies.csv")
    df_new.to_csv(added_path, index=False, encoding='utf-8-sig')
    print(f"[INFO] Added companies saved to: {added_path}")

# 유형 B 업데이트 내역 저장
type_b_records = df_result[df_result['비고'].str.contains('표시 누락', na=False)]
if len(type_b_records) > 0:
    updated_path = os.path.join(OUTPUT_DIR, "updated_mark_companies.csv")
    type_b_records.to_csv(updated_path, index=False, encoding='utf-8-sig')
    print(f"[INFO] Updated mark companies saved to: {updated_path}")

print("\n[DONE]")
