# -*- coding: utf-8 -*-
import os, glob
from datetime import datetime

BASE = r"d:\git_rk\project\25_121_ulsan\output"
WORDING_DIR = os.path.join(BASE, "wording")

# Find latest wording MD file
md_files = glob.glob(os.path.join(WORDING_DIR, "wording_*_1018.md"))
if not md_files:
    md_files = glob.glob(os.path.join(WORDING_DIR, "wording_*.md"))
md_file = sorted(md_files)[-1]
print(f"Source: {md_file}")

with open(md_file, "r", encoding="utf-8") as f:
    t = f.read()

# Strip markdown formatting for TXT
t = t.replace("**", "")
lines = []
for line in t.split("\n"):
    if line.startswith("# "):
        line = line[2:]
    elif line.startswith("## "):
        line = line[3:]
    elif line.startswith("### "):
        line = line[4:]
    if line.strip() == "---":
        line = ""
    lines.append(line)
txt = "\n".join(lines)

txt_file = md_file.replace(".md", ".txt")
with open(txt_file, "w", encoding="utf-8") as f:
    f.write(txt)
print(f"TXT created: {txt_file}")

# Generate report
MD_DATA = os.path.join(BASE, "(OUTPUT)울산 일자리 미스매치_260205_1822.md")
with open(MD_DATA, "r", encoding="utf-8") as f:
    md_content = f.read()

sections = md_content.split("\n---\n")
tables = {}
for i, sec in enumerate(sections):
    sec_strip = sec.strip()
    if sec_strip:
        table_lines = [l for l in sec_strip.split("\n") if l.startswith("|")]
        tables[i] = "\n".join(table_lines)

# Parse wording
with open(md_file, "r", encoding="utf-8") as f:
    wording_content = f.read()

wording_sections = wording_content.split("\n---\n")
wordings = {}
num_map = {"1.":1,"2.":2,"3.":3,"4.":4,"5.":5,"6.":6,"7.":7,"8.":8,"9.":9,
           "10.":10,"11.":11,"12.":12,"13":13,"15.":15,"16.":16,"17.":17,"18.":18,"19.":19}
for ws in wording_sections:
    ws = ws.strip()
    if not ws: continue
    lines_w = ws.split("\n")
    header = ""
    for l in lines_w:
        if l.startswith("## "):
            header = l; break
    if not header: continue
    idx = lines_w.index(header)
    text = "\n".join(lines_w[idx+1:]).strip()
    h = header.replace("## ", "").strip()
    for prefix, num in num_map.items():
        if h.startswith(prefix):
            wordings[num] = text; break

ts = datetime.now().strftime("%y%m%d_%H%M")
REPORT_DIR = os.path.join(BASE, "report")
os.makedirs(REPORT_DIR, exist_ok=True)
OUTPUT = os.path.join(REPORT_DIR, f"울산_일자리_미스매치_분석보고서_{ts}.md")

structure = [
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

report = [f"# 울산 일자리 미스매치 분석 보고서\n",
          f"> 생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n", "---\n"]
for tidx, heading, wkey in structure:
    report.append(heading); report.append("")
    if wkey and wkey in wordings:
        report.append(wordings[wkey]); report.append("")
    if tidx is not None and tidx in tables and tables[tidx]:
        report.append(tables[tidx]); report.append("")
    report.append("---\n")

report_text = "\n".join(report)
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(report_text)
print(f"Report: {OUTPUT}")
print(f"Size: {len(report_text):,} bytes")
