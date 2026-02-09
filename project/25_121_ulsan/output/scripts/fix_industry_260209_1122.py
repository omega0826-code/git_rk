# -*- coding: utf-8 -*-
"""업종 분류 최종 보정 - 수동 검토 결과 반영"""
import csv, os

BASE = r'd:\git_rk\project\25_121_ulsan\CSV'

# 수동 보정 테이블: s1 키워드 -> (s3, s4, s5)
# 원칙: 중분류에 정확히 대응되면 중분류, 아니면 대분류
corrections = {
    # 농업,임업및어업 → 대분류1 (중분류는 01농업, 02임업, 03어업으로 분리됨)
    "농업, 임업 및 어업": ("1", "농업, 임업 및 어업", "대분류"),
    # 정보통신업 → 대분류10 (중분류에는 58출판, 59영상, 60방송, 61통신, 62컴퓨터, 63정보서비스로 분리)
    "정보통신업": ("10", "정보통신업", "대분류"),
    # 금융및보험업 → 대분류11 (중분류는 64금융, 65보험연금, 66금융보험서비스로 분리)
    "금융 및 보험업": ("11", "금융 및 보험업", "대분류"),
    # 전문,과학 및 기술 서비스업 → 대분류13 (중분류는 70연구개발, 71전문서비스, 72건축기술, 73기타로 분리)
    "전문, 과학 및 기술 서비스업": ("13", "전문, 과학 및 기술 서비스업", "대분류"),
    # 사업시설관리,사업지원 및 임대 서비스업 → 대분류14 (중분류는 74사업시설, 75사업지원, 76임대로 분리)
    "사업시설 관리, 사업 지원 및 임대 서비스업": ("14", "사업시설 관리, 사업 지원 및 임대 서비스업", "대분류"),
    # 보건업및사회복지서비스업 → 대분류17 (중분류는 86보건업, 87사회복지로 분리)
    "보건업 및 사회복지 서비스업": ("17", "보건업 및 사회복지 서비스업", "대분류"),
    # 예술,스포츠및여가관련 서비스업 → 대분류18 (중분류는 90창작예술, 91스포츠오락으로 분리)
    "예술, 스포츠 및 여가관련 서비스업": ("18", "예술, 스포츠 및 여가관련 서비스업", "대분류"),
}

def clean(s):
    return s.strip().replace('\r','').replace('　',' ').replace('；',';').strip()

# 원본 로드
rows = []
with open(os.path.join(BASE, '업종#1_raw data.csv'), 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if len(row) >= 5 and row[0].strip():
            rows.append(row)

# 보정 적용
result = []
changes = 0
for row in rows:
    s1_clean = clean(row[0])
    s1_key = s1_clean
    # 괄호 부분 제거해서 비교
    import re
    s1_base = re.sub(r'\([^)]*\)', '', s1_clean).strip()
    
    corrected = False
    for key, (new_s3, new_s4, new_s5) in corrections.items():
        if key == s1_base or key == s1_key:
            old = f"s3={row[2]}, s4={row[3]}, s5={row[4]}"
            new = f"s3={new_s3}, s4={new_s4}, s5={new_s5}"
            if old != new:
                print(f"[수정] {s1_base[:35]}")
                print(f"  Before: {old}")
                print(f"  After : {new}")
                changes += 1
            row[2], row[3], row[4] = new_s3, new_s4, new_s5
            corrected = True
            break
    
    result.append(row[:5])

# 저장
with open(os.path.join(BASE, '업종#1_raw data.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['s1','s2','s3','s4','s5'])
    w.writerows(result)

print(f"\n[완료] {changes}건 보정, 총 {len(result)}개")
print(f"\n--- 최종 결과 ---")
for r in result:
    print(f"  s3={r[2]:4s}  s5={r[4]:3s}  s4={r[3]}")
