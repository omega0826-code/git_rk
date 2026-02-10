# -*- coding: utf-8 -*-
"""
B/C/D 그룹 보고서의 기업별 응답 테이블을 Part A처럼 다중 열로 재구성.
- B: Q3+Q3_1+Q3_2 → 반복수강여부/강사변경영향/재수강의향 3열 합치기
- C: Q5+Q6+Q8 → 교육효과지원/AI적용현황/AI디지털필수교육 3열 합치기  
- D: Q7+Q7_1+Q7_2 → 참여과목방식/선호우려/대안방식 3열 합치기
"""
import csv, os

CSV_FILE = r"d:\git_rk\project\25_124_interviiew\260209\(csv)interview_0209.csv"
REPORT_DIR = r"d:\git_rk\project\25_124_interviiew\260209\REPORT"

# Read CSV
with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Company order from existing reports (sorted by 규모 then name)
COMPANY_ORDER = [
    ("금정(온산지점)", "30명 미만"),
    ("동일메탈", "30명 미만"),
    ("드래곤엠앤이", "30명 미만"),
    ("세광기업", "30명 미만"),
    ("세영윈도우", "30명 미만"),
    ("아성정밀화학", "30명 미만"),
    ("예광이엔지", "30명 미만"),
    ("대송컨테이너항업", "30~50명"),
    ("맑은기업", "30~50명"),
    ("선경화성", "30~50명"),
    ("수성정밀", "30~50명"),
    ("㈜스윅", "30~50명"),
    ("㈜아일", "30~50명"),
    ("에스엘티이", "30~50명"),
    ("케이에이알", "30~50명"),
    ("한국후지필터", "30~50명"),
    ("디비밸리", "50명 이상"),
    ("㈜성전사", "50명 이상"),
    ("코스포영남파워", "50명 이상"),
    ("한텍", "50명 이상"),
    ("현대밋숀", "50명 이상"),
]

# Map CSV company names to report names
NAME_MAP = {}
for row in rows:
    csv_name = row.get("업체명", "").strip().replace(" ", "")
    for report_name, size in COMPANY_ORDER:
        if report_name.replace("(", "").replace(")", "").replace("㈜", "") in csv_name.replace("(", "").replace(")", "").replace("㈜", "") or \
           csv_name in report_name.replace(" ", ""):
            NAME_MAP[report_name] = row
            break

# Manual fixes for fuzzy matching
for row in rows:
    name = row.get("업체명", "").strip()
    if "금정" in name: NAME_MAP["금정(온산지점)"] = row
    elif "동일" in name and "메탈" in name: NAME_MAP["동일메탈"] = row
    elif "드래곤" in name: NAME_MAP["드래곤엠앤이"] = row
    elif "세광" in name: NAME_MAP["세광기업"] = row
    elif "세영" in name: NAME_MAP["세영윈도우"] = row
    elif "아성" in name: NAME_MAP["아성정밀화학"] = row
    elif "예광" in name: NAME_MAP["예광이엔지"] = row
    elif "대송" in name: NAME_MAP["대송컨테이너항업"] = row
    elif "맑은" in name: NAME_MAP["맑은기업"] = row
    elif "선경" in name: NAME_MAP["선경화성"] = row
    elif "수성" in name: NAME_MAP["수성정밀"] = row
    elif "스윅" in name: NAME_MAP["㈜스윅"] = row
    elif "아일" in name: NAME_MAP["㈜아일"] = row
    elif "에스엘" in name: NAME_MAP["에스엘티이"] = row
    elif "케이에이" in name: NAME_MAP["케이에이알"] = row
    elif "후지" in name: NAME_MAP["한국후지필터"] = row
    elif "디비" in name: NAME_MAP["디비밸리"] = row
    elif "성전" in name: NAME_MAP["㈜성전사"] = row
    elif "코스포" in name: NAME_MAP["코스포영남파워"] = row
    elif "한텍" in name: NAME_MAP["한텍"] = row
    elif "현대" in name and "밋숀" in name: NAME_MAP["현대밋숀"] = row

def get_q(company_name, q_col):
    """Get question response for a company."""
    row = NAME_MAP.get(company_name)
    if not row: return "(응답 없음)"
    val = row.get(q_col, "").strip()
    if not val: return "(응답 없음)"
    # Truncate multiline to short summary
    val = val.replace("\n", " ").replace("\r", "")
    if len(val) > 80:
        val = val[:77] + "..."
    return val

