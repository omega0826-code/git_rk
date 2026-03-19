# -*- coding: utf-8 -*-
import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import re

file1 = r"d:\git_rk\data\factory_on\202601\company_list\electronics_iot\preliminary_comany_list_dup_checked_260312_1617F.csv"
file2 = r"d:\git_rk\data\factory_on\202601\company_list\electronics_iot\company_electronics_iot_employees_10_and_over_F_260310.csv"

print("[INFO] Loading files...")
df1 = pd.read_csv(file1, encoding='utf-8-sig')
df2 = pd.read_csv(file2, encoding='utf-8-sig')
print(f"[INFO] File1 rows: {len(df1)}, File2 rows: {len(df2)}")

# ========================================
# 회사명 정규화 먼저 수행
# ========================================

# ========================================
# 비교: 사업자등록번호 기반  
# ========================================
def normalize_brn(val):
    """사업자등록번호 정규화"""
    if pd.isna(val):
        return None
    s = str(val).strip().replace('-', '')
    s = re.sub(r'[^0-9]', '', s)
    if len(s) == 0:
        return None
    return s

# File1 사업자등록번호 정규화
df1['사업자등록번호_정규'] = df1['사업자등록번호'].apply(normalize_brn)

# File2는 사업자등록번호가 없으므로 회사명으로 비교
# File2의 회사명 정규화
def normalize_name(val):
    if pd.isna(val):
        return ''
    s = str(val).strip()
    # 공백 제거
    s = re.sub(r'\s+', '', s)
    # 괄호 안 내용, (주), (유), ㈜ 등 정규화
    s = s.replace('㈜', '(주)')
    s = s.replace('(주)', '').replace('(유)', '').replace('주식회사', '')
    s = s.replace('(합)', '').replace('(사)', '')
    # 공장명 등 suffix 제거
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

# File1 회사명 정규화
df1['회사명_정규'] = df1['사업체명'].apply(normalize_name)
# File2 회사명 정규화  
df2['회사명_정규'] = df2['회사명'].apply(normalize_name)

# File2의 모든 정규화된 회사명 set
f2_names = set(df2['회사명_정규'].values)
f2_names_with_mark_elec = set(df2[df2['기존자료(가전)'] == '○']['회사명_정규'].values)
f2_names_with_mark_iot = set(df2[df2['기존자료(IoT)'] == '○']['회사명_정규'].values)

# Filtered dataframes (after normalization so they have the column)
df1_elec = df1[df1['기존자료(전자)'] == '○'].copy()
df1_iot = df1[df1['기존자료(IoT)'] == '○'].copy()

print(f"\n[INFO] File1 - 기존자료(전자/가전) marked: {len(df1_elec)}")
print(f"[INFO] File1 - 기존자료(IoT) marked: {len(df1_iot)}")
print(f"[INFO] File2 - 기존자료(가전) marked: {len(f2_names_with_mark_elec)} (unique names)")
print(f"[INFO] File2 - 기존자료(IoT) marked: {len(f2_names_with_mark_iot)} (unique names)")

# ========================================
# 1. 기존자료(전자/가전) 비교: 파일1에는 ○가 있지만 파일2에는 ○가 없는 업체
# ========================================
print("\n" + "=" * 80)
print("[1] 기존자료(전자/가전) - 파일1에 O가 있지만 파일2에 누락된 업체")
print("=" * 80)

missing_elec = []
for idx, row in df1_elec.iterrows():
    name_norm = row['회사명_정규']
    company_name = row['사업체명']
    elec_type = row.get('기존(전자유형)', '')
    
    # 파일2에서 해당 회사명이 있는지 확인
    in_f2 = name_norm in f2_names
    marked_in_f2 = name_norm in f2_names_with_mark_elec
    
    if not marked_in_f2:
        missing_elec.append({
            '사업체명': company_name,
            '정규화명': name_norm,
            '유형': elec_type,
            '시도': row.get('시도', ''),
            '생산품목': str(row.get('생산품목', ''))[:50],
            '파일2_존재여부': 'O' if in_f2 else 'X',
            '비고': '파일2에 존재하나 가전 미표시' if in_f2 else '파일2에 미존재'
        })

