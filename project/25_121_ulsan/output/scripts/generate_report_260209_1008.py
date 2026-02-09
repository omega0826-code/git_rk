# -*- coding: utf-8 -*-
"""보고서 재생성 - 워딩 수정본(마침표 제거, 평균대비 제거) 반영"""
import os
from datetime import datetime

BASE_DIR = r"d:\git_rk\project\25_121_ulsan\output"
MD_FILE = os.path.join(BASE_DIR, "(OUTPUT)울산 일자리 미스매치_260205_1822.md")
WORDING_FILE = os.path.join(BASE_DIR, "wording", "wording_전체_260209_1008.md")
REPORT_DIR = os.path.join(BASE_DIR, "report")
os.makedirs(REPORT_DIR, exist_ok=True)

ts = datetime.now().strftime("%y%m%d_%H%M")
OUTPUT_FILE = os.path.join(REPORT_DIR, f"울산_일자리_미스매치_분석보고서_{ts}.md")

# 원본 MD에서 각 섹션의 테이블 추출
with open(MD_FILE, "r", encoding="utf-8") as f:
    md_content = f.read()

sections = md_content.split("\n---\n")

def get_table(section_text):
    lines = section_text.strip().split("\n")
    table_lines = [l for l in lines if l.startswith("|")]
    return "\n".join(table_lines)

tables = {}
for i, sec in enumerate(sections):
    sec_strip = sec.strip()
    if sec_strip:
        tables[i] = get_table(sec_strip)

# 워딩 파일에서 각 문항별 텍스트 추출
with open(WORDING_FILE, "r", encoding="utf-8") as f:
    wording_content = f.read()

wording_sections = wording_content.split("\n---\n")
wordings = {}
for ws in wording_sections:
    ws = ws.strip()
    if not ws:
        continue
    lines = ws.split("\n")
    # 첫 줄에서 번호 추출
    header = ""
    for l in lines:
        if l.startswith("## "):
            header = l
            break
    if not header:
        continue
    # 헤더 이후 텍스트만 추출
    idx = lines.index(header)
    text = "\n".join(lines[idx+1:]).strip()
    
    # 번호 파싱
    h = header.replace("## ", "").strip()
    if h.startswith("1."):
        wordings[1] = text
    elif h.startswith("2."):
        wordings[2] = text
    elif h.startswith("3."):
        wordings[3] = text
    elif h.startswith("4."):
        wordings[4] = text
    elif h.startswith("5."):
        wordings[5] = text
    elif h.startswith("6."):
        wordings[6] = text
    elif h.startswith("7."):
        wordings[7] = text
    elif h.startswith("8."):
        wordings[8] = text
    elif h.startswith("9."):
        wordings[9] = text
    elif h.startswith("10."):
        wordings[10] = text
    elif h.startswith("11."):
        wordings[11] = text
    elif h.startswith("12."):
        wordings[12] = text
    elif h.startswith("13"):
        wordings[13] = text
    elif h.startswith("15."):
        wordings[15] = text
    elif h.startswith("16."):
        wordings[16] = text
    elif h.startswith("17."):
        wordings[17] = text
    elif h.startswith("18."):
        wordings[18] = text
    elif h.startswith("19."):
        wordings[19] = text

# 보고서 구조
report_structure = [
    (None, "## 1. 조사 개요\n\n> 울산 소재 4개 대학 재학생 1,000명 대상 일자리 미스매치 실태 조사 결과", None),
    (0, "## 2. 응답자 일반현황", 1),
    (1, "## 3. 취업 준비 현황\n\n### 3-1. 일자리 정보 탐색 활용 경로 (중복응답)", 2),
    (2, "### 3-2. 취업 준비 중 느끼는 어려움 (중복응답)", 3),
    (3, "### 3-3. 대학에서 제공 받았으면 하는 지원 (중복응답)", 4),
    (4, "### 3-4-1. 필요 취업 정보 (1순위)", 5),
    (5, "### 3-4-2. 필요 취업 정보 (1순위+2순위)", 6),
    (6, "### 3-5-1. 부족 역량 (1순위)", 7),
    (7, "### 3-5-2. 부족 역량 (1순위+2순위)", 8),
    (8, "## 4. 취업 희망 조건\n\n### 4-1-1. 취업 시 고려 요소 (1순위)", 9),
    (9, "### 4-1-2. 취업 시 고려 요소 (1순위+2순위)", 10),
    (10, "### 4-2. 대학교별 취업 희망 업종", 11),
    (11, "### 4-3. 대학교별 취업 희망 직군", 12),
    (12, "## 5. 울산 지역 인식 및 정주 의향\n\n### 5-1. 울산 지역 기업 인식 수준 (응답자 수)", 13),
    (13, "### 5-1-2. 울산 지역 기업 인식 수준 (평균)", None),
    (14, "### 5-2. 졸업 후 희망 취업 지역", 15),
    (15, "### 5-3. 울산 정주 환경이 타지역 취업에 미친 영향", 16),
    (16, "### 5-3-1. 타지역 취업에 영향을 미친 정주환경 요인 (중복응답)", 17),
    (17, "### 5-4-1. 청년 정착 지원 정책 (1순위)", 18),
    (18, "### 5-4-2. 청년 정착 지원 정책 (1순위+2순위)", 19),
]

report_lines = []
report_lines.append("# 울산 일자리 미스매치 분석 보고서\n")
report_lines.append(f"> 생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
report_lines.append("---\n")

for table_idx, heading, wording_key in report_structure:
    report_lines.append(heading)
    report_lines.append("")
    if wording_key and wording_key in wordings:
        report_lines.append(wordings[wording_key])
        report_lines.append("")
    if table_idx is not None and table_idx in tables and tables[table_idx]:
        report_lines.append(tables[table_idx])
        report_lines.append("")
    report_lines.append("---\n")

report_text = "\n".join(report_lines)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(report_text)

print(f"[완료] 보고서 생성: {OUTPUT_FILE}")
print(f"[완료] 총 {len(report_text):,} bytes")
