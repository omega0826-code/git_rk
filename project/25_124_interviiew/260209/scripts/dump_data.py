# -*- coding: utf-8 -*-
"""
원본 CSV → 파일 내보내기 (전체 데이터)
"""
import sys, io, csv
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CSV_PATH = r'd:\git_rk\project\25_124_interviiew\260209\data\(csv)interview_0209.csv'
OUT_PATH = r'd:\git_rk\project\25_124_interviiew\260209\REPORT\_raw_data_dump.txt'

with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

with open(OUT_PATH, 'w', encoding='utf-8') as out:
    out.write(f"총 기업 수: {len(rows)}\n")
    out.write(f"컬럼: {list(rows[0].keys())}\n\n")
    
    for i, row in enumerate(rows, 1):
        name = row.get('NAME','') or row.get('업체명','')
        out.write(f"=== [{i}] {name} ===\n")
        for k, v in row.items():
            val = v.strip() if v else ''
            if val:
                out.write(f"  {k}: {val}\n")
        out.write("\n")

print(f"저장 완료: {OUT_PATH}")
print(f"총 {len(rows)} 행")
