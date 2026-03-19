# -*- coding: utf-8 -*-
"""
표본할당표 대비 보유현황 집계 스크립트
- 전자산업 할당표 대비 보유현황
- IoT가전 할당표 대비 보유현황 (분류 유형별 세분화)
"""
import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import os
from datetime import datetime

# ========================================
# 파일 경로
# ========================================
BASE_DIR = r"d:\git_rk\data\factory_on\202601\company_list\electronics_iot"
INPUT_DIR = os.path.join(BASE_DIR, "260319_1204")
INPUT_FILE = os.path.join(INPUT_DIR, "company_electronics_iot_employees_10_and_over_F_260319_1204.csv")

print("[INFO] Loading CSV...")
df = pd.read_csv(INPUT_FILE, encoding='utf-8-sig')
total = len(df)
print(f"[INFO] Total rows: {total}")

# ========================================
# 종업원 규모 그룹 정의
# ========================================
size_order = ['10~29인', '30~99인', '100~299인', '300인+']

def map_size(s):
    s = str(s).strip()
    if s in ['10~29인']:
        return '10~29인'
    elif s in ['30~99인']:
        return '30~99인'
    elif s in ['100~299인']:
        return '100~299인'
    elif s in ['300~499인', '500~999인', '1000인 이상', '300인 이상', '300인+']:
        return '300인+'
    return None

df['종업원규모_그룹'] = df['종업원규모'].apply(map_size)

# ========================================
# 할당표 (기존 보고서 기준 고정값)
# ========================================
# 전자산업 할당표
electronics_alloc = {
    '전자부품':         {'10~29인': 22, '30~99인': 13, '100~299인': 11, '300인+': 17},
    '컴퓨터주변기기':   {'10~29인': 12, '30~99인': 10, '100~299인': 4,  '300인+': 1},
    '방송통신장비':     {'10~29인': 16, '30~99인': 9,  '100~299인': 7,  '300인+': 5},
    '영상음향기기':     {'10~29인': 12, '30~99인': 10, '100~299인': 7,  '300인+': 1},
    '측정제어분석기기': {'10~29인': 28, '30~99인': 14, '100~299인': 10, '300인+': 8},
    '전기장비':         {'10~29인': 55, '30~99인': 23, '100~299인': 23, '300인+': 32},
}

# IoT가전 할당표
iot_alloc = {
    '지능형 가전':             {'10~29인': 54, '30~99인': 25, '100~299인': 14, '300인+': 10},
    '홈헬스케어':              {'10~29인': 11, '30~99인': 7,  '100~299인': 3,  '300인+': 1},
    '홈네트워크 및 주거안전':  {'10~29인': 57, '30~99인': 20, '100~299인': 5,  '300인+': 3},
    '홈에너지':                {'10~29인': 28, '30~99인': 7,  '100~299인': 2,  '300인+': 3},
}

# ========================================
# 1. 전자산업 보유현황 집계
# ========================================
print("\n[STEP 1] Electronics industry aggregation...")

# 전자산업_대분류가 있는 행만
df_elec = df[df['업종_전자산업'] == 'O'].copy()
print(f"[INFO] Electronics rows (업종_전자산업=O): {len(df_elec)}")

# 대분류별 집계
elec_categories = ['전자부품', '컴퓨터주변기기', '방송통신장비', '영상음향기기', '측정제어분석기기', '전기장비']
elec_results = {}

for cat in elec_categories:
    subset = df_elec[df_elec['전자산업_대분류'] == cat]
    counts = {}
    for size in size_order:
        counts[size] = len(subset[subset['종업원규모_그룹'] == size])
    counts['합계'] = sum(counts.values())
    elec_results[cat] = counts

# 합계 행
elec_total = {}
for size in size_order + ['합계']:
    elec_total[size] = sum(elec_results[cat][size] for cat in elec_categories)
elec_results['합계'] = elec_total

# ========================================
# 2. IoT가전 보유현황 집계 (분류 유형별)
# ========================================
print("\n[STEP 2] IoT appliance aggregation...")

# 예상_근거에서 대분류 추출
iot_major_map = {
    '지능형 가전': ['지능형 가전'],
    '홈헬스케어': ['홈헬스케어'],
    '홈네트워크 및 주거안전': ['홈네트워크 및 주거안전'],
    '홈에너지': ['홈에너지'],
}

# 가전IoT_예상이 확정/예상/모호인 행만
df_iot = df[df['가전IoT_예상'].str.contains('확정|예상|모호', na=False)].copy()
print(f"[INFO] IoT related rows: {len(df_iot)}")

# 확정 = 확정(이전조사) + 확정(KEA추가)
df_iot['is_confirmed'] = df_iot['가전IoT_예상'].str.contains('확정', na=False)
df_iot['is_expected'] = df_iot['가전IoT_예상'] == '예상'
df_iot['is_ambiguous'] = df_iot['가전IoT_예상'] == '모호'

