# -*- coding: utf-8 -*-
"""
업종_raw data.csv 대분류 매핑 스크립트 (v4)
- 69행 이후 s1/s2가 분리된 쌍(pair) 행을 병합 후 매핑
"""
import pandas as pd
import os

os.chdir(r'd:\git_rk\project\25_121_ulsan\CSV')

# ============================================================
# 1. 파일 읽기
# ============================================================
raw = pd.read_csv('업종_raw data.csv', encoding='utf-8-sig', dtype=str)
daebun = pd.read_csv('표준산업분류_대분류.csv', encoding='utf-8', dtype=str)
raw1 = pd.read_csv('업종#1_raw data.csv', encoding='utf-8', dtype=str)

# 정리
for df in [raw, daebun, raw1]:
    df.columns = df.columns.str.strip()
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].str.strip().str.replace('\r', '', regex=False).str.replace('\u3000', '', regex=False)

# s4, s4_name 칼럼 제거 (이전 실행 결과 초기화)
for col in ['s4', 's4_name']:
    if col in raw.columns:
        raw.drop(columns=[col], inplace=True)

# 빈행 제거
raw = raw.dropna(how='all').reset_index(drop=True)

print(f"원본 행 수: {len(raw)}")
print(f"칼럼: {list(raw.columns)}")

# ============================================================
# 2. 69행 이후 분리된 행 병합 (s1만 있는 행 + s2만 있는 행 -> 하나로)
# ============================================================
# 1~68행: 중분류 세부 (s1,s2,s3,s3_nm 모두 있음)
# 69행~: 대분류/통합 항목 (s1만 있는 행과 s2만 있는 행이 번갈아)

# 중분류 세부 부분 (s3가 있는 행)
detail_mask = raw['s3'].notna() & (raw['s3'] != '')
detail_rows = raw[detail_mask].copy()

# 대분류/통합 부분 (s3가 없는 행)
summary_rows = raw[~detail_mask].copy()

print(f"\n세부행 (s3 있음): {len(detail_rows)}행")
print(f"통합행 (s3 없음): {len(summary_rows)}행")

# 통합행 병합: s1만 있는 행 + 다음 s2만 있는 행
merged_summary = []
i = 0
rows_list = summary_rows.values.tolist()
cols = summary_rows.columns.tolist()

while i < len(rows_list):
    row = dict(zip(cols, rows_list[i]))
    s1_val = str(row.get('s1', '')).strip() if pd.notna(row.get('s1')) and str(row.get('s1', '')).strip() != 'nan' else ''
    s2_val = str(row.get('s2', '')).strip() if pd.notna(row.get('s2')) and str(row.get('s2', '')).strip() != 'nan' else ''
    
    if s1_val and not s2_val:
        # s1만 있는 행 -> 다음 행에서 s2 가져오기
        if i + 1 < len(rows_list):
            next_row = dict(zip(cols, rows_list[i+1]))
            next_s2 = str(next_row.get('s2', '')).strip() if pd.notna(next_row.get('s2')) and str(next_row.get('s2', '')).strip() != 'nan' else ''
            next_s1 = str(next_row.get('s1', '')).strip() if pd.notna(next_row.get('s1')) and str(next_row.get('s1', '')).strip() != 'nan' else ''
            
            if next_s2 and not next_s1:
                # 병합
                row['s2'] = next_s2
                merged_summary.append(row)
                i += 2
                continue
        merged_summary.append(row)
        i += 1
    elif s1_val and s2_val:
        # 둘 다 있으면 그대로
        merged_summary.append(row)
        i += 1
    else:
        # s1도 s2도 없는 행 스킵
        i += 1

summary_df = pd.DataFrame(merged_summary)
print(f"병합 후 통합행: {len(summary_df)}행")

# 전체 데이터 재조합
raw_merged = pd.concat([detail_rows, summary_df], ignore_index=True)
print(f"최종 행 수: {len(raw_merged)}")

# ============================================================
# 3. 중분류->대분류 매핑 테이블
# ============================================================
jung_to_dae = {}
code_ranges = {
    'A': ['01','02','03'],
    'B': ['05','06','07','08'],
    'C': [str(i).zfill(2) for i in range(10,35)],
    'D': ['35'],
    'E': ['36','37','38','39'],
    'F': ['41','42'],
    'G': ['45','46','47'],
    'H': ['49','50','51','52'],
    'I': ['55','56'],
    'J': ['58','59','60','61','62','63'],
    'K': ['64','65','66'],
    'L': ['68'],
    'M': ['70','71','72','73'],
    'N': ['74','75','76'],
    'O': ['84'],
    'P': ['85'],
    'Q': ['86','87'],
    'R': ['90','91'],
    'S': ['94','95','96'],
    'T': ['97','98'],
    'U': ['99']
}
for dae_code, jung_codes in code_ranges.items():
    for jc in jung_codes:
        jung_to_dae[jc] = dae_code