print(f"\n누락 업체 수: {len(missing_elec)}")
for i, m in enumerate(missing_elec, 1):
    print(f"  {i:3d}. [{m['파일2_존재여부']}] {m['사업체명']} | {m['유형']} | {m['시도']} | {m['비고']}")

# ========================================
# 2. 기존자료(IoT) 비교
# ========================================
print("\n" + "=" * 80)
print("[2] 기존자료(IoT) - 파일1에 O가 있지만 파일2에 누락된 업체")
print("=" * 80)

missing_iot = []
for idx, row in df1_iot.iterrows():
    name_norm = row['회사명_정규']
    company_name = row['사업체명']
    iot_type = row.get('기존(IoT유형)', '')
    
    in_f2 = name_norm in f2_names
    marked_in_f2 = name_norm in f2_names_with_mark_iot
    
    if not marked_in_f2:
        missing_iot.append({
            '사업체명': company_name,
            '정규화명': name_norm,
            '유형': iot_type,
            '시도': row.get('시도', ''),
            '생산품목': str(row.get('생산품목', ''))[:50],
            '파일2_존재여부': 'O' if in_f2 else 'X',
            '비고': '파일2에 존재하나 IoT 미표시' if in_f2 else '파일2에 미존재'
        })

print(f"\n누락 업체 수: {len(missing_iot)}")
for i, m in enumerate(missing_iot, 1):
    print(f"  {i:3d}. [{m['파일2_존재여부']}] {m['사업체명']} | {m['유형']} | {m['시도']} | {m['비고']}")

# ========================================
# 3. Summary
# ========================================
print("\n" + "=" * 80)
print("[SUMMARY]")
print("=" * 80)

# 가전 누락 분류
elec_exist_no_mark = [m for m in missing_elec if m['파일2_존재여부'] == 'O']
elec_not_exist = [m for m in missing_elec if m['파일2_존재여부'] == 'X']
print(f"\n[가전/전자] 총 누락: {len(missing_elec)}건")
print(f"  - 파일2에 존재하나 가전 미표시: {len(elec_exist_no_mark)}건")
print(f"  - 파일2에 미존재: {len(elec_not_exist)}건")

# IoT 누락 분류
iot_exist_no_mark = [m for m in missing_iot if m['파일2_존재여부'] == 'O']
iot_not_exist = [m for m in missing_iot if m['파일2_존재여부'] == 'X']
print(f"\n[IoT] 총 누락: {len(missing_iot)}건")
print(f"  - 파일2에 존재하나 IoT 미표시: {len(iot_exist_no_mark)}건")
print(f"  - 파일2에 미존재: {len(iot_not_exist)}건")

# 파일2 미존재 업체 상세 (가전)
if elec_not_exist:
    print(f"\n--- [가전] 파일2에 아예 없는 업체 ({len(elec_not_exist)}건) ---")
    for i, m in enumerate(elec_not_exist, 1):
        print(f"  {i}. {m['사업체명']} | {m['유형']} | {m['시도']}")

# 파일2 미존재 업체 상세 (IoT)
if iot_not_exist:
    print(f"\n--- [IoT] 파일2에 아예 없는 업체 ({len(iot_not_exist)}건) ---")
    for i, m in enumerate(iot_not_exist, 1):
        print(f"  {i}. {m['사업체명']} | {m['유형']} | {m['시도']}")

# CSV로 결과 저장
output_path = r"d:\git_rk\data\factory_on\202601\company_list\electronics_iot\missing_companies_result.csv"

all_missing = []
for m in missing_elec:
    m_copy = m.copy()
    m_copy['구분'] = '기존자료(가전/전자)'
    all_missing.append(m_copy)
for m in missing_iot:
    m_copy = m.copy()
    m_copy['구분'] = '기존자료(IoT)'
    all_missing.append(m_copy)

if all_missing:
    df_result = pd.DataFrame(all_missing)
    df_result = df_result[['구분', '사업체명', '정규화명', '유형', '시도', '생산품목', '파일2_존재여부', '비고']]
    df_result.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n[INFO] Results saved to: {output_path}")

print("\n[DONE]")
