# -*- coding: utf-8 -*-
import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('Malgun', r"C:\Windows\Fonts\malgun.ttf"))
pdfmetrics.registerFont(TTFont('MalgunBold', r"C:\Windows\Fonts\malgunbd.ttf"))

# ========================================
# 데이터 로드 및 집계
# ========================================
f = r'd:\git_rk\data\factory_on\202601\company_list\electronics_iot\260318_1634\company_electronics_iot_employees_10_and_over_F_260318_1634.csv'
df = pd.read_csv(f, encoding='utf-8-sig')
sizes = ['10~29인', '30~99인', '100~299인', '300인 이상']

# IoT가전 확정+예상 제외 조건
iot_exclude = df['가전IoT_예상'].isin(['확정(이전조사)', '확정(KEA추가)', '예상'])
print(f"전체: {len(df)}")
print(f"IoT가전 확정+예상: {iot_exclude.sum()}")

# 전자산업 대상: 전자산업_대분류가 있고, IoT확정+예상이 아닌 기업
df_10plus = df[df['종업원규모'].isin(sizes)]
df_elec = df_10plus[(df_10plus['전자산업_대분류'] != '') & (df_10plus['전자산업_대분류'].notna())]
df_elec_excl = df_elec[~df_elec.index.isin(df[iot_exclude].index)]

print(f"\n전자산업 전체(10인+): {len(df_elec)}")
print(f"IoT확정+예상 제외 후: {len(df_elec_excl)}")
print(f"제외된 기업: {len(df_elec) - len(df_elec_excl)}")

# 전자산업 1차분류
df_elec_excl = df_elec_excl.copy()
df_elec_excl['전자산업_1차'] = df_elec_excl['전자산업_대분류'].apply(lambda x: str(x).split('/')[0])

cats_e = ['전자부품', '컴퓨터주변기기', '방송통신장비', '영상음향기기', '측정제어분석기기', '전기장비']
elec_result = {}
for cat in cats_e:
    sub = df_elec_excl[df_elec_excl['전자산업_1차'] == cat]
    vals = [(sub['종업원규모'] == s).sum() for s in sizes]
    elec_result[cat] = vals + [sum(vals)]
    print(f"  {cat}: {vals} = {sum(vals)}")

# 합계
total_e = [sum(elec_result[c][i] for c in cats_e) for i in range(5)]
elec_result['합계'] = total_e
print(f"  합계: {total_e}")

# IoT가전 (기존과 동일)
def get_iot_cat(x):
    x = str(x)
    if '지능형 가전' in x: return '지능형 가전'
    if '홈헬스케어' in x: return '홈헬스케어'
    if '홈네트워크' in x or '주거안전' in x: return '홈네트워크 및 주거안전'
    if '홈에너지' in x: return '홈에너지'
    return '미분류'

iot = df_10plus[df_10plus['가전IoT_예상'].isin(['확정(이전조사)', '확정(KEA추가)', '예상', '모호'])].copy()
iot['IoT_cat'] = iot['예상_근거'].apply(get_iot_cat)
iot['grade'] = iot['가전IoT_예상'].apply(lambda x: '확정' if '확정' in str(x) else x)

cats_i = ['지능형 가전', '홈헬스케어', '홈네트워크 및 주거안전', '홈에너지']
grades = ['확정', '예상', '모호']
iot_result = {}
for cat in cats_i:
    iot_result[cat] = {}
    for g in grades:
        sub = iot[(iot['IoT_cat'] == cat) & (iot['grade'] == g)]
        vals = [(sub['종업원규모'] == s).sum() for s in sizes]
        iot_result[cat][g] = vals + [sum(vals)]

# ========================================
# 할당표 데이터
# ========================================
alloc_e = {
    '전자부품': [22, 13, 11, 17, 63],
    '컴퓨터주변기기': [12, 10, 4, 1, 27],
    '방송통신장비': [16, 9, 7, 5, 37],
    '영상음향기기': [12, 10, 7, 1, 30],
    '측정제어분석기기': [28, 14, 10, 8, 60],
    '전기장비': [55, 23, 23, 32, 133],
    '합계': [145, 79, 62, 64, 350],
}
alloc_i = {
    '지능형 가전': [54, 25, 14, 10, 103],
    '홈헬스케어': [11, 7, 3, 1, 22],
    '홈네트워크 및 주거안전': [57, 20, 5, 3, 85],
    '홈에너지': [28, 7, 2, 3, 40],
    '합계': [150, 59, 24, 17, 250],
}