# 대분류 매칭 (예상_근거에서 추출)
def extract_iot_major(reason):
    """예상_근거 문자열에서 IoT 대분류 추출"""
    if pd.isna(reason) or str(reason).strip() == '':
        return '미분류'
    reason = str(reason)
    # 우선순위: 명시적 매칭
    for major, keywords in iot_major_map.items():
        for kw in keywords:
            if kw in reason:
                return major
    return '미분류'

df_iot['iot_대분류'] = df_iot['예상_근거'].apply(extract_iot_major)

# 확정 건도 대분류를 매칭 시도
# 확정인데 미분류인 경우 → 이전조사 참여업체이므로 업종 기반으로 추정
# 다만, 정확한 분류 근거가 없으면 미분류로 유지

# 대분류별 집계
iot_categories = ['지능형 가전', '홈헬스케어', '홈네트워크 및 주거안전', '홈에너지']
iot_results = {}

for cat in iot_categories:
    subset = df_iot[df_iot['iot_대분류'] == cat]
    counts = {'확정': {}, '예상': {}, '모호': {}, '소계': {}}
    for size in size_order:
        size_subset = subset[subset['종업원규모_그룹'] == size]
        counts['확정'][size] = len(size_subset[size_subset['is_confirmed']])
        counts['예상'][size] = len(size_subset[size_subset['is_expected']])
        counts['모호'][size] = len(size_subset[size_subset['is_ambiguous']])
        counts['소계'][size] = counts['확정'][size] + counts['예상'][size] + counts['모호'][size]
    for key in counts:
        counts[key]['합계'] = sum(counts[key].values())
    iot_results[cat] = counts

# 미분류 (대분류가 없는 확정 건 포함)
subset_unclass = df_iot[df_iot['iot_대분류'] == '미분류']
iot_unclassified = {'확정': {}, '예상': {}, '모호': {}, '소계': {}}
for size in size_order:
    size_subset = subset_unclass[subset_unclass['종업원규모_그룹'] == size]
    iot_unclassified['확정'][size] = len(size_subset[size_subset['is_confirmed']])
    iot_unclassified['예상'][size] = len(size_subset[size_subset['is_expected']])
    iot_unclassified['모호'][size] = len(size_subset[size_subset['is_ambiguous']])
    iot_unclassified['소계'][size] = iot_unclassified['확정'][size] + iot_unclassified['예상'][size] + iot_unclassified['모호'][size]
for key in iot_unclassified:
    iot_unclassified[key]['합계'] = sum(iot_unclassified[key].values())

# 합계 행
iot_total = {'확정': {}, '예상': {}, '모호': {}, '소계': {}}
for size in size_order + ['합계']:
    for key in iot_total:
        val = sum(iot_results[cat][key].get(size, 0) for cat in iot_categories)
        val += iot_unclassified[key].get(size, 0)
        iot_total[key][size] = val
iot_results['합계'] = iot_total

# ========================================
# 마크다운 생성
# ========================================
print("\n[STEP 3] Generating markdown report...")

def fmt(n):
    """숫자 포맷: 1000 이상이면 콤마"""
    if n >= 1000:
        return f"{n:,}"
    return str(n)

def fmt_diff(n):
    """여유분 포맷"""
    if n >= 0:
        return f"+{fmt(n)}"
    return f"{fmt(n)}"

lines = []
lines.append("# 표본할당표 대비 보유현황 비교")
lines.append("")
lines.append(f"> **작성일**: {datetime.now().strftime('%Y-%m-%d')} | **데이터**: `260319_1204`")
lines.append("")
lines.append("---")
lines.append("")

# 1. 전자산업
lines.append("## 1. 전자산업 할당표 대비 보유현황")
lines.append("")
lines.append("| 대분류 | 구분 | 10~29인 | 30~99인 | 100~299인 | 300인+ | 합계 |")
lines.append("|--------|------|---------|---------|-----------|--------|------|")

labels = {'전자부품': '전자부품', '컴퓨터주변기기': '컴퓨터주변기기', '방송통신장비': '방송통신장비',
          '영상음향기기': '영상음향기기', '측정제어분석기기': '측정제어분석기기', '전기장비': '전기장비'}
nums = {'전자부품': '1', '컴퓨터주변기기': '2', '방송통신장비': '3',
        '영상음향기기': '4', '측정제어분석기기': '5', '전기장비': '6'}

