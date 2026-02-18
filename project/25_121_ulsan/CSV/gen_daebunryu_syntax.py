# -*- coding: utf-8 -*-
"""
업종_raw data.csv 기반으로 대분류 변환 SPSS syntax 생성
- b1(=s2) -> 대분류 코드로 RECODE
- VALUE LABELS: s4 + ' ' + s4_name
"""
import pandas as pd
import os

os.chdir(r'd:\git_rk\project\25_121_ulsan\CSV')

raw = pd.read_csv('업종_raw data.csv', encoding='utf-8-sig', dtype=str)

# 정리
for c in raw.columns:
    if raw[c].dtype == object:
        raw[c] = raw[c].str.strip().str.replace('\r', '', regex=False).str.replace('\u3000', '', regex=False)

# 빈행 제거
raw = raw.dropna(subset=['s2']).reset_index(drop=True)
raw = raw[raw['s2'].notna() & (raw['s2'] != '') & (raw['s2'] != 'nan')].reset_index(drop=True)

# ============================================================
# 대분류 코드를 숫자로 변환 (SPSS VALUE LABELS용)
# ============================================================
dae_code_num = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5,
    'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10,
    'K': 11, 'L': 12, 'M': 13, 'N': 14, 'O': 15,
    'P': 16, 'Q': 17, 'R': 18, 'S': 19, 'T': 20, 'U': 21,
    '알수없음': 9999
}

# ============================================================
# 1. RECODE 구문 생성: b1(s2) -> 대분류 숫자코드
# ============================================================
# s2 -> s4 매핑 (중복 제거)
recode_map = {}
for _, row in raw.iterrows():
    s2 = str(row['s2']).strip()
    s4 = str(row['s4']).strip()
    if s2 and s4 and s2 != 'nan' and s4 != 'nan':
        recode_target = dae_code_num.get(s4, s4)
        recode_map[s2] = recode_target

lines = []
lines.append('RECODE b1')
# s2 기준 숫자 정렬
for s2_val in sorted(recode_map.keys(), key=lambda x: int(x) if x.isdigit() else 99999):
    target = recode_map[s2_val]
    lines.append(f'({s2_val}={target})')
lines.append('(else = copy)')
lines.append(' into b1#1_daebunryu.')
lines.append('')
lines.append('EXECUTE.')
lines.append('')

# ============================================================
# 2. VALUE LABELS 구문 생성: 대분류 숫자코드 + 's4 s4_name'
# ============================================================
# 고유 s4 + s4_name 조합
label_map = {}
for _, row in raw.iterrows():
    s4 = str(row['s4']).strip()
    s4_name = str(row['s4_name']).strip()
    if s4 and s4 != 'nan' and s4_name and s4_name != 'nan':
        num = dae_code_num.get(s4, s4)
        label = f'{s4} {s4_name}'
        label_map[num] = label

lines.append('VALUE LABELS')
lines.append('b1#1_daebunryu')
for num in sorted(label_map.keys(), key=lambda x: int(x) if isinstance(x, int) else 99999):
    label = label_map[num]
    lines.append(f"    {num} '{label}'")

# 마지막 줄에 마침표
last = lines[-1]
lines[-1] = last + '.'
lines.append('')

# ============================================================
# 3. 파일 저장
# ============================================================
output_text = '\n'.join(lines)
output_path = '업종 대분류 변환 syntax.md'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(output_text)

print(output_text)
print(f'\n>>> 파일 저장 완료: {output_path}')
