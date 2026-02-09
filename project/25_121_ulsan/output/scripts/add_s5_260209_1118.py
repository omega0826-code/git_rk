# -*- coding: utf-8 -*-
import csv, os
BASE = r'd:\git_rk\project\25_121_ulsan\CSV'

dae_codes = set()
with open(os.path.join(BASE, '표준산업분류_대분류.csv'), 'r', encoding='utf-8') as f:
    for row in csv.reader(f):
        if len(row) >= 2 and row[0].strip():
            dae_codes.add(row[0].strip())

jung_codes = set()
with open(os.path.join(BASE, '표준산업분류_중분류.csv'), 'r', encoding='utf-8') as f:
    for row in csv.reader(f):
        if len(row) >= 2 and row[0].strip() and row[0].strip() != '코드':
            jung_codes.add(row[0].strip().replace('\r', ''))

rows = []
with open(os.path.join(BASE, '업종#1_raw data.csv'), 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if len(row) >= 4 and row[0].strip():
            s3 = row[2].strip()
            if s3 in jung_codes:
                s5 = '중분류'
            elif s3 in dae_codes:
                s5 = '대분류'
            else:
                s5 = '알수없음'
            rows.append(row[:4] + [s5])

with open(os.path.join(BASE, '업종#1_raw data.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['s1', 's2', 's3', 's4', 's5'])
    w.writerows(rows)

print(f'Done: {len(rows)}개')
for r in rows:
    print(f'  s3={r[2]:4s}  s5={r[4]}  {r[0][:40]}')
