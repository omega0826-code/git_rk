# -*- coding: utf-8 -*-
"""맑은기업 CSV 재정렬 + Z_조사_개요/Z_규모별_특성 수정"""
import os, csv, sys
sys.stdout.reconfigure(encoding='utf-8')

CSV_DIR = r'd:\git_rk\project\25_124_interviiew\260209\REPORT\output\csv_tables'

def get_size_order(s):
    if '30명 미만' in s and '30~50' not in s:
        return 0
    elif '30~50' in s:
        return 1
    elif '50명 이상' in s:
        return 2
    return 3

# 1. Fix Z_조사_개요.csv
fp = os.path.join(CSV_DIR, 'Z_조사_개요.csv')
with open(fp, 'r', encoding='utf-8-sig') as f:
    content = f.read()
content = content.replace('30명 미만(7)', '30명 미만(8)')
content = content.replace('30~50명 미만(9)', '30~50명 미만(8)')
with open(fp, 'w', encoding='utf-8-sig') as f:
    f.write(content)
print('[OK] Z_조사_개요.csv')

# 2. Fix Z_규모별_특성.csv
fp2 = os.path.join(CSV_DIR, 'Z_규모별_특성.csv')
with open(fp2, 'r', encoding='utf-8-sig') as f:
    content2 = f.read()
print(f'[INFO] Z_규모별_특성.csv 현재 내용:\n{content2}')
# This file documents corrections - update it
with open(fp2, 'w', encoding='utf-8-sig') as f:
    f.write('항목,기존(개별보고서),수정(통합보고서),비고\r\n')
    f.write('제조업 기업 수,14개,**15개**,한텍(가스-제조업) 누락\r\n')
    f.write('30명 미만 기업 수,7개,**8개**,맑은기업(20명) 재분류\r\n')
    f.write('30~50명 기업 수,9개,**8개**,맑은기업 제외\r\n')
    f.write('제조업 비율 분모,/14,**/15**,전체 테이블 재계산\r\n')
print('[OK] Z_규모별_특성.csv')

# 3. Re-sort 기업별 detail CSV files
sorted_count = 0
for fname in sorted(os.listdir(CSV_DIR)):
    if not fname.endswith('.csv'):
        continue
    fpath = os.path.join(CSV_DIR, fname)
    
    with open(fpath, 'r', encoding='utf-8-sig') as f:
        reader = list(csv.reader(f))
    
    if len(reader) < 3:
        continue
    
    header = reader[0]
    if len(header) < 3:
        continue
    
    has_no = header[0].strip() in ('NO', 'no', 'No')
    size_col = -1
    for ci, col in enumerate(header):
        if col.strip() == '규모':
            size_col = ci
            break
    
    if size_col < 0 or not has_no:
        continue
    
    # Skip separator row
    data_start = 1
    separator = None
    if len(reader) > 1 and reader[1][0].strip().startswith(':'):
        data_start = 2
        separator = reader[1]
    
    data_rows = [r for r in reader[data_start:] if any(cell.strip() for cell in r)]
    if not data_rows:
        continue
    
    has_malgeun = any('맑은기업' in ','.join(r) for r in data_rows)
    if not has_malgeun:
        continue
    
    # Add original index for stable sort
    for i, r in enumerate(data_rows):
        r.append(str(i))
    
    data_rows.sort(key=lambda r: (get_size_order(r[size_col]), int(r[-1])))
    
    for i, r in enumerate(data_rows):
        r.pop()
        r[0] = str(i + 1)
    
    output = [header]
    if separator:
        output.append(separator)
    output.extend(data_rows)
    
    with open(fpath, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(output)
    
    sorted_count += 1
    print(f'[SORT] {fname}')

print(f'\n[DONE] 재정렬 완료: {sorted_count}개 파일')

# 4. Verify 맑은기업 is now in 30명 미만 group
print('\n===== 검증: 맑은기업 위치 확인 =====')
for fname in sorted(os.listdir(CSV_DIR)):
    if not fname.endswith('.csv'):
        continue
    fpath = os.path.join(CSV_DIR, fname)
    with open(fpath, 'r', encoding='utf-8-sig') as f:
        for i, line in enumerate(f, 1):
            if '맑은기업' in line:
                print(f'  {fname}:{i} -> {line.strip()[:100]}')
                break
