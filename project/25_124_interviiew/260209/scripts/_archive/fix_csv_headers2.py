# -*- coding: utf-8 -*-
"""
1) fix_a_csv.py 재실행하여 A그룹 원본 CSV 복원
2) transpose_tables.py의 save_csv 로직으로 B/C/D/ETC 원본 CSV 복원
3) 전체 CSV에서 헤더만 정리: _기업수, _비율 접미사 제거
"""
import csv, os, glob

CSV_DIR = r"d:\git_rk\project\25_124_interviiew\260209\REPORT\csv_tables"
REPORT_DIR = r"d:\git_rk\project\25_124_interviiew\260209\REPORT"
INDUSTRIES = ["전체", "제조업", "건설업", "서비스업", "기타업"]
INDUSTRY_N = {"전체": 21, "제조업": 14, "건설업": 2, "서비스업": 1, "기타업": 3}

def write_csv(filename, header, rows):
    fp = os.path.join(CSV_DIR, filename)
    with open(fp, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)

def parse_transposed_table_from_md(filepath, start, end):
    """Read a transposed table (industries as rows) from md file."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")
    lines = [l.rstrip("\r") for l in lines]
    table_lines = lines[start-1:end]
    
    # Parse header to get categories (skip 구분 and 합계)
    header_cells = [c.strip() for c in table_lines[0].split("|")]
    header_cells = [c for c in header_cells if c != ""]
    # header_cells: [구분, 합계, cat1, (empty), cat2, (empty), ...]
    categories = []
    i = 2
    while i < len(header_cells):
        if header_cells[i]:
            categories.append(header_cells[i])
        i += 2
    
    # Parse data rows
    data = {}
    for line in table_lines[3:]:
        cells = [c.strip() for c in line.split("|")]
        cells = [c for c in cells if c != ""]
        if len(cells) < 3:
            continue
        ind = cells[0]
        data[ind] = {}
        idx = 2
        for cat in categories:
            if idx + 1 < len(cells):
                data[ind][cat] = (cells[idx], cells[idx+1])
                idx += 2
    
    return categories, data

def gen_csv_with_clean_headers(filename, categories, data):
    """Generate CSV with clean headers (no _기업수/_비율 suffixes)."""
    header = ["구분", "합계"]
    for cat in categories:
        header.append(cat)  # was _기업수
        header.append(cat)  # was _비율 - same name, user just wants suffix removed
    
    # Actually, having duplicate column names is bad for CSV
    # The user wants: remove _비율 and _기업수 from header text
    # So each category appears twice with no suffix
    # But that creates duplicates. Let me just remove suffixes.
    # Actually rethinking: the user said "비율의 헤드라인만 삭제" - 
    # meaning just remove the header label for 비율 columns (make them empty or same as category?)
    # And "_기업수 라는 부분도 삭제" - remove _기업수 suffix
    # 
    # So the header would be: 구분, 합계, 오후(13~17시), , 상관없음, , ...
    # Where 비율 columns have empty headers
    
    header = ["구분", "합계"]
    for cat in categories:
        header.append(cat)   # 기업수 column - just category name
        header.append("")    # 비율 column - empty header
    
    rows = []
    for ind in INDUSTRIES:
        n = INDUSTRY_N[ind]
        row = [ind, n]
        for cat in categories:
            count, pct = data.get(ind, {}).get(cat, ("0", "0.0%"))
            row.append(count)
            row.append(pct)
        rows.append(row)
    
    write_csv(filename, header, rows)
    print(f"OK: {filename}")

# ===== A그룹 직접 생성 =====
print("--- A group ---")

a_data_11 = {
    "전체": {"오후(13~17시)": ("9","42.9%"), "상관없음": ("5","23.8%"), "퇴근 후(18시~)": ("2","9.5%"), "주말": ("3","14.3%"), "온라인(시간무관)": ("2","9.5%")},
    "제조업": {"오후(13~17시)": ("6","42.9%"), "상관없음": ("3","21.4%"), "퇴근 후(18시~)": ("2","14.3%"), "주말": ("2","14.3%"), "온라인(시간무관)": ("1","7.1%")},
    "건설업": {"오후(13~17시)": ("1","50.0%"), "상관없음": ("1","50.0%"), "퇴근 후(18시~)": ("0","0.0%"), "주말": ("0","0.0%"), "온라인(시간무관)": ("0","0.0%")},
    "서비스업": {"오후(13~17시)": ("0","0.0%"), "상관없음": ("0","0.0%"), "퇴근 후(18시~)": ("0","0.0%"), "주말": ("1","100%"), "온라인(시간무관)": ("0","0.0%")},
    "기타업": {"오후(13~17시)": ("2","66.7%"), "상관없음": ("1","33.3%"), "퇴근 후(18시~)": ("0","0.0%"), "주말": ("0","0.0%"), "온라인(시간무관)": ("1","33.3%")},
}
gen_csv_with_clean_headers("01_group_A_1-1_선호시간대.csv", ["오후(13~17시)","상관없음","퇴근 후(18시~)","주말","온라인(시간무관)"], a_data_11)

a_data_12 = {
    "전체": {"연초연말": ("8","38.1%"), "월요일": ("4","19.0%"), "주말": ("4","19.0%"), "월초월말": ("2","9.5%"), "금요일": ("1","4.8%")},
    "제조업": {"연초연말": ("7","50.0%"), "월요일": ("4","28.6%"), "주말": ("4","28.6%"), "월초월말": ("1","7.1%"), "금요일": ("0","0.0%")},
    "건설업": {"연초연말": ("0","0.0%"), "월요일": ("0","0.0%"), "주말": ("0","0.0%"), "월초월말": ("1","50.0%"), "금요일": ("0","0.0%")},
    "서비스업": {"연초연말": ("1","100%"), "월요일": ("0","0.0%"), "주말": ("0","0.0%"), "월초월말": ("0","0.0%"), "금요일": ("0","0.0%")},
    "기타업": {"연초연말": ("0","0.0%"), "월요일": ("0","0.0%"), "주말": ("0","0.0%"), "월초월말": ("0","0.0%"), "금요일": ("1","33.3%")},
}
gen_csv_with_clean_headers("01_group_A_1-2_회피시기.csv", ["연초연말","월요일","주말","월초월말","금요일"], a_data_12)

a_data_21 = {
    "전체": {"시간확보어려움": ("12","57.1%"), "참여도저조": ("7","33.3%"), "대체인력부족": ("4","19.0%"), "콘텐츠부적합": ("5","23.8%"), "비용인센티브": ("4","19.0%"), "교통접근성": ("2","9.5%"), "없음": ("2","9.5%")},
    "제조업": {"시간확보어려움": ("8","57.1%"), "참여도저조": ("5","35.7%"), "대체인력부족": ("3","21.4%"), "콘텐츠부적합": ("3","21.4%"), "비용인센티브": ("3","21.4%"), "교통접근성": ("1","7.1%"), "없음": ("1","7.1%")},
    "건설업": {"시간확보어려움": ("1","50.0%"), "참여도저조": ("0","0.0%"), "대체인력부족": ("0","0.0%"), "콘텐츠부적합": ("0","0.0%"), "비용인센티브": ("0","0.0%"), "교통접근성": ("1","50.0%"), "없음": ("1","50.0%")},
    "서비스업": {"시간확보어려움": ("1","100%"), "참여도저조": ("0","0.0%"), "대체인력부족": ("1","100%"), "콘텐츠부적합": ("0","0.0%"), "비용인센티브": ("1","100%"), "교통접근성": ("0","0.0%"), "없음": ("0","0.0%")},
    "기타업": {"시간확보어려움": ("2","66.7%"), "참여도저조": ("2","66.7%"), "대체인력부족": ("0","0.0%"), "콘텐츠부적합": ("2","66.7%"), "비용인센티브": ("0","0.0%"), "교통접근성": ("0","0.0%"), "없음": ("0","0.0%")},
}
gen_csv_with_clean_headers("01_group_A_2-1_애로사항.csv", ["시간확보어려움","참여도저조","대체인력부족","콘텐츠부적합","비용인센티브","교통접근성","없음"], a_data_21)

# ===== B/C/D/ETC: Read from already-transposed MD files =====
print("\n--- B/C/D/ETC groups ---")

file_tables = {
    "02_group_B.md": [
        ("1-1_반복수강여부", 11, 18),
        ("2-1_강사변경영향", 58, 65),
        ("3-1_재수강의향", 73, 80),
        ("4-1_반복필요주제", 88, 97),
    ],
    "03_group_C.md": [
        ("1-1_교육효과지원", 11, 18),
        ("2-1_AI적용현황", 56, 62),
        ("3-1_AI디지털필수교육", 97, 106),
    ],
    "04_group_D.md": [
        ("1-1_교육방식선호", 11, 18),
        ("2-1_선호우려", 57, 64),
        ("3-1_대안방식", 73, 80),
    ],
    "06_Q_ETC.md": [
        ("2-1_정책제도", 19, 26),
        ("2-2_콘텐츠수준", 38, 44),
    ],
}

for md_file, tables in file_tables.items():
    md_path = os.path.join(REPORT_DIR, md_file)
    basename = md_file.replace(".md", "")
    for tbl_name, start, end in tables:
        try:
            categories, data = parse_transposed_table_from_md(md_path, start, end)
            csv_name = f"{basename}_{tbl_name}.csv"
            gen_csv_with_clean_headers(csv_name, categories, data)
        except Exception as e:
            print(f"ERR: {basename}/{tbl_name}: {e}")

print("\nDone! All CSV files restored with clean headers.")
