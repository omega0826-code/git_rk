# -*- coding: utf-8 -*-
import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pdfplumber

for fname in ['2025년 전자산업 표본할당.pdf', '2025년 IoT가전 표본할당.pdf']:
    fpath = rf"d:\git_rk\project\26_supply_demand\sample_allocation\{fname}"
    print(f"\n{'='*80}")
    print(f"FILE: {fname}")
    print('='*80)
    with pdfplumber.open(fpath) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"\n--- Page {i+1} ---")
            text = page.extract_text()
            if text:
                print(text[:2000])
            tables = page.extract_tables()
            for j, table in enumerate(tables):
                print(f"\n  [Table {j+1}]")
                for row in table:
                    print(f"  {row}")