for cat in elec_categories + ['합계']:
    alloc = electronics_alloc.get(cat, None)
    hold = elec_results[cat]
    
    if cat == '합계':
        cat_label = '**합계**'
        # 합계 할당
        alloc_vals = {}
        for size in size_order:
            alloc_vals[size] = sum(electronics_alloc[c].get(size, 0) for c in elec_categories)
        alloc_vals['합계'] = sum(alloc_vals.values())
    else:
        n = nums[cat]
        circled = chr(0x2460 + int(n) - 1)  # ①②③...
        cat_label = f"**{circled} {cat}**"
        alloc_vals = dict(alloc)
        alloc_vals['합계'] = sum(alloc.values())
    
    # 할당 행
    a_cells = [fmt(alloc_vals.get(s, 0)) for s in size_order]
    a_total = fmt(alloc_vals['합계'])
    lines.append(f"| {cat_label} | 할당 | {a_cells[0]} | {a_cells[1]} | {a_cells[2]} | {a_cells[3]} | **{a_total}** |")
    
    # 보유 행
    h_cells = [fmt(hold.get(s, 0)) for s in size_order]
    h_total = fmt(hold['합계'])
    lines.append(f"| | 보유 | {h_cells[0]} | {h_cells[1]} | {h_cells[2]} | {h_cells[3]} | **{h_total}** |")
    
    # 여유 행
    d_cells = [fmt_diff(hold.get(s, 0) - alloc_vals.get(s, 0)) for s in size_order]
    d_total = fmt_diff(hold['합계'] - alloc_vals['합계'])
    lines.append(f"| | 여유 | {d_cells[0]} | {d_cells[1]} | {d_cells[2]} | {d_cells[3]} | **{d_total}** |")

lines.append("")
lines.append("---")
lines.append("")

# 2. IoT가전
lines.append("## 2. IoT가전 할당표 대비 보유현황 (분류 유형별 세분화)")
lines.append("")
lines.append("| 세부 업종 | 구분 | 10~29인 | 30~99인 | 100~299인 | 300인+ | 합계 |")
lines.append("|-----------|------|---------|---------|-----------|--------|------|")

for cat in iot_categories + ['합계']:
    if cat == '합계':
        cat_label = '**합계**'
        alloc_vals = {}
        for s in size_order:
            alloc_vals[s] = sum(iot_alloc[c].get(s, 0) for c in iot_categories)
        alloc_vals['합계'] = sum(alloc_vals.values())
        r = iot_results['합계']
    else:
        cat_label = f"**{cat}**"
        alloc_vals = dict(iot_alloc[cat])
        alloc_vals['합계'] = sum(iot_alloc[cat].values())
        r = iot_results[cat]
    
    # 할당
    a_cells = [fmt(alloc_vals.get(s, 0)) for s in size_order]
    lines.append(f"| {cat_label} | 할당 | {a_cells[0]} | {a_cells[1]} | {a_cells[2]} | {a_cells[3]} | **{fmt(alloc_vals['합계'])}** |")
    
    # 확정
    c_cells = [fmt(r['확정'].get(s, 0)) for s in size_order]
    lines.append(f"| | 확정 | {c_cells[0]} | {c_cells[1]} | {c_cells[2]} | {c_cells[3]} | **{fmt(r['확정']['합계'])}** |")
    
    # 예상
    e_cells = [fmt(r['예상'].get(s, 0)) for s in size_order]
    lines.append(f"| | 예상 | {e_cells[0]} | {e_cells[1]} | {e_cells[2]} | {e_cells[3]} | **{fmt(r['예상']['합계'])}** |")
    
    # 모호
    m_cells = [fmt(r['모호'].get(s, 0)) for s in size_order]
    lines.append(f"| | 모호 | {m_cells[0]} | {m_cells[1]} | {m_cells[2]} | {m_cells[3]} | **{fmt(r['모호']['합계'])}** |")
    
    # 소계
    s_cells = [fmt(r['소계'].get(s, 0)) for s in size_order]
    lines.append(f"| | 소계 | {s_cells[0]} | {s_cells[1]} | {s_cells[2]} | {s_cells[3]} | **{fmt(r['소계']['합계'])}** |")
    
    # 여유
    d_cells = [fmt_diff(r['소계'].get(s, 0) - alloc_vals.get(s, 0)) for s in size_order]
    d_total = fmt_diff(r['소계']['합계'] - alloc_vals['합계'])
    lines.append(f"| | 여유 | {d_cells[0]} | {d_cells[1]} | {d_cells[2]} | {d_cells[3]} | **{d_total}** |")

lines.append("")

# 미분류 정보 참고
unc = iot_unclassified
if unc['소계']['합계'] > 0:
    lines.append(f"> [!WARNING]")
    lines.append(f"> **미분류**: 확정 {unc['확정']['합계']}건, 예상 {unc['예상']['합계']}건, 모호 {unc['모호']['합계']}건 (합계 {unc['소계']['합계']}건)")
    lines.append(f"> 이들은 예상_근거에서 IoT 대분류를 추출할 수 없는 건입니다.")
    lines.append(f"> 미분류 건은 위 합계에 포함되어 있습니다.")
    lines.append("")

lines.append("> [!NOTE]")
lines.append("> - **확정** = 확정(이전조사) + 확정(KEA추가)")
lines.append("> - **예상** = 키워드 `해당` 매칭")
lines.append("> - **모호** = 키워드 `해당(예상)/모호` 매칭")
lines.append("> - **소계** = 확정 + 예상 + 모호 (미분류 제외)")
lines.append("> - **여유** = 소계 - 할당")
lines.append("")

# 저장
report_path = os.path.join(INPUT_DIR, "allocation_vs_holdings_report.md")
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f"\n[INFO] Report saved to: {report_path}")

# 콘솔에도 출력
print("\n" + "=" * 80)
for line in lines:
    print(line)

print("\n[DONE]")
