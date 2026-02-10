# -*- coding: utf-8 -*-
"""
원본 CSV 데이터를 분석하여 통합보고서용 데이터를 모두 추출하는 스크립트
"""
import sys, io, csv, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CSV_PATH = r'd:\git_rk\project\25_124_interviiew\260209\data\(csv)interview_0209.csv'

# CSV 로드
with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"총 기업 수: {len(rows)}")
print(f"컬럼: {list(rows[0].keys())}")
print()

# 각 기업 출력
for i, row in enumerate(rows, 1):
    print(f"=== [{i}] {row.get('NAME','')} ===")
    for k, v in row.items():
        val = v.strip() if v else ''
        if val:
            print(f"  {k}: {val}")
    print()
