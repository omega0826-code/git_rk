# -*- coding: utf-8 -*-
"""
가전IoT_예상 컬럼 재분류 스크립트
- KEA(추가) 또는 기존자료(가전IoT)에 O가 있는 경우 -> 확정
- 그외는 이전에 검토한 내용(키워드 기반 분류 결과) 유지
"""
import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import os
from datetime import datetime

# ========================================
# 파일 경로 설정
# ========================================
BASE_DIR = r"d:\git_rk\data\factory_on\202601\company_list\electronics_iot"
INPUT_DIR = os.path.join(BASE_DIR, "260318_1634")
INPUT_FILE = os.path.join(INPUT_DIR, "company_electronics_iot_employees_10_and_over_F_260318_1634.csv")

TIMESTAMP = datetime.now().strftime('%y%m%d_%H%M')
OUTPUT_DIR = os.path.join(BASE_DIR, TIMESTAMP)
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"[INFO] Output directory: {OUTPUT_DIR}")

# ========================================
# 파일 로드
# ========================================
print("[INFO] Loading CSV...")
df = pd.read_csv(INPUT_FILE, encoding='utf-8-sig')
total = len(df)
print(f"[INFO] Total rows: {total}")

# ========================================
# 재분류 전 현황
# ========================================
print("\n[BEFORE] 가전IoT_예상 분포:")
before_counts = df['가전IoT_예상'].value_counts(dropna=False)
for val, cnt in before_counts.items():
    label = val if pd.notna(val) else 'NaN'
    print(f"  {label}: {cnt}")

# ========================================
# 재분류 로직
# ========================================
print("\n[STEP] Reclassifying...")

change_log = []  # 변경 이력 기록

for idx in range(total):
    old_grade = str(df.at[idx, '가전IoT_예상']).strip() if pd.notna(df.at[idx, '가전IoT_예상']) else ''
    old_reason = str(df.at[idx, '예상_근거']).strip() if pd.notna(df.at[idx, '예상_근거']) else ''
    if old_reason == 'nan':
        old_reason = ''

    # KEA(추가) 여부
    kea_val = str(df.at[idx, 'KEA(추가)']).strip() if pd.notna(df.at[idx, 'KEA(추가)']) else ''
    has_kea = (kea_val in ['O', '○'])

    # 기존자료(가전IoT) 여부
    iot_val = str(df.at[idx, '기존자료(가전IoT)']).strip() if pd.notna(df.at[idx, '기존자료(가전IoT)']) else ''
    has_iot = (iot_val in ['O', '○'])

    new_grade = old_grade
    new_reason = old_reason

    # 규칙 1: KEA(추가) O -> 확정(KEA추가)
    if has_kea:
        if '확정' not in old_grade:
            new_grade = '확정(KEA추가)'
            new_reason = 'KEA 회원사 추가'
            change_log.append({
                'nid': df.at[idx, 'nid'],
                'company': df.at[idx, '회사명'],
                'old_grade': old_grade,
                'new_grade': new_grade,
                'trigger': 'KEA(추가)=O'
            })

    # 규칙 2: 기존자료(가전IoT) O -> 확정(이전조사)
    elif has_iot:
        if '확정' not in old_grade:
            new_grade = '확정(이전조사)'
            if not old_reason:
                new_reason = '기존 가전IoT 조사 참여업체'
            change_log.append({
                'nid': df.at[idx, 'nid'],
                'company': df.at[idx, '회사명'],
                'old_grade': old_grade,
                'new_grade': new_grade,
                'trigger': '기존자료(가전IoT)=O'
            })

    # 규칙 3: 그외 -> 기존 분류 유지
    # (예상, 모호, 자료없음 등은 그대로)

    df.at[idx, '가전IoT_예상'] = new_grade
    df.at[idx, '예상_근거'] = new_reason

    if (idx + 1) % 5000 == 0:
        print(f"  Progress: {idx + 1}/{total}")

print(f"  Progress: {total}/{total}")

# ========================================
# 재분류 후 현황
# ========================================
print("\n[AFTER] 가전IoT_예상 분포:")
after_counts = df['가전IoT_예상'].value_counts(dropna=False)
for val, cnt in after_counts.items():
    label = val if pd.notna(val) else 'NaN'
    print(f"  {label}: {cnt}")

# 변경 건수
print(f"\n[CHANGES] Total changes: {len(change_log)}")
if len(change_log) > 0:
    print("\n[CHANGE DETAIL] (max 20):")
    for i, ch in enumerate(change_log[:20]):
        print(f"  {ch['nid']} | {ch['company']} | {ch['old_grade']} -> {ch['new_grade']} | {ch['trigger']}")
    if len(change_log) > 20:
        print(f"  ... (+{len(change_log) - 20} more)")

# 교차 검증: KEA/기존자료 O인데 미확정이 0건인지 확인
kea_o = df['KEA(추가)'].fillna('').str.strip().isin(['O', '○'])
iot_o = df['기존자료(가전IoT)'].fillna('').str.strip().isin(['O', '○'])
confirmed = df['가전IoT_예상'].fillna('').str.contains('확정')
still_unconfirmed = (kea_o | iot_o) & ~confirmed
print(f"\n[VERIFY] KEA/기존자료 O but unconfirmed: {still_unconfirmed.sum()} (should be 0)")

# ========================================
# 저장
# ========================================
output_filename = f"company_electronics_iot_employees_10_and_over_F_{TIMESTAMP}.csv"
output_path = os.path.join(OUTPUT_DIR, output_filename)
df.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\n[INFO] Result saved to: {output_path}")

# 변경 이력 저장
if len(change_log) > 0:
    change_df = pd.DataFrame(change_log)
    change_path = os.path.join(OUTPUT_DIR, f"change_log_{TIMESTAMP}.csv")
    change_df.to_csv(change_path, index=False, encoding='utf-8-sig')
    print(f"[INFO] Change log saved to: {change_path}")

# IoT 관련 기업 (확정+예상+모호) 추출
iot_related = df[df['가전IoT_예상'].str.contains('확정|예상|모호', na=False)]
if len(iot_related) > 0:
    related_path = os.path.join(OUTPUT_DIR, "iot_appliance_related_companies.csv")
    iot_related.to_csv(related_path, index=False, encoding='utf-8-sig')
    print(f"[INFO] IoT related ({len(iot_related)} companies) saved to: {related_path}")

print("\n[DONE]")