# ========== B GROUP: Q3+Q3_1+Q3_2 합치기 ==========
print("=== B Group ===")

# Current B group file
b_path = os.path.join(REPORT_DIR, "02_group_B.md")
with open(b_path, "r", encoding="utf-8") as f:
    b_content = f.read()
b_lines = [l.rstrip("\r") for l in b_content.split("\n")]

# The existing single-column company table for Q3 is at lines 26-48
# We need to replace it with a 3-column table: 반복수강여부(Q3) / 강사변경영향(Q3_1) / 재수강의향(Q3_2)

# Build the existing summaries from the current report (keep them, just update the table)
# Existing B report summaries for Q3 companies (lines 26-48 of current file)
# Let's use the existing "응답" content from the report since it was already curated

# Read existing curated data from B report 1-2 table
existing_b_q3 = {}
for line in b_lines[26:48]:
    cells = [c.strip() for c in line.split("|")]
    cells = [c for c in cells if c != ""]
    if len(cells) >= 4 and cells[0].isdigit():
        no = int(cells[0])
        name = cells[1]
        size = cells[2]
        resp = cells[3]
        existing_b_q3[name] = {"no": no, "size": size, "q3": resp}

# Build Q3_1 and Q3_2 responses manually from CSV analysis (I already know from the file)
# Q3_1 = 강사변경영향, Q3_2 = 재수강의향
b_q3_1 = {
    "금정(온산지점)": "큰 차이 없음, 영향X",
    "동일메탈": "영향 없음",
    "드래곤엠앤이": "특별한 영향 없을 것 같음",
    "세광기업": "주제가 중요, 강사는 중요하지 않음",
    "세영윈도우": "X (해당없음)",
    "아성정밀화학": "강사 바뀌면 다른 경험 가능→의향↑",
    "예광이엔지": "그런 건 없음",
    "대송컨테이너항업": "영향 있음, 강사별 교육 해석 방식 차이",
    "맑은기업": "영향 없을 것 같음",
    "선경화성": "강사 비중X, 영향X",
    "수성정밀": "강사변경은 수강결정에 영향 별로 없음",
    "㈜스윅": "강사 정보 없어서 영향X, 질에 따라 다름",
    "㈜아일": "아젠다 위주, 강사 바뀐다고 달라지지 않음",
    "에스엘티이": "그렇다(영향 있음)",
    "케이에이알": "큰 영향X, 내용이 바뀌는 게 좋음",
    "한국후지필터": "그렇지 않음(영향 없음)",
    "디비밸리": "분산 수강이라 상관없음",
    "㈜성전사": "강사 차이 못 느낌, 과목이 중요",
    "코스포영남파워": "큰 차이 없음",
    "한텍": "그건 아님(영향 없음)",
    "현대밋숀": "그런 건 없음(영향 없음)",
}

b_q3_2 = {
    "금정(온산지점)": "그렇다",
    "동일메탈": "거의 없음",
    "드래곤엠앤이": "그렇다",
    "세광기업": "그렇다",
    "세영윈도우": "그렇다",
    "아성정밀화학": "법규·AI·디지털·장비 업데이트 시 반드시 재수강",
    "예광이엔지": "그렇다",
    "대송컨테이너항업": "그렇다",
    "맑은기업": "반복 교육 불필요하다고 느낌",
    "선경화성": "요즘 트렌드라 필요함",
    "수성정밀": "법령 변경·최신 기술 시 재수강 희망",
    "㈜스윅": "아주 그렇다, 최신 기술 동향 관심↑",
    "㈜아일": "매우 필요(AI, ESG)",
    "에스엘티이": "매우 그렇다",
    "케이에이알": "최신 기술 동향(AI, 디지털, 법규) OK",
    "한국후지필터": "그렇다",
    "디비밸리": "가능한 업데이트 과정 희망",
    "㈜성전사": "기술동향→상관X, 법규→중시",
    "코스포영남파워": "당연히 그렇다",
    "한텍": "그렇다, 임원분들 관심↑",
    "현대밋숀": "상관없음",
}

# Build new 3-column B table
new_b_table = []
new_b_table.append("|  NO   | 기업명           | 규모      | 반복 수강 여부 (Q3)                                              | 강사변경 영향 (Q3_1)                        | 재수강 의향 (Q3_2)                         |")
new_b_table.append("| :---: | ---------------- | --------- | ---------------------------------------------------------------- | ------------------------------------------- | ------------------------------------------ |")

