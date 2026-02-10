# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
"""
보고서 마크다운 파일에서 모든 분석결과 표를 추출하여
개별 CSV 파일로 저장하고, 하나의 엑셀 파일로 통합합니다.
"""
import re
import os
import csv
import pandas as pd

REPORT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(REPORT_DIR, "csv_tables")
EXCEL_PATH = os.path.join(REPORT_DIR, "분석결과_전체표.xlsx")

# 추출 대상 파일과 시트 이름 매핑
FILES = [
    "01_group_A.md",
    "02_group_B.md",
    "03_group_C.md",
    "04_group_D.md",
]


def parse_md_tables(filepath):
    """마크다운 파일에서 모든 표를 추출합니다.
    
    Returns:
        list of (title, header_rows, data_rows)
        각 행은 셀 문자열 리스트
    """
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    tables = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\r\n")

        # 표 시작 감지: | 로 시작하는 줄
        if line.strip().startswith("|"):
            # 이전 줄에서 제목 찾기
            title = ""
            for back in range(1, 6):
                if i - back >= 0:
                    prev = lines[i - back].strip()
                    if prev.startswith("#"):
                        title = re.sub(r"^#+\s*", "", prev).strip()
                        break

            # 표 줄 수집
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].rstrip("\r\n"))
                i += 1

            # 파싱
            rows = []
            for tl in table_lines:
                # 구분선(---) 행은 건너뜀
                if re.match(r"^\|[\s\-:]+\|$", tl.replace(" ", "")):
                    continue
                cells = [c.strip() for c in tl.split("|")]
                # 양 끝 빈 문자열 제거 (|로 시작/끝)
                if cells and cells[0] == "":
                    cells = cells[1:]
                if cells and cells[-1] == "":
                    cells = cells[:-1]
                rows.append(cells)

            if rows:
                tables.append((title, rows))
        else:
            i += 1

    return tables


def merge_header_rows(rows):
    """2행 헤더(기업수/비율 서브헤더)를 1행으로 병합합니다."""
    if len(rows) < 2:
        return rows

    first_row = rows[0]
    second_row = rows[1]

    # 서브헤더 패턴 감지: 두 번째 행에 '기업수' 또는 '비율'이 포함
    has_subheader = any("기업수" in c or "비율" in c for c in second_row)

    if not has_subheader:
        return rows

    # 병합: 첫째 행의 카테고리명 + 둘째 행의 서브헤더 결합
    merged = []
    parent = ""
    for idx, cell in enumerate(first_row):
        if cell.strip():
            parent = cell.strip()

        if idx < len(second_row):
            sub = second_row[idx].strip()
            if sub in ("기업수", "비율"):
                merged.append(f"{parent}_{sub}")
            elif sub == "":
                merged.append(parent)
            else:
                merged.append(sub)
        else:
            merged.append(parent)

    return [merged] + rows[2:]


def save_table_csv(table_name, rows, csv_dir):
    """표를 CSV 파일로 저장합니다."""
    # 파일명 정리
    safe_name = re.sub(r"[^\w가-힣\s\-·]", "", table_name).strip()
    safe_name = re.sub(r"\s+", "_", safe_name)
    if not safe_name:
        safe_name = "table"

    filepath = os.path.join(csv_dir, f"{safe_name}.csv")

    # 중복 방지
    counter = 1
    base = filepath
    while os.path.exists(filepath):
        name, ext = os.path.splitext(base)
        filepath = f"{name}_{counter}{ext}"
        counter += 1

    merged = merge_header_rows(rows)

    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        for row in merged:
            writer.writerow(row)

    return filepath, safe_name, merged


def main():
    os.makedirs(CSV_DIR, exist_ok=True)

    all_sheets = {}  # sheet_name -> DataFrame
    csv_files = []

    for md_file in FILES:
        filepath = os.path.join(REPORT_DIR, md_file)
        if not os.path.exists(filepath):
            print(f"[SKIP] {md_file} 파일 없음")
            continue

        group_label = md_file.split("_")[0]  # 01, 02, 03, 04
        group_map = {"01": "A", "02": "B", "03": "C", "04": "D"}
        group = group_map.get(group_label, group_label)

        tables = parse_md_tables(filepath)
        print(f"\n[{md_file}] 표 {len(tables)}개 추출")

        for idx, (title, rows) in enumerate(tables, 1):
            csv_path, safe_name, merged = save_table_csv(
                f"{group}_{title}", rows, CSV_DIR
            )
            csv_files.append(csv_path)

            # 엑셀 시트명 (31자 제한)
            sheet_name = f"{group}_{title}"
            sheet_name = re.sub(r"[:\\/\?\*\[\]]", "", sheet_name)
            if len(sheet_name) > 31:
                sheet_name = sheet_name[:31]

            # 중복 시트명 방지
            base_sheet = sheet_name
            counter = 1
            while sheet_name in all_sheets:
                suffix = f"_{counter}"
                sheet_name = base_sheet[: 31 - len(suffix)] + suffix
                counter += 1

            # DataFrame 생성
            if len(merged) > 1:
                df = pd.DataFrame(merged[1:], columns=merged[0])
            else:
                df = pd.DataFrame(merged)

            all_sheets[sheet_name] = df
            print(f"  [{idx}] {title} → {os.path.basename(csv_path)}")

    # 엑셀 파일 생성
    if all_sheets:
        with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl") as writer:
            for sheet_name, df in all_sheets.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"\n✅ 엑셀 파일 저장 완료: {EXCEL_PATH}")
        print(f"   총 {len(all_sheets)}개 시트")

    print(f"\n✅ CSV 파일 {len(csv_files)}개 저장 완료: {CSV_DIR}")


if __name__ == "__main__":
    main()
