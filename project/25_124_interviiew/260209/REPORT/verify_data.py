# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

files = [
    r'd:\git_rk\project\25_124_interviiew\260209\REPORT\01_group_A.md',
    r'd:\git_rk\project\25_124_interviiew\260209\REPORT\02_group_B.md',
    r'd:\git_rk\project\25_124_interviiew\260209\REPORT\03_group_C.md',
    r'd:\git_rk\project\25_124_interviiew\260209\REPORT\04_group_D.md',
]

errors = []
warnings = []

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    fname = fpath.split('\\')[-1]

    i = 0
    current_section = ""
    company_count = 0
    in_company_table = False

    while i < len(lines):
        line = lines[i].rstrip('\r\n')

        # Track section titles
        if line.strip().startswith('#'):
            current_section = re.sub(r'^#+\s*', '', line.strip())
            in_company_table = False
            company_count = 0

        # Detect company table (NO column)
        if re.search(r'\|\s*:?---', line):
            # Check previous line for NO header
            if i > 0 and 'NO' in lines[i-1]:
                in_company_table = True
                company_count = 0
            i += 1
            continue

        # Count companies in company table
        if in_company_table and line.strip().startswith('|'):
            cells = [c.strip() for c in line.split('|')]
            cells = [c for c in cells if c]
            if cells and cells[0].isdigit():
                company_count += 1
            elif not line.strip().startswith('|'):
                if company_count > 0 and company_count != 21:
                    errors.append(f'{fname} | {current_section} | 기업수={company_count} (21 아님)')
                in_company_table = False

        # Industry table data rows
        if line.strip().startswith('|'):
            cells = [c.strip() for c in line.split('|')]
            cells = [c for c in cells if c]

            if len(cells) >= 3 and cells[0] in ('전체', '제조업', '건설업', '서비스업', '기타업'):
                try:
                    total = int(cells[1])
                except ValueError:
                    i += 1
                    continue

                # Check percentage calculations
                for j in range(2, len(cells)):
                    if '%' in cells[j]:
                        pct_str = cells[j].replace('%', '').strip()
                        try:
                            pct = float(pct_str)
                            if j >= 3:
                                try:
                                    count = int(cells[j-1])
                                    expected = round(count / total * 100, 1)
                                    if abs(pct - expected) > 0.15:
                                        errors.append(
                                            f'{fname} | {current_section} | {cells[0]} col{j}: '
                                            f'{count}/{total}={expected}% but shown {pct}%'
                                        )
                                except ValueError:
                                    pass
                        except ValueError:
                            pass

            # Subtotal check: 제조+건설+서비스+기타 == 전체-기타분류?
            if cells[0] == '전체':
                try:
                    total_n = int(cells[1])
                    sub = 0
                    for k in range(1, 5):
                        if i+k < len(lines):
                            sub_line = lines[i+k].rstrip('\r\n')
                            sub_cells = [c.strip() for c in sub_line.split('|')]
                            sub_cells = [c for c in sub_cells if c]
                            if sub_cells and sub_cells[0] in ('제조업','건설업','서비스업','기타업'):
                                try:
                                    sub += int(sub_cells[1])
                                except ValueError:
                                    pass
                    if sub > 0 and sub != total_n:
                        errors.append(
                            f'{fname} | {current_section} | 업종합계({sub}) != 전체({total_n})'
                        )
                except ValueError:
                    pass

        i += 1

    # Final company table check
    if in_company_table and company_count > 0 and company_count != 21:
        errors.append(f'{fname} | {current_section} | 기업수={company_count} (21 아님)')

print('='*60)
print('보고서 데이터 정합성 검증 결과')
print('='*60)

if errors:
    print(f'\n[오류] {len(errors)}건:')
    for e in errors:
        print(f'  - {e}')
else:
    print('\n[OK] 오류 없음!')

print(f'\n검증 항목:')
print(f'  - 업종별 합계 (제조+건설+서비스+기타 == 전체) 검증')
print(f'  - 비율 계산 (기업수/합계*100) 정확성 검증')
print(f'  - 기업별 테이블 21개 기업 포함 여부 검증')
