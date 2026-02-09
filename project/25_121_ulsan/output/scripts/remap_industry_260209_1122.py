# -*- coding: utf-8 -*-
"""업종 분류 재매핑 - 중분류 우선, 이름 기반 정확 매칭"""
import csv, os, re

BASE = r'd:\git_rk\project\25_121_ulsan\CSV'

def clean(s):
    s = s.strip().replace('\r','').replace('\n','').replace('；',';').replace('　',' ').strip()
    s = re.sub(r'\([^)]*\)', '', s).strip()
    return s

def normalize(s):
    return clean(s).replace(' ','').replace(';','')

# 대분류 로드: {정규화이름: (코드, 원본이름)}
dae = {}
with open(os.path.join(BASE, '표준산업분류_대분류.csv'), 'r', encoding='utf-8') as f:
    for row in csv.reader(f):
        if len(row)>=2 and row[0].strip():
            dae[normalize(row[1])] = (row[0].strip(), clean(row[1]))

# 중분류 로드: {정규화이름: (코드, 원본이름)}
jung = {}
with open(os.path.join(BASE, '표준산업분류_중분류.csv'), 'r', encoding='utf-8') as f:
    for row in csv.reader(f):
        if len(row)>=2 and row[0].strip() and row[0].strip()!='코드':
            code = row[0].strip().replace('\r','')
            name = row[1].strip().replace('\r','')
            jung[normalize(name)] = (code, clean(name))

print(f"대분류: {len(dae)}개")
print(f"중분류: {len(jung)}개")

# 원본 로드
raw = []
with open(os.path.join(BASE, '업종#1_raw data.csv'), 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        if len(row) >= 2 and row[0].strip():
            raw.append(row)

print(f"\n원본: {len(raw)}개\n{'='*80}")

# 매핑
results = []
for row in raw:
    s1 = row[0].strip().replace('\r','')
    s2 = row[1].strip().replace('\r','')
    s1_norm = normalize(s1)
    
    s3, s4, s5 = '', '', ''
    matched = False
    
    # 1) 중분류 정확 매칭 (이름 기반)
    if s1_norm in jung:
        s3, s4 = jung[s1_norm]
        s5 = '중분류'
        matched = True
    
    # 2) 중분류 포함 매칭
    if not matched:
        for nk, (code, name) in jung.items():
            if s1_norm == nk or (len(s1_norm) > 5 and (s1_norm in nk or nk in s1_norm)):
                s3, s4 = code, name
                s5 = '중분류'
                matched = True
                break
    
    # 3) 대분류 정확 매칭
    if not matched:
        if s1_norm in dae:
            s3, s4 = dae[s1_norm]
            s5 = '대분류'
            matched = True
    
    # 4) 대분류 포함 매칭
    if not matched:
        for nk, (code, name) in dae.items():
            if len(s1_norm) > 3 and (s1_norm in nk or nk in s1_norm):
                s3, s4 = code, name
                s5 = '대분류'
                matched = True
                break
    
    # 5) 특수 케이스
    if not matched:
        if '제조업' in s1 and '그 외' in s1:
            s3, s4, s5 = '3', '제조업', '대분류'
            matched = True
    
    if not matched:
        s3, s4, s5 = '알수없음', '알수없음', ''
        print(f"  [미매칭] {s1}")
    
    results.append([s1, s2, s3, s4, s5])
    print(f"  s3={s3:4s}  s5={s5:3s}  s4={s4}")

# 저장
with open(os.path.join(BASE, '업종#1_raw data.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['s1','s2','s3','s4','s5'])
    w.writerows(results)

print(f"\n{'='*80}")
print(f"[완료] 총 {len(results)}개")
dae_cnt = sum(1 for r in results if r[4]=='대분류')
jung_cnt = sum(1 for r in results if r[4]=='중분류')
print(f"  대분류: {dae_cnt}개, 중분류: {jung_cnt}개")
