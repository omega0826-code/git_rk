# -*- coding: utf-8 -*-
"""업종 분류 매핑 스크립트 - s3(코드), s4(코드명) 추가"""
import csv
import re
import os

BASE = r"d:\git_rk\project\25_121_ulsan\CSV"

def clean(s):
    """텍스트 정규화: 공백/특수문자 제거"""
    s = s.strip().replace('\r', '').replace('\n', '')
    s = s.replace('；', ';').replace('　', ' ').strip()
    # 괄호 안 예시 제거 (SK이노베이션 등)
    s = re.sub(r'\([^)]*\)', '', s)
    s = s.strip()
    return s

# 1. 대분류 로드
dae = {}
with open(os.path.join(BASE, "표준산업분류_대분류.csv"), "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 2 and row[0].strip():
            code = row[0].strip()
            name = row[1].strip()
            dae[code] = name

# 2. 중분류 로드
jung = {}
with open(os.path.join(BASE, "표준산업분류_중분류.csv"), "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 2 and row[0].strip() and row[0].strip() != '코드':
            code = row[0].strip().replace('\r','')
            name = row[1].strip().replace('\r','')
            jung[code] = name

print(f"대분류: {len(dae)}개, 중분류: {len(jung)}개")

# 3. 원본 데이터 로드
raw_data = []
with open(os.path.join(BASE, "업종#1_raw data.csv"), "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if len(row) >= 2 and row[0].strip():
            raw_data.append(row)

print(f"원본 데이터: {len(raw_data)}개 항목")

# 4. 매핑 로직
def normalize(s):
    s = clean(s)
    s = s.replace(' ', '').replace(';', '').replace('；', '')
    return s

# 대분류 매핑 딕셔너리 (정규화된 키 -> (코드, 원본명))
dae_map = {normalize(v): (k, v) for k, v in dae.items()}

# 중분류 매핑 딕셔너리
jung_map = {normalize(v): (k, v) for k, v in jung.items()}

# 직접 매핑 테이블 (원본 s1 -> 중분류 코드)
direct_map = {
    "코크스, 연탄 및 석유정제품 제조업": ("19", "코크스, 연탄 및 석유정제품 제조업"),
    "화학 물질 및 화학제품 제조업": ("20", "화학 물질 및 화학제품 제조업; 의약품 제외"),
    "전자 부품, 컴퓨터, 영상, 음향 및 통신장비 제조업": ("26", "전자 부품, 컴퓨터, 영상, 음향 및 통신장비 제조업"),
    "의료, 정밀, 광학 기기 및 시계 제조업": ("27", "의료, 정밀, 광학 기기 및 시계 제조업"),
    "전기장비 제조업": ("28", "전기장비 제조업"),
    "자동차 및 트레일러 제조업": ("30", "자동차 및 트레일러 제조업"),
    "기타 기계 및 장비 제조업": ("29", "기타 기계 및 장비 제조업"),
    "그 외 제조업": ("3", "제조업"),  # 대분류로 매핑
}

results = []
for row in raw_data:
    s1 = row[0].strip().replace('\r', '')
    s2 = row[1].strip().replace('\r', '')
    s1_clean = clean(s1)
    s1_norm = normalize(s1)
    
    s3 = ""
    s4 = ""
    matched = False
    
    # 1) 직접 매핑 확인
    for key, (code, name) in direct_map.items():
        if normalize(key) == s1_norm:
            s3 = code
            s4 = name
            matched = True
            break
    
    # 2) 중분류 정확 매칭
    if not matched:
        if s1_norm in jung_map:
            s3, s4 = jung_map[s1_norm]
            matched = True
    
    # 3) 대분류 정확 매칭
    if not matched:
        if s1_norm in dae_map:
            s3, s4 = dae_map[s1_norm]
            matched = True
    
    # 4) 부분 매칭 (중분류)
    if not matched:
        for norm_key, (code, name) in jung_map.items():
            if s1_norm in norm_key or norm_key in s1_norm:
                s3 = code
                s4 = name
                matched = True
                break
    
    # 5) 부분 매칭 (대분류)
    if not matched:
        for norm_key, (code, name) in dae_map.items():
            if s1_norm in norm_key or norm_key in s1_norm:
                s3 = code
                s4 = name
                matched = True
                break
    
    if not matched:
        s3 = "알수없음"
        s4 = "알수없음"
        print(f"  [미매칭] {s1}")
    
    results.append([s1, s2, s3, s4])
    print(f"  {s1[:30]:30s} => s3={s3:5s}, s4={s4}")

# 5. 결과 저장 (UTF-8 BOM)
output_file = os.path.join(BASE, "업종#1_raw data.csv")
with open(output_file, "w", encoding="utf-8-sig", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["s1", "s2", "s3", "s4"])
    for r in results:
        writer.writerow(r)

print(f"\n[완료] {output_file}")
print(f"총 {len(results)}개 항목, 매칭 완료")