# ========================================
# PDF 생성
# ========================================
OUTPUT_DIR = r"d:\git_rk\data\factory_on\202601\company_list\electronics_iot\260318_1634"
output_path = os.path.join(OUTPUT_DIR, "allocation_vs_holdings_insight_report.pdf")

doc = SimpleDocTemplate(output_path, pagesize=A4,
                        leftMargin=15*mm, rightMargin=15*mm,
                        topMargin=15*mm, bottomMargin=15*mm)

# 스타일
title_s = ParagraphStyle('T', fontName='MalgunBold', fontSize=16, leading=22, alignment=1, spaceAfter=6*mm)
date_s = ParagraphStyle('D', fontName='Malgun', fontSize=8, leading=11, alignment=2, textColor=colors.grey, spaceAfter=4*mm)
sub_s = ParagraphStyle('S', fontName='MalgunBold', fontSize=11, leading=15, spaceAfter=3*mm, spaceBefore=5*mm, textColor=colors.HexColor('#1a1a2e'))
note_s = ParagraphStyle('N', fontName='Malgun', fontSize=7.5, leading=10, textColor=colors.HexColor('#666666'), spaceAfter=2*mm)
caution_s = ParagraphStyle('C', fontName='Malgun', fontSize=8, leading=12, spaceAfter=2*mm, leftIndent=4*mm, textColor=colors.HexColor('#721c24'), backColor=colors.HexColor('#f8d7da'), borderPadding=4)
warning_s = ParagraphStyle('W', fontName='Malgun', fontSize=8, leading=12, spaceAfter=2*mm, leftIndent=4*mm, textColor=colors.HexColor('#856404'), backColor=colors.HexColor('#fff3cd'), borderPadding=4)
important_s = ParagraphStyle('I', fontName='Malgun', fontSize=8, leading=12, spaceAfter=2*mm, leftIndent=4*mm, textColor=colors.HexColor('#004085'), backColor=colors.HexColor('#cce5ff'), borderPadding=4)
tip_s = ParagraphStyle('P', fontName='Malgun', fontSize=8, leading=12, spaceAfter=2*mm, leftIndent=4*mm, textColor=colors.HexColor('#155724'), backColor=colors.HexColor('#d4edda'), borderPadding=4)

HEADER_BG = colors.HexColor('#1a1a2e')
ALLOC_BG = colors.HexColor('#e8eaf6')
SURPLUS_BG = colors.HexColor('#e8f5e9')

def fmt(n):
    return f'{n:,}' if isinstance(n, int) else str(n)

def surplus(n):
    return f'+{n:,}' if n >= 0 else f'{n:,}'

def make_table(data, cw):
    t = Table(data, colWidths=cw, repeatRows=1)
    cmds = [
        ('FONTNAME', (0,0), (-1,-1), 'Malgun'), ('FONTSIZE', (0,0), (-1,-1), 7.5), ('LEADING', (0,0), (-1,-1), 11),
        ('FONTNAME', (0,0), (-1,0), 'MalgunBold'), ('BACKGROUND', (0,0), (-1,0), HEADER_BG), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'), ('ALIGN', (0,0), (1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#cccccc')),
        ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 3), ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]
    for i in range(1, len(data)):
        row = data[i]
        if row[1] == '할당':
            cmds.append(('BACKGROUND', (0,i), (-1,i), ALLOC_BG))
            cmds.append(('FONTNAME', (0,i), (-1,i), 'MalgunBold'))
        elif row[1] == '여유':
            cmds.append(('BACKGROUND', (0,i), (-1,i), SURPLUS_BG))
            cmds.append(('FONTNAME', (-1,i), (-1,i), 'MalgunBold'))
        elif row[1] == '소계':
            cmds.append(('FONTNAME', (0,i), (-1,i), 'MalgunBold'))
            cmds.append(('LINEABOVE', (0,i), (-1,i), 0.8, colors.HexColor('#333333')))
        if row[0] and row[0] != '' and i > 0:
            cmds.append(('FONTNAME', (0,i), (0,i), 'MalgunBold'))
    t.setStyle(TableStyle(cmds))
    return t

