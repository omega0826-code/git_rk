# -*- coding: utf-8 -*-
"""CSV 파일들을 엑셀 시트별로 합치기"""
import pandas as pd
import glob, os

CSV_DIR = r"d:\git_rk\project\25_124_interviiew\260209\REPORT\csv_tables"
OUT = r"d:\git_rk\project\25_124_interviiew\260209\REPORT\tables_all.xlsx"

files = sorted(glob.glob(os.path.join(CSV_DIR, "*.csv")))

with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
    for fp in files:
        name = os.path.basename(fp).replace(".csv", "")
        # Excel sheet name max 31 chars
        sheet = name[:31]
        df = pd.read_csv(fp, encoding="utf-8-sig")
        df.to_excel(writer, sheet_name=sheet, index=False)
        print(f"OK: {sheet}")

print(f"\nSaved: {OUT}")
