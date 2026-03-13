# -*- coding: utf-8 -*-
"""마크다운 파서 — 마크다운 테이블에서 설문조사 데이터 추출"""
import re


def parse_md_sections(md_path):
    """마크다운 파일을 ## 번호. 제목 기준으로 섹션 분리"""
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()
    sections = {}
    parts = re.split(r'\n## ', text)
    for part in parts[1:]:
        lines = part.strip().split('\n')
        title_line = lines[0].strip()
        m = re.match(r'^(\d+)\.\s*(.+)$', title_line)
        if m:
            idx = int(m.group(1))
            title = m.group(2).strip()
            sections[idx] = {'title': title, 'lines': lines[1:]}
    return sections


def parse_md_table(lines):
    """마크다운 테이블을 행 리스트로 파싱"""
    rows = []
    for line in lines:
        line = line.strip()
        if not line.startswith('|'):
            continue
        if re.match(r'^\|[\s:\-|]+\|$', line):
            continue
        cells = [c.strip() for c in line.split('|')[1:-1]]
        rows.append(cells)
    return rows


def _parse_pct(s):
    s = s.strip()
    return 0.0 if s in ('-', '', 'None') else float(s.replace('%', ''))


def _parse_num(s):
    s = s.strip()
    return 0 if s in ('-', '', 'None') else int(float(s.replace(',', '')))


def get_bar_data_md(section):
    """중복응답/순위 표에서 전체 행의 (항목명, 비율, 빈도) 추출"""
    rows = parse_md_table(section['lines'])
    if len(rows) < 2:
        return [], [], [], 0
    header = rows[0]
    total_row = rows[1]
    n = _parse_num(total_row[2])
    labels, pcts, freqs = [], [], []
    for i in range(3, len(header) - 1, 2):
        nm = re.sub(r'\(빈도\)$', '', header[i]).strip()
        if nm in ('빈도', '비율', '구 분'):
            continue
        if len(nm) > 22:
            nm = nm[:20] + "..."
        fv = _parse_num(total_row[i]) if i < len(total_row) else 0
        pv = _parse_pct(total_row[i + 1]) if i + 1 < len(total_row) else 0
        labels.append(nm)
        freqs.append(fv)
        pcts.append(pv)
    return labels, pcts, freqs, n


def get_pie1_md(section):
    """응답자 일반현황 (표1) — 소속 대학 기준 파이"""
    rows = parse_md_table(section['lines'])
    labels, vals = [], []
    for row in rows:
        if row[0].strip() == '소속 대학':
            labels.append(row[1].strip())
            vals.append(_parse_num(row[2]))
    total = sum(vals) if vals else 1
    pcts = [round(v / total * 100, 1) for v in vals]
    return labels, pcts, vals, int(total)


def get_radar_md(section):
    """평균 점수 → 레이더 차트"""
    rows = parse_md_table(section['lines'])
    if len(rows) < 2:
        return [], []
    header = rows[0]
    total_row = rows[1]
    labels, vals = [], []
    for i in range(2, len(header)):
        nm = header[i].strip()
        if nm in ('세부 항목',):
            continue
        if len(nm) > 14:
            nm = nm[:12] + "..."
        v = total_row[i].strip()
        if v in ('-', ''):
            continue
        labels.append(nm)
        vals.append(round(float(v), 2))
    return labels, vals


def get_stacked_md(section, top_n=10):
    """대학교별 데이터 → 누적 막대"""
    rows = parse_md_table(section['lines'])
    if len(rows) < 2:
        return [], {}, []
    header = rows[0]
    univs = [h.strip() for h in header[2:]]
    items = []
    data = {u: [] for u in univs}
    for row in rows[1:]:
        nm = row[0].strip()
        if nm in ('전 체', '전체'):
            continue
        m = re.match(r'^\d+\s+(.+)$', nm)
        name = m.group(1) if m else nm
        if len(name) > 20:
            name = name[:18] + "..."
        bv = _parse_num(row[1])
        if bv == 0:
            continue
        items.append(name)
        for ci, u in enumerate(univs):
            v = _parse_num(row[2 + ci]) if (2 + ci) < len(row) else 0
            data[u].append(v)
    totals = [sum(data[u][i] for u in univs) for i in range(len(items))]
    idx_s = sorted(range(len(items)), key=lambda i: totals[i], reverse=True)[:top_n]
    return [items[i] for i in idx_s], {u: [data[u][i] for i in idx_s] for u in univs}, univs