story = []
story.append(Paragraph('표본할당표 대비 보유현황 비교 및 조사 검토 인사이트', title_s))
story.append(Paragraph('작성일: 2026-03-18 | 데이터: 260318_1634 | IoT가전 확정+예상 기업 전자산업에서 제외', date_s))

# ========================================
# 1. 전자산업
# ========================================
story.append(Paragraph('1. 전자산업 할당표 대비 보유현황 (IoT가전 확정·예상 제외)', sub_s))

cw_e = [38*mm, 14*mm, 22*mm, 22*mm, 22*mm, 22*mm, 22*mm]
elec_labels = {'전자부품': '① 전자부품', '컴퓨터주변기기': '② 컴퓨터주변기기', '방송통신장비': '③ 방송통신장비',
               '영상음향기기': '④ 영상음향기기', '측정제어분석기기': '⑤ 측정제어분석', '전기장비': '⑥ 전기장비', '합계': '합계'}
elec_data = [['대분류', '구분', '10~29인', '30~99인', '100~299인', '300인+', '합계']]
for cat in cats_e + ['합계']:
    a = alloc_e[cat]
    h = elec_result[cat]
    s = [h[i] - a[i] for i in range(5)]
    elec_data.append([elec_labels[cat], '할당', fmt(a[0]), fmt(a[1]), fmt(a[2]), fmt(a[3]), fmt(a[4])])
    elec_data.append(['', '보유', fmt(h[0]), fmt(h[1]), fmt(h[2]), fmt(h[3]), fmt(h[4])])
    elec_data.append(['', '여유', surplus(s[0]), surplus(s[1]), surplus(s[2]), surplus(s[3]), surplus(s[4])])

story.append(make_table(elec_data, cw_e))
story.append(Spacer(1, 1*mm))
story.append(Paragraph(f'※ IoT가전 확정+예상 {iot_exclude.sum()}건 중 전자산업 대분류 해당 기업을 제외한 수치입니다.', note_s))
story.append(Spacer(1, 2*mm))

story.append(Paragraph('전자산업 조사 검토사항', sub_s))
story.append(Paragraph(
    '<b>⚠ 300인 이상 규모의 여유분 부족 주의</b><br/>'
    '• 측정제어분석기기·방송통신장비·전기장비 300인+ 셀의 여유분 확인 필요<br/>'
    '• IoT가전 제외로 대규모 기업 일부 감소 → 전수층 대체 여력 더욱 제한적',
    caution_s))
story.append(Paragraph(
    '<b>⚠ 영상음향기기 — 전체적으로 가장 취약한 업종</b><br/>'
    '• 6개 대분류 중 보유 최소, 모든 규모에서 여유 가장 적음<br/>'
    '• 조사 전 영상음향기기 기업의 연락처·업종 정보 사전 검증 우선 권장',
    warning_s))
story.append(Paragraph(
    '<b>ℹ 복수 업종 분류 기업 처리 방안 필요</b><br/>'
    '• 약 20% 기업이 2개 이상 대분류에 동시 해당<br/>'
    '• 조사 시 실제 주력 생산품 기준 재분류 검토 필요',
    important_s))

# ========================================
# 2. IoT가전 (새 페이지)
# ========================================
story.append(PageBreak())
story.append(Paragraph('2. IoT가전 할당표 대비 보유현황 (분류 유형별 세분화)', sub_s))

cw_i = [42*mm, 14*mm, 22*mm, 22*mm, 22*mm, 18*mm, 22*mm]
iot_labels = {'홈네트워크 및 주거안전': '홈네트워크 및\n주거안전'}
iot_data = [['세부 업종', '구분', '10~29인', '30~99인', '100~299인', '300인+', '합계']]