dae_name_map = dict(zip(daebun['a1'], daebun['a3']))

# 업종#1 매핑 (s2 기준)
raw1_map = {}
for _, row in raw1.iterrows():
    s2 = str(row.get('s2', '')).strip()
    s3 = str(row.get('s3', '')).strip()
    s4_r = str(row.get('s4', '')).strip()
    s5 = str(row.get('s5', '')).strip()
    if s2 and s2 != 'nan':
        raw1_map[s2] = {'s3': s3, 's4': s4_r, 's5': s5}

# ============================================================
# 4. 매핑 실행
# ============================================================
s4_list = []
s4_name_list = []

for idx, row in raw_merged.iterrows():
    s1 = str(row.get('s1', '')).strip() if pd.notna(row.get('s1')) else ''
    s2 = str(row.get('s2', '')).strip() if pd.notna(row.get('s2')) else ''
    s3 = str(row.get('s3', '')).strip() if pd.notna(row.get('s3')) else ''
    
    s1 = s1.replace('\r', '').replace('\u3000', '').strip()
    s2 = s2.replace('\r', '').strip()
    s3 = s3.replace('\r', '').strip()
    
    dae_code = ''
    dae_name = ''
    
    # Case 1: s3가 중분류 숫자 코드인 경우
    if s3 and s3 not in ('nan', '', '알수없음'):
        s3_padded = s3.zfill(2) if s3.isdigit() else s3
        if s3_padded in jung_to_dae:
            dae_code = jung_to_dae[s3_padded]
            dae_name = dae_name_map.get(dae_code, '')
        elif s3 in dae_name_map:
            dae_code = s3
            dae_name = dae_name_map.get(s3, '')
    
    # Case 2: s2 기반 업종#1 매핑
    if not dae_code and s2 and s2 != 'nan':
        if s2 in raw1_map:
            ref = raw1_map[s2]
            ref_s3 = ref['s3']
            ref_s5 = ref['s5']
            
            if ref_s5 == '대분류':
                dae_code = ref_s3
                dae_name = dae_name_map.get(ref_s3, '')
            elif ref_s5 == '중분류':
                ref_s3_padded = ref_s3.zfill(2) if ref_s3.isdigit() else ref_s3
                if ref_s3_padded in jung_to_dae:
                    dae_code = jung_to_dae[ref_s3_padded]
                    dae_name = dae_name_map.get(dae_code, '')
    
    # Case 3: s1 기반 대분류명 직접 매칭
    if not dae_code and s1 and s1 != 'nan':
        # 대분류명 직접 매칭
        name_to_dae = {v: k for k, v in dae_name_map.items()}
        if s1 in name_to_dae:
            dae_code = name_to_dae[s1]
            dae_name = s1
        else:
            # 부분 매칭
            for nm, cd in name_to_dae.items():
                if s1 in nm or nm in s1:
                    dae_code = cd
                    dae_name = nm
                    break
            # 제조업 계열
            if not dae_code and '제조업' in s1:
                dae_code = 'C'
                dae_name = '제조업'
    
    # Case 4: 9999 / 알수없음
    if not dae_code:
        if s1 in ('9999', '알수없음') or s3 == '알수없음':
            dae_code = '알수없음'
            dae_name = '알수없음'
    
    s4_list.append(dae_code)
    s4_name_list.append(dae_name)

raw_merged['s4'] = s4_list
raw_merged['s4_name'] = s4_name_list

# ============================================================
# 5. 결과 확인
# ============================================================
print('\n=== 매핑 결과 ===')
cols_to_show = [c for c in ['s1','s2','s3','s3_nm','s4','s4_name'] if c in raw_merged.columns]
print(raw_merged[cols_to_show].to_string())

unmapped = raw_merged[(raw_merged['s4'] == '') & (raw_merged['s1'].notna()) & (raw_merged['s1'].str.strip() != '') & (raw_merged['s1'].str.strip() != 'nan')]
if len(unmapped) > 0:
    print(f'\n=== 매핑 실패 {len(unmapped)}건 ===')
    print(unmapped[cols_to_show].to_string())
else:
    print('\n*** 모든 행이 정상적으로 매핑되었습니다 ***')

# 대분류별 요약
print('\n=== 대분류별 요약 ===')
summary = raw_merged.groupby(['s4', 's4_name']).size().reset_index(name='count')
print(summary.to_string(index=False))

# ============================================================
# 6. 저장
# ============================================================
raw_merged.to_csv('업종_raw data.csv', index=False, encoding='utf-8-sig')
print('\n>>> 파일 저장 완료: 업종_raw data.csv')
