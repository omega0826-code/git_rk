# -*- coding: utf-8 -*-
"""
전체 그룹 보고서의 업종별 테이블을:
1. 행-열 전환 (업종이 행, 항목이 열)
2. 합계 열 추가
3. CSV 파일로 저장
"""
import re, csv, os

REPORT_DIR = r"d:\git_rk\project\25_124_interviiew\260209\REPORT"
CSV_DIR = os.path.join(REPORT_DIR, "csv_tables")
os.makedirs(CSV_DIR, exist_ok=True)

# 업종별 기업수
INDUSTRY_N = {"전체": 21, "제조업": 14, "건설업": 2, "서비스업": 1, "기타업": 3}
INDUSTRIES = ["전체", "제조업", "건설업", "서비스업", "기타업"]

def parse_industry_table(lines):
    """Parse a markdown table with industry columns, return (categories, data_dict)"""
    # lines[0] = header row with category names
    # lines[1] = separator
    # lines[2] = sub-header (기업수/비율)
    # lines[3:] = data rows
    
    # Parse header to get category column name
    # Parse data rows
    categories = []
    data = {}  # category -> {industry: (count, pct)}
    
    for line in lines[3:]:
        cells = [c.strip() for c in line.split("|")]
        cells = [c for c in cells if c != ""]
        if len(cells) < 3:
            continue
        cat_name = cells[0]
        categories.append(cat_name)
        
        # Each industry has 2 cells: count, pct
        idx = 1
        for ind in INDUSTRIES:
            if idx + 1 < len(cells):
                count = cells[idx].strip()
                pct = cells[idx + 1].strip()
                if ind not in data:
                    data[ind] = {}
                data[ind][cat_name] = (count, pct)
                idx += 2
            else:
                if ind not in data:
                    data[ind] = {}
                data[ind][cat_name] = ("0", "0.0%")
    
    return categories, data