for i, (name, size) in enumerate(COMPANY_ORDER, 1):
    q3_resp = existing_b_q3.get(name, {}).get("q3", "(응답 없음)")
    q3_1_resp = b_q3_1.get(name, "-")
    q3_2_resp = b_q3_2.get(name, "-")
    new_b_table.append(f"| {i:>3}   | {name:<16} | {size:<9} | {q3_resp:<64} | {q3_1_resp:<43} | {q3_2_resp:<42} |")

new_b_table_str = "\r\n".join(new_b_table)

# Replace old table (lines 26-48)
b_lines[25:48] = new_b_table_str.split("\r\n")

# Update section title 1-2
for i, line in enumerate(b_lines):
    if "### 1-2." in line:
        b_lines[i] = "### 1-2. 규모별 반복 수강 행태 및 기업별 응답 (Q3, Q3_1, Q3_2)"
        break

# Write back B
with open(b_path, "w", encoding="utf-8") as f:
    f.write("\r\n".join(b_lines) + "\r\n")
print(f"B group done: {b_path}")

# ========== C GROUP: Q5+Q6+Q8 합치기 ==========
print("\n=== C Group ===")

c_path = os.path.join(REPORT_DIR, "03_group_C.md")
with open(c_path, "r", encoding="utf-8") as f:
    c_content = f.read()
c_lines = [l.rstrip("\r") for l in c_content.split("\n")]

# Read existing Q5 responses (1-2, lines 22-44)
existing_c_q5 = {}
for line in c_lines[21:44]:
    cells = [c.strip() for c in line.split("|")]
    cells = [c for c in cells if c != ""]
    if len(cells) >= 4 and cells[0].isdigit():
        existing_c_q5[cells[1]] = cells[3]

# Read existing Q6 responses (2-2, lines 65-87)
existing_c_q6 = {}
for line in c_lines[64:87]:
    cells = [c.strip() for c in line.split("|")]
    cells = [c for c in cells if c != ""]
    if len(cells) >= 4 and cells[0].isdigit():
        existing_c_q6[cells[1]] = cells[3]

# Read existing Q8 responses (3-2, lines 108-130)
existing_c_q8 = {}
for line in c_lines[107:130]:
    cells = [c.strip() for c in line.split("|")]
    cells = [c for c in cells if c != ""]
    if len(cells) >= 4 and cells[0].isdigit():
        existing_c_q8[cells[1]] = cells[3]

# Build new combined C table (to replace 1-2)
new_c_table = []
new_c_table.append("|  NO   | 기업명           | 규모      | 교육 효과 지원 (Q5)                                             | AI 적용 현황 (Q6)                                     | AI·디지털 필수 교육 (Q8)                                    |")
new_c_table.append("| :---: | ---------------- | --------- | --------------------------------------------------------------- | ----------------------------------------------------- | ----------------------------------------------------------- |")

for i, (name, size) in enumerate(COMPANY_ORDER, 1):
    q5 = existing_c_q5.get(name, "(응답 없음)")
    q6 = existing_c_q6.get(name, "(응답 없음)")
    q8 = existing_c_q8.get(name, "(응답 없음)")
    new_c_table.append(f"| {i:>3}   | {name:<16} | {size:<9} | {q5:<63} | {q6:<53} | {q8:<59} |")

# Replace Q5 company table (1-2, lines 22-44) with combined table
# Also update section title
for i, line in enumerate(c_lines):
    if "### 1-2." in line:
        c_lines[i] = "### 1-2. 규모별 교육 효과 지원·AI 현황·필수 교육 및 기업별 응답 (Q5, Q6, Q8)"
        break

c_lines[21:44] = new_c_table

# Remove the standalone Q6 and Q8 company tables (2-2, 3-2)
# After replacing 1-2, line numbers shifted. Find and remove 2-2 and 3-2 sections.
# Find "### 2-2." and remove until next "---"
new_c_lines = []
skip_until_next_section = False
skip_section_name = None
for i, line in enumerate(c_lines):
    if "### 2-2." in line or "### 3-2." in line:
        skip_until_next_section = True
        skip_section_name = line.strip()
        continue
    if skip_until_next_section:
        # Check for section break or next section
        if line.strip().startswith("---") or line.strip().startswith("## ") or line.strip().startswith("### ") and "2-2" not in line and "3-2" not in line:
            skip_until_next_section = False
            new_c_lines.append(line)
        continue
    new_c_lines.append(line)

