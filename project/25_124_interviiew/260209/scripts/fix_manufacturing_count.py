"""
제조업 기업 수 14 → 15 일괄 수정 스크립트
- 모든 보고서 파일(01~06, 05_summary)에서 제조업 행의 합계 14 → 15 수정
- 비율(%) 재계산: 각 기업수/15 로 재계산
- 05_summary.md: 제조업 (14개, 66.7%) → (15개, 71.4%)
- 00_integrated_report.md: 동일 패턴 수정
- wording 파일에서 42.9%, 21.4% 등 관련 비율 수정
"""
import re
import os

REPORT_DIR = r"d:\git_rk\project\25_124_interviiew\260209\REPORT"

def recalc_pct(n, total=15):
    """비율 계산 (소수점 1자리)"""
    if total == 0:
        return "0.0%"
    val = n / total * 100
    # 100%는 그대로
    if val == 100.0:
        return "100%"
    return f"{val:.1f}%"

def fix_table_row_manufacturing(line, old_total=14, new_total=15):
    """
    테이블 행에서 | 제조업 | 14 | ... 패턴을 찾아서 15로 수정하고 비율 재계산
    """
    # Match: | 제조업   | 14   | ... 
    # 제조업 뒤 공백, 14 뒤 공백 포함
    if '제조업' not in line:
        return line, False
    
    # 테이블 행인지 확인
    if not line.strip().startswith('|'):
        return line, False
    
    # 셀을 분리
    cells = line.split('|')
    if len(cells) < 4:
        return line, False
    
    # 제조업이 포함된 셀 찾기
    mfg_idx = None
    for i, cell in enumerate(cells):
        if '제조업' in cell.strip():
            mfg_idx = i
            break
    
    if mfg_idx is None:
        return line, False
    
    # 다음 셀이 합계(14)인지 확인
    total_idx = mfg_idx + 1
    if total_idx >= len(cells):
        return line, False
    
    total_val = cells[total_idx].strip()
    if total_val != str(old_total):
        return line, False
    
    # 합계를 15로 변경
    cells[total_idx] = cells[total_idx].replace(str(old_total), str(new_total))
    
    # 이후 셀에서 기업수, 비율 쌍을 찾아 비율 재계산
    i = total_idx + 1
    while i < len(cells) - 1:  # 마지막은 빈 문자열
        cell_val = cells[i].strip()
        
        # 기업수인지 확인 (숫자)
        try:
            count = int(cell_val)
            # 다음 셀이 비율(%)인지 확인
            if i + 1 < len(cells):
                pct_cell = cells[i + 1].strip()
                if '%' in pct_cell:
                    new_pct = recalc_pct(count, new_total)
                    # 원래 셀의 공백 패딩 유지
                    old_pct_stripped = pct_cell
                    cells[i + 1] = cells[i + 1].replace(old_pct_stripped, new_pct)
                    i += 2
                    continue
        except ValueError:
            pass
        i += 1
    
    new_line = '|'.join(cells)
    return new_line, True

def fix_summary_header(line):
    """05_summary.md: ### 제조업 (14개, 66.7%) → (15개, 71.4%)"""
    if '제조업' in line and '14개' in line:
        # 15/21 = 71.4%
        line = line.replace('14개', '15개')
        line = line.replace('66.7%', '71.4%')
        return line, True
    return line, False

def fix_wording_42_9(content):
    """wording 파일에서 제조업 관련 42.9% → 40.0% (6/15) 등 수정"""
    # 제조업의 오후 시간대 선호가 6개(42.9%) → 6개(40.0%)
    content = content.replace('6개(42.9%)', '6개(40.0%)')
    # "상관없음" 응답도 제조업에서 3개(21.4%) → 3개(20.0%)
    content = content.replace('3개(21.4%)', '3개(20.0%)')
    return content

def process_file(filepath):
    """파일 처리"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    
    lines = content.split('\n')
    changed = False
    changes = []
    
    new_lines = []
    for i, line in enumerate(lines):
        new_line = line
        was_changed = False
        
        # 테이블 행 처리
        new_line, was_changed = fix_table_row_manufacturing(line)
        
        # 05_summary.md 헤더 처리
        if not was_changed:
            new_line, was_changed = fix_summary_header(line)
        
        if was_changed:
            changed = True
            changes.append((i + 1, line.strip(), new_line.strip()))
        
        new_lines.append(new_line)
    
    if changed:
        new_content = '\n'.join(new_lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return changes
    return []

def process_wording_file(filepath):
    """wording 파일의 본문 텍스트 비율 수정"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    
    original = content
    content = fix_wording_42_9(content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    # 1. 보고서 파일 수정 (테이블 행)
    report_files = [
        '01_group_A.md',
        '02_group_B.md',
        '03_group_C.md',
        '04_group_D.md',
        '05_summary.md',
        '06_Q_ETC.md',
    ]
    
    print("=" * 70)
    print("제조업 기업수 14 → 15 일괄 수정")
    print("=" * 70)
    
    total_changes = 0
    for fname in report_files:
        fpath = os.path.join(REPORT_DIR, fname)
        if not os.path.exists(fpath):
            print(f"[SKIP] {fname} - 파일 없음")
            continue
        
        changes = process_file(fpath)
        if changes:
            print(f"\n[수정] {fname} ({len(changes)}건)")
            for line_no, old, new in changes:
                print(f"  L{line_no}:")
                print(f"    전: {old[:100]}")
                print(f"    후: {new[:100]}")
            total_changes += len(changes)
        else:
            print(f"[변경없음] {fname}")
    
    # 2. 00_integrated_report.md 처리
    integrated = os.path.join(REPORT_DIR, '00_integrated_report.md')
    if os.path.exists(integrated):
        changes = process_file(integrated)
        if changes:
            print(f"\n[수정] 00_integrated_report.md ({len(changes)}건)")
            for line_no, old, new in changes:
                print(f"  L{line_no}:")
                print(f"    전: {old[:100]}")
                print(f"    후: {new[:100]}")
            total_changes += len(changes)
        else:
            print(f"[변경없음] 00_integrated_report.md")
    
    # 3. wording 파일들 처리 (본문 텍스트 비율)
    wording_dir = os.path.join(REPORT_DIR, 'wording')
    if os.path.exists(wording_dir):
        for fname in os.listdir(wording_dir):
            if fname.endswith('.md') or fname.endswith('.txt'):
                fpath = os.path.join(wording_dir, fname)
                # 테이블 행 먼저
                changes = process_file(fpath)
                if changes:
                    print(f"\n[수정-테이블] wording/{fname} ({len(changes)}건)")
                    total_changes += len(changes)
                # 본문 텍스트 비율
                if process_wording_file(fpath):
                    print(f"[수정-본문] wording/{fname}")
                    total_changes += 1
    
    print(f"\n{'=' * 70}")
    print(f"총 수정: {total_changes}건")
    print("=" * 70)

if __name__ == '__main__':
    main()