def build_transposed_md(categories, data, col_width=None):
    """Build a transposed markdown table with 합계 column."""
    # Header row
    header = "| 구분     | 합계 |"
    sep = "| -------- | ---- |"
    sub = "|          |      |"
    
    for cat in categories:
        header += f" {cat} |       |"
        sep += " " + "-" * max(len(cat.encode('utf-8'))//2, 6) + " | ----- |"
        sub += f" 기업수 | 비율  |"
    
    # Simplify separator
    parts_h = header.split("|")
    parts_count = len([p for p in parts_h if p.strip() != ""])
    sep = "| " + " | ".join(["--------" if i == 0 else "----" if i == 1 else "------" if i % 2 == 0 else "-----" for i in range(parts_count)]) + " |"
    
    # Actually, let's build it more carefully
    lines = []
    
    # Header
    h = "| 구분     | 합계 "
    for cat in categories:
        h += f"| {cat} |       "
    h += "|"
    lines.append(h)
    
    # Separator
    s = "| -------- | ---- "
    for cat in categories:
        cat_w = max(len(cat), 4)
        s += f"| {'-'*cat_w} | ----- "
    s += "|"
    lines.append(s)
    
    # Sub-header
    sh = "|          |      "
    for cat in categories:
        cat_w = max(len(cat), 4)
        sh += f"| {'기업수'.ljust(cat_w)} | 비율  "
    sh += "|"
    lines.append(sh)
    
    # Data rows
    for ind in INDUSTRIES:
        n = INDUSTRY_N[ind]
        row = f"| {ind.ljust(8)} | {str(n).ljust(4)} "
        for cat in categories:
            count, pct = data.get(ind, {}).get(cat, ("0", "0.0%"))
            cat_w = max(len(cat), 4)
            row += f"| {str(count).ljust(cat_w)} | {pct.ljust(5)} "
        row += "|"
        lines.append(row)
    
    return "\r\n".join(lines)

def save_csv(filename, categories, data):
    """Save table to CSV file with UTF-8 BOM."""
    filepath = os.path.join(CSV_DIR, filename)
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        # Header
        header = ["구분", "합계"]
        for cat in categories:
            header.extend([f"{cat}_기업수", f"{cat}_비율"])
        writer.writerow(header)
        # Data
        for ind in INDUSTRIES:
            row = [ind, INDUSTRY_N[ind]]
            for cat in categories:
                count, pct = data.get(ind, {}).get(cat, ("0", "0.0%"))
                row.extend([count, pct])
            writer.writerow(row)
    print(f"  CSV 저장: {filepath}")

def process_file(filepath, table_defs):
    """
    table_defs: list of (section_name, start_line, end_line)
    start_line, end_line are 1-indexed
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    lines = content.split("\n")
    # Normalize line endings
    lines = [l.rstrip("\r") for l in lines]
    
    basename = os.path.basename(filepath).replace(".md", "")
    
    # Process tables in reverse order (so line numbers stay valid)
    for section_name, start, end in reversed(table_defs):
        table_lines = lines[start-1:end]
        
        print(f"\n처리 중: {basename} / {section_name} (lines {start}-{end})")
        
        categories, data = parse_industry_table(table_lines)
        print(f"  항목: {categories}")
        
        # Build transposed markdown
        new_md = build_transposed_md(categories, data)
        new_lines = new_md.split("\r\n")
        
        # Replace in file
        lines[start-1:end] = new_lines
        
        # Save CSV
        csv_name = f"{basename}_{section_name}.csv"
        save_csv(csv_name, categories, data)
    
    # Write back
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\r\n".join(lines) + "\r\n")
    
    print(f"\n[완료] {filepath} 저장 완료")

# Also save 01_group_A tables that were already transposed
def save_existing_a_tables():
    """Save already-transposed A group tables to CSV."""
    filepath = os.path.join(REPORT_DIR, "01_group_A.md")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    lines = content.split("\n")
    lines = [l.rstrip("\r") for l in lines]
    
    # 1-1: lines 15-22 (already transposed with 합계)
    # 1-2: lines 26-33  
    # 2-1: lines 88-95
    for name, start, end in [("1-1_선호시간대", 15, 22), ("1-2_회피시기", 26, 33), ("2-1_애로사항", 88, 95)]:
        table_lines = lines[start-1:end]
        # These are already transposed: rows = industries, cols = categories
        # Parse differently
        # Header has category names
        header_cells = [c.strip() for c in table_lines[0].split("|")]
        header_cells = [c for c in header_cells if c != ""]
        # header_cells[0] = 구분, header_cells[1] = 합계, then pairs of category names
        categories = []
        i = 2
        while i < len(header_cells):
            categories.append(header_cells[i])
            i += 2  # skip the empty pair column
        
        data = {}
        for line in table_lines[3:]:
            cells = [c.strip() for c in line.split("|")]
            cells = [c for c in cells if c != ""]
            if len(cells) < 3:
                continue
            ind = cells[0]
            # n = cells[1]  # 합계
            idx = 2
            if ind not in data:
                data[ind] = {}
            for cat in categories:
                if idx + 1 < len(cells):
                    data[ind][cat] = (cells[idx], cells[idx+1])
                    idx += 2
        
        csv_name = f"01_group_A_{name}.csv"
        save_csv(csv_name, categories, data)

# ============ Define all tables ============

# 02_group_B.md
B_TABLES = [
    ("1-1_반복수강여부", 11, 16),
    ("2-1_강사변경영향", 56, 61),
    ("3-1_재수강의향", 71, 76),
    ("4-1_반복필요주제", 86, 94),
]

# 03_group_C.md
C_TABLES = [
    ("1-1_교육효과지원", 11, 19),
    ("2-1_AI적용현황", 55, 60),
    ("3-1_AI디지털필수교육", 96, 104),
]

# 04_group_D.md
D_TABLES = [
    ("1-1_교육방식선호", 11, 17),
    ("2-1_선호우려", 57, 63),
    ("3-1_대안방식", 73, 79),
]

# 06_Q_ETC.md
ETC_TABLES = [
    ("2-1_정책제도", 19, 24),
    ("2-2_콘텐츠수준", 36, 41),
]

# ============ Execute ============
print("=" * 60)
print("업종별 테이블 전환 + 합계열 추가 + CSV 저장")
print("=" * 60)

# A, B는 이미 처리 완료 → 건너뜀
# print("\n--- 01_group_A (CSV만 저장) ---")
# save_existing_a_tables()
# print("\n--- 02_group_B ---")
# process_file(os.path.join(REPORT_DIR, "02_group_B.md"), B_TABLES)

print("\n--- 03_group_C ---")
process_file(os.path.join(REPORT_DIR, "03_group_C.md"), C_TABLES)

print("\n--- 04_group_D ---")
process_file(os.path.join(REPORT_DIR, "04_group_D.md"), D_TABLES)

print("\n--- 06_Q_ETC ---")
process_file(os.path.join(REPORT_DIR, "06_Q_ETC.md"), ETC_TABLES)

print("\n" + "=" * 60)
print("모든 처리 완료!")
print(f"CSV 파일 위치: {CSV_DIR}")
print("=" * 60)