with open(c_path, "w", encoding="utf-8") as f:
    f.write("\r\n".join(new_c_lines) + "\r\n")
print(f"C group done: {c_path}")

# ========== D GROUP: Q7+Q7_1+Q7_2 합치기 ==========
print("\n=== D Group ===")

d_path = os.path.join(REPORT_DIR, "04_group_D.md")
with open(d_path, "r", encoding="utf-8") as f:
    d_content = f.read()
d_lines = [l.rstrip("\r") for l in d_content.split("\n")]

# Read existing Q7 responses (1-2, lines 26-48)
existing_d_q7 = {}
for line in d_lines[25:48]:
    cells = [c.strip() for c in line.split("|")]
    cells = [c for c in cells if c != ""]
    if len(cells) >= 4 and cells[0].isdigit():
        existing_d_q7[cells[1]] = cells[3]

# Read existing Q7_2 responses (3-2, lines 86-108)
existing_d_q72 = {}
for line in d_lines[85:108]:
    cells = [c.strip() for c in line.split("|")]
    cells = [c for c in cells if c != ""]
    if len(cells) >= 4 and cells[0].isdigit():
        existing_d_q72[cells[1]] = cells[3]

# Q7_1 responses (선호·우려) - manually from CSV analysis
d_q71 = {
    "금정(온산지점)": "주말 시간 우려",
    "동일메탈": "재직자의 참여 의지 중요",
    "드래곤엠앤이": "(응답 없음)",
    "세광기업": "직원들이 수용적→교육 시너지↓, 주말보상문제",
    "세영윈도우": "(응답 없음)",
    "아성정밀화학": "평일 온라인 접근성↑, 주말 집체는 심화에 유리, 피로 우려",
    "예광이엔지": "주말 직원 참여도 낮을 것 같음",
    "대송컨테이너항업": "근로자 참여도↓(주말 쉬기 원함)",
    "맑은기업": "주말 참여도 없음, 현실성 없음",
    "선경화성": "거의 대부분 참석X, 주말→참여도↓",
    "수성정밀": "평일 온라인은 시간 자유, 주말 집체 8시간 이내",
    "㈜스윅": "주말이 어려워 애로사항 큼",
    "㈜아일": "주말 집체 선호하지 않음, 온라인 선호",
    "에스엘티이": "관리직은 괜찮으나 현장직 문제, 주말 참여 힘듦",
    "케이에이알": "주말 참여도 문제",
    "한국후지필터": "주말 힘듦",
    "디비밸리": "업무 방해 안 되는 선에서, 인원 분산 수강",
    "㈜성전사": "상관없을 것 같음",
    "코스포영남파워": "주말 근무 태도 문제, 보상 필요",
    "한텍": "온라인 강조, 주말 참여도↓",
    "현대밋숀": "직원들이 참여하지 않을 것 같음",
}

# Build new 3-column D table
new_d_table = []
new_d_table.append("|  NO   | 기업명           | 규모      | 참여 과목·방식 (Q7)                                             | 선호·우려 (Q7_1)                                   | 대안 방식 (Q7_2)                                    |")
new_d_table.append("| :---: | ---------------- | --------- | --------------------------------------------------------------- | -------------------------------------------------- | --------------------------------------------------- |")

for i, (name, size) in enumerate(COMPANY_ORDER, 1):
    q7 = existing_d_q7.get(name, "(응답 없음)")
    q71 = d_q71.get(name, "-")
    q72 = existing_d_q72.get(name, "(응답 없음)")
    new_d_table.append(f"| {i:>3}   | {name:<16} | {size:<9} | {q7:<63} | {q71:<50} | {q72:<51} |")

# Replace old Q7 table (1-2, lines 26-48)
for i, line in enumerate(d_lines):
    if "### 1-2." in line:
        d_lines[i] = "### 1-2. 규모별 교육 방식·선호·대안 및 기업별 응답 (Q7, Q7_1, Q7_2)"
        break

d_lines[25:48] = new_d_table

# Remove standalone Q7_2 company table (3-2)
new_d_lines = []
skip = False
for i, line in enumerate(d_lines):
    if "### 3-2." in line:
        skip = True
        continue
    if skip:
        if line.strip().startswith("---") or line.strip().startswith("## "):
            skip = False
            new_d_lines.append(line)
        continue
    new_d_lines.append(line)

with open(d_path, "w", encoding="utf-8") as f:
    f.write("\r\n".join(new_d_lines) + "\r\n")
print(f"D group done: {d_path}")

print("\nAll done!")