iot_totals = {g: [0]*5 for g in grades + ['소계']}
for cat in cats_i + ['합계']:
    if cat == '합계':
        a = alloc_i[cat]
        # 소계
        subtot = [sum(iot_totals['확정'][i] + iot_totals['예상'][i] + iot_totals['모호'][i] for _ in [0]) for i in range(5)]
        # 이미 누적됨
        iot_data.append(['합계', '할당', fmt(a[0]), fmt(a[1]), fmt(a[2]), fmt(a[3]), fmt(a[4])])
        for g in grades:
            v = iot_totals[g]
            iot_data.append(['', g, fmt(v[0]), fmt(v[1]), fmt(v[2]), fmt(v[3]), fmt(v[4])])
        st = iot_totals['소계']
        iot_data.append(['', '소계', fmt(st[0]), fmt(st[1]), fmt(st[2]), fmt(st[3]), fmt(st[4])])
        s = [st[i] - a[i] for i in range(5)]
        iot_data.append(['', '여유', surplus(s[0]), surplus(s[1]), surplus(s[2]), surplus(s[3]), surplus(s[4])])
    else:
        label = iot_labels.get(cat, cat)
        a = alloc_i[cat]
        iot_data.append([label, '할당', fmt(a[0]), fmt(a[1]), fmt(a[2]), fmt(a[3]), fmt(a[4])])
        subtot_cat = [0]*5
        for g in grades:
            v = iot_result[cat][g]
            iot_data.append(['', g, fmt(v[0]), fmt(v[1]), fmt(v[2]), fmt(v[3]), fmt(v[4])])
            for i in range(5):
                subtot_cat[i] += v[i]
                iot_totals[g][i] += v[i]
        iot_data.append(['', '소계', fmt(subtot_cat[0]), fmt(subtot_cat[1]), fmt(subtot_cat[2]), fmt(subtot_cat[3]), fmt(subtot_cat[4])])
        for i in range(5):
            iot_totals['소계'][i] += subtot_cat[i]
        s = [subtot_cat[i] - a[i] for i in range(5)]
        iot_data.append(['', '여유', surplus(s[0]), surplus(s[1]), surplus(s[2]), surplus(s[3]), surplus(s[4])])

story.append(make_table(iot_data, cw_i))
story.append(Spacer(1, 1*mm))
story.append(Paragraph('확정 = 확정(이전조사)+확정(KEA추가) / 예상 = 키워드 해당 / 모호 = 해당(예상)·모호 / 여유 = 소계−할당', note_s))
story.append(Spacer(1, 2*mm))

story.append(Paragraph('IoT가전 조사 검토사항', sub_s))
story.append(Paragraph(
    '<b>⚠ 300인 이상 규모 — 전 업종에서 여유분 극소</b><br/>'
    '• 홈헬스케어: 할당 1 vs 보유 3 → 여유 +2 (확정 0건)<br/>'
    '• 홈네트워크: 할당 3 vs 보유 11 → 여유 +8 (확정 0건)<br/>'
    '• 300인 이상은 전수층 → 사전 협조 요청 필수',
    caution_s))
story.append(Paragraph(
    '<b>⚠ 확정 기업 비율 극히 낮음 — 예상·모호 의존도 높음</b><br/>'
    '• 전체 확정: 87건 (소계의 1.4%)<br/>'
    '• 홈헬스케어: 확정 6건 / 할당 22건 → 확정만으로 할당의 27%<br/>'
    '• 예상·모호 등급의 실제 가전IoT 해당 여부 조사에서 검증 필요',
    warning_s))
story.append(Paragraph(
    '<b>ℹ 홈헬스케어 — 모호 등급 0건, 확정도 최소</b><br/>'
    '• 확정 6건 + 예상 332건 = 338건이 전부, 모호 기업 0건<br/>'
    '• 가장 작은 모집단 → 표본 추출 후 업종 확인 절차 권장',
    important_s))
story.append(Paragraph(
    '<b>💡 조사 우선순위 제안</b><br/>'
    '• 1순위: 확정 87건 (이전 조사 참여/KEA 회원사)<br/>'
    '• 2순위: 예상 4,596건 (키워드 직접 매칭)<br/>'
    '• 3순위: 모호 1,422건 (업종 확인 후 편입/제외 판단)<br/>'
    '• 300인+ 규모는 모든 등급 사전 전화 확인 후 조사 권장',
    tip_s))

doc.build(story)
print(f"\n[DONE] PDF saved: {output_path}")
