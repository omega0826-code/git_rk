# -*- coding: utf-8 -*-
import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import os
from datetime import date, timedelta
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
# 영업일 계산
# ========================================
start = date(2026, 3, 23)
end = date(2026, 4, 15)

# 2026년 공휴일 (3/23~4/15 해당)
holidays_2026 = {
    # 이 기간에 해당하는 공휴일 없음
    # 참고: 삼일절(3/1), 어린이날(5/5) 등은 범위 밖
}

weekday_names = ['월', '화', '수', '목', '금', '토', '일']

all_days = []
d = start
while d <= end:
    wd = d.weekday()  # 0=월 ~ 6=일
    is_weekend = wd >= 5
    is_holiday = d in holidays_2026
    is_workday = not is_weekend and not is_holiday
    all_days.append({
        'date': d,
        'weekday': weekday_names[wd],
        'week_num': (d - start).days // 7 + 1,
        'is_weekend': is_weekend,
        'is_holiday': is_holiday,
        'is_workday': is_workday,
        'holiday_name': holidays_2026.get(d, '')
    })
    d += timedelta(days=1)

total_days = len(all_days)
work_days = [d for d in all_days if d['is_workday']]
num_workdays = len(work_days)
print(f"전체 기간: {start} ~ {end} ({total_days}일)")
print(f"영업일: {num_workdays}일")
print(f"주말/공휴일: {total_days - num_workdays}일")

# ========================================
# 조사 목표
# ========================================
target_elec = 350
target_iot = 250
target_total = target_elec + target_iot

daily_elec = target_elec / num_workdays
daily_iot = target_iot / num_workdays
daily_total = target_total / num_workdays

print(f"\n전자산업 목표: {target_elec}건 → 일 {daily_elec:.1f}건")
print(f"IoT가전 목표: {target_iot}건 → 일 {daily_iot:.1f}건")
print(f"합계: {target_total}건 → 일 {daily_total:.1f}건")

# 주차별 집계
weeks = {}
for d in all_days:
    w = d['week_num']
    if w not in weeks:
        weeks[w] = {'start': d['date'], 'end': d['date'], 'workdays': 0, 'days': []}
    weeks[w]['end'] = d['date']
    weeks[w]['days'].append(d)
    if d['is_workday']:
        weeks[w]['workdays'] += 1

print("\n주차별 영업일:")
for w, info in sorted(weeks.items()):
    print(f"  {w}주차: {info['start']}~{info['end']} ({info['workdays']}일)")

# ========================================
# PDF 생성
# ========================================
OUTPUT_DIR = r"d:\git_rk\data\factory_on\202601\company_list\electronics_iot\260318_1634"
output_path = os.path.join(OUTPUT_DIR, "survey_schedule_plan.pdf")

doc = SimpleDocTemplate(output_path, pagesize=A4,
                        leftMargin=15*mm, rightMargin=15*mm,
                        topMargin=15*mm, bottomMargin=15*mm)

# 스타일
title_s = ParagraphStyle('T', fontName='MalgunBold', fontSize=16, leading=22, alignment=1, spaceAfter=4*mm)
date_s = ParagraphStyle('D', fontName='Malgun', fontSize=8, leading=11, alignment=2, textColor=colors.grey, spaceAfter=4*mm)
sub_s = ParagraphStyle('S', fontName='MalgunBold', fontSize=11, leading=15, spaceAfter=3*mm, spaceBefore=4*mm, textColor=colors.HexColor('#1a1a2e'))
body_s = ParagraphStyle('B', fontName='Malgun', fontSize=9, leading=13, spaceAfter=2*mm)
note_s = ParagraphStyle('N', fontName='Malgun', fontSize=7.5, leading=10, textColor=colors.HexColor('#666666'), spaceAfter=2*mm)
caution_s = ParagraphStyle('C', fontName='Malgun', fontSize=8, leading=12, spaceAfter=2*mm, leftIndent=4*mm, textColor=colors.HexColor('#721c24'), backColor=colors.HexColor('#f8d7da'), borderPadding=4)
warning_s = ParagraphStyle('W', fontName='Malgun', fontSize=8, leading=12, spaceAfter=2*mm, leftIndent=4*mm, textColor=colors.HexColor('#856404'), backColor=colors.HexColor('#fff3cd'), borderPadding=4)
important_s = ParagraphStyle('I', fontName='Malgun', fontSize=8, leading=12, spaceAfter=2*mm, leftIndent=4*mm, textColor=colors.HexColor('#004085'), backColor=colors.HexColor('#cce5ff'), borderPadding=4)
tip_s = ParagraphStyle('P', fontName='Malgun', fontSize=8, leading=12, spaceAfter=2*mm, leftIndent=4*mm, textColor=colors.HexColor('#155724'), backColor=colors.HexColor('#d4edda'), borderPadding=4)

HEADER_BG = colors.HexColor('#1a1a2e')
WEEK_BG = colors.HexColor('#e8eaf6')
WE_BG = colors.HexColor('#f5f5f5')
TODAY_BG = colors.HexColor('#e8f5e9')

def fmt(n):
    return f'{n:,}' if isinstance(n, (int, float)) and n == int(n) else f'{n:.1f}' if isinstance(n, float) else str(n)

import math

story = []
story.append(Paragraph('전자산업·IoT가전 조사 일정 계획', title_s))
story.append(Paragraph('조사기간: 2026.03.23(월) ~ 2026.04.15(수) | 작성일: 2026-03-18', date_s))

# ========================================
# 1. 기간 요약
# ========================================
story.append(Paragraph('1. 조사 기간 개요', sub_s))

summary_data = [
    ['구분', '전자산업', 'IoT가전', '합계'],
    ['목표 표본(건)', '350', '250', '600'],
    ['조사 기간', '3/23(월)~4/15(수)', '3/23(월)~4/15(수)', '-'],
    ['총 일수', str(total_days), str(total_days), '-'],
    ['영업일', str(num_workdays), str(num_workdays), '-'],
    ['일 평균 목표', f'{daily_elec:.1f}', f'{daily_iot:.1f}', f'{daily_total:.1f}'],
]
cw_s = [35*mm, 45*mm, 45*mm, 35*mm]
t = Table(summary_data, colWidths=cw_s)
t.setStyle(TableStyle([
    ('FONTNAME', (0,0), (-1,-1), 'Malgun'), ('FONTSIZE', (0,0), (-1,-1), 8.5), ('LEADING', (0,0), (-1,-1), 12),
    ('FONTNAME', (0,0), (-1,0), 'MalgunBold'), ('BACKGROUND', (0,0), (-1,0), HEADER_BG), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (0,-1), 'MalgunBold'),
    ('ALIGN', (1,0), (-1,-1), 'CENTER'), ('ALIGN', (0,0), (0,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#cccccc')),
    ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
]))
story.append(t)
story.append(Spacer(1, 3*mm))

# ========================================
# 2. 주차별 조사 계획
# ========================================
story.append(Paragraph('2. 주차별 조사 계획', sub_s))

# 일별 할당 (균등 배분)
daily_e = math.ceil(daily_elec)  # 올림
daily_i = math.ceil(daily_iot)

week_data = [['주차', '기간', '영업일', '전자산업', 'IoT가전', '합계', '누적(%)']]
cum_e, cum_i = 0, 0
for w in sorted(weeks.keys()):
    info = weeks[w]
    wd = info['workdays']
    if wd == 0:
        continue
    # 주차별 목표
    w_e = min(daily_e * wd, target_elec - cum_e)
    w_i = min(daily_i * wd, target_iot - cum_i)
    if w_e < 0: w_e = 0
    if w_i < 0: w_i = 0
    cum_e += w_e
    cum_i += w_i
    cum_pct = (cum_e + cum_i) / target_total * 100
    s_date = info['start'].strftime('%m/%d')
    e_date = info['end'].strftime('%m/%d')
    week_data.append([
        f'{w}주차', f'{s_date}~{e_date}', f'{wd}일',
        f'{w_e}건', f'{w_i}건', f'{w_e + w_i}건', f'{cum_pct:.0f}%'
    ])

# 잔여분 마지막 주에 조정
remain_e = target_elec - cum_e
remain_i = target_iot - cum_i
if remain_e != 0 or remain_i != 0:
    last = week_data[-1]
    old_e = int(last[3].replace('건',''))
    old_i = int(last[4].replace('건',''))
    new_e = old_e + remain_e
    new_i = old_i + remain_i
    week_data[-1] = [last[0], last[1], last[2], f'{new_e}건', f'{new_i}건', f'{new_e+new_i}건', '100%']

# 합계행
week_data.append(['합계', '-', f'{num_workdays}일', f'{target_elec}건', f'{target_iot}건', f'{target_total}건', '100%'])

cw_w = [18*mm, 32*mm, 18*mm, 25*mm, 25*mm, 22*mm, 22*mm]
tw = Table(week_data, colWidths=cw_w)
tw_cmds = [
    ('FONTNAME', (0,0), (-1,-1), 'Malgun'), ('FONTSIZE', (0,0), (-1,-1), 8), ('LEADING', (0,0), (-1,-1), 11),
    ('FONTNAME', (0,0), (-1,0), 'MalgunBold'), ('BACKGROUND', (0,0), (-1,0), HEADER_BG), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,-1), (-1,-1), 'MalgunBold'), ('BACKGROUND', (0,-1), (-1,-1), WEEK_BG),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#cccccc')),
    ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
]
tw.setStyle(TableStyle(tw_cmds))
story.append(tw)
story.append(Spacer(1, 3*mm))

# ========================================
# 3. 일별 상세 스케줄
# ========================================
story.append(Paragraph('3. 일별 상세 스케줄', sub_s))

day_data = [['날짜', '요일', '구분', '전자산업', 'IoT가전', '합계', '누적 전자', '누적 IoT']]
cum_e2, cum_i2 = 0, 0
day_num = 0
for d in all_days:
    dt = d['date']
    wd_name = d['weekday']
    if d['is_weekend']:
        day_data.append([dt.strftime('%m/%d'), wd_name, '주말', '-', '-', '-', '-', '-'])
    elif d['is_holiday']:
        day_data.append([dt.strftime('%m/%d'), wd_name, d['holiday_name'], '-', '-', '-', '-', '-'])
    else:
        day_num += 1
        # 마지막 영업일에 잔여분 배정
        if day_num == num_workdays:
            de = target_elec - cum_e2
            di = target_iot - cum_i2
        else:
            de = daily_e
            di = daily_i
        cum_e2 += de
        cum_i2 += di
        # 초과 방지
        if cum_e2 > target_elec:
            de -= (cum_e2 - target_elec)
            cum_e2 = target_elec
        if cum_i2 > target_iot:
            di -= (cum_i2 - target_iot)
            cum_i2 = target_iot
        day_data.append([dt.strftime('%m/%d'), wd_name, f'D{day_num}',
                         f'{de}', f'{di}', f'{de+di}',
                         f'{cum_e2}/{target_elec}', f'{cum_i2}/{target_iot}'])

cw_d = [18*mm, 12*mm, 15*mm, 22*mm, 22*mm, 20*mm, 28*mm, 28*mm]
td = Table(day_data, colWidths=cw_d)
td_cmds = [
    ('FONTNAME', (0,0), (-1,-1), 'Malgun'), ('FONTSIZE', (0,0), (-1,-1), 7), ('LEADING', (0,0), (-1,-1), 10),
    ('FONTNAME', (0,0), (-1,0), 'MalgunBold'), ('BACKGROUND', (0,0), (-1,0), HEADER_BG), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#cccccc')),
    ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2),
]
# 주말 회색 처리
for i in range(1, len(day_data)):
    if day_data[i][2] in ('주말', ):
        td_cmds.append(('BACKGROUND', (0,i), (-1,i), WE_BG))
        td_cmds.append(('TEXTCOLOR', (0,i), (-1,i), colors.HexColor('#999999')))
td.setStyle(TableStyle(td_cmds))
story.append(td)
story.append(Spacer(1, 3*mm))

# ========================================
# 4. 조사 검토 인사이트
# ========================================
story.append(PageBreak())
story.append(Paragraph('4. 조사 운영 인사이트 및 검토사항', sub_s))

story.append(Paragraph(
    f'<b>📊 일일 조사 목표량 검토</b><br/>'
    f'• 전자산업: 일 {daily_e}건 (총 350건 ÷ {num_workdays}일)<br/>'
    f'• IoT가전: 일 {daily_i}건 (총 250건 ÷ {num_workdays}일)<br/>'
    f'• 합계: 일 {daily_e + daily_i}건 — 조사원 1인당 하루 5~8건 기준 시 약 <b>{math.ceil((daily_e + daily_i)/6)}~{math.ceil((daily_e + daily_i)/5)}명</b> 필요',
    important_s))

story.append(Paragraph(
    '<b>⚠ 초반 1주차(3/23~3/29) 집중 운영 필요</b><br/>'
    '• 1주차에 조사 프로세스 안정화 및 응답률 모니터링<br/>'
    '• 목표 달성률이 70% 미만이면 2주차부터 일일 할당량 상향 조정 필요<br/>'
    '• 1주차 목표 누적 약 25% 도달 권장',
    warning_s))

story.append(Paragraph(
    '<b>⚠ 300인 이상 기업 우선 접촉 전략</b><br/>'
    '• 전자산업 300인+: 여유 극소 (영상음향 +13, 방송통신 +15 등)<br/>'
    '• IoT가전 300인+: 홈헬스케어 여유 +2, 홈네트워크 +8 등 대체 어려움<br/>'
    '• <b>1주차 내 300인+ 기업 전수 사전 연락</b> 완료 권장',
    caution_s))

story.append(Paragraph(
    '<b>💡 단계별 조사 전략 제안</b><br/>'
    '• <b>1단계(1주차)</b>: 확정 기업 87건 우선 조사 + 300인+ 사전 접촉<br/>'
    '• <b>2단계(2~3주차)</b>: 예상 등급 기업 집중 조사 (전자산업 병행)<br/>'
    '• <b>3단계(4주차)</b>: 미달성 업종 보충 조사 + 모호 등급 기업 전환<br/>'
    '• 주 1회 업종별·규모별 달성률 점검 → 부족 셀 조기 대응',
    tip_s))

story.append(Paragraph(
    '<b>💡 응답 거부 대비 예비 표본 운용</b><br/>'
    '• 통상 조사 응답률 30~40% 가정 시, 접촉 대상은 목표의 약 2.5~3배 필요<br/>'
    '• 전자산업: 350건 목표 → <b>약 900~1,050건 접촉</b> 계획<br/>'
    '• IoT가전: 250건 목표 → <b>약 625~750건 접촉</b> 계획<br/>'
    '• 업종별·규모별 예비 리스트를 사전 준비하여 즉시 투입 가능하도록 관리',
    tip_s))

story.append(Paragraph(
    '<b>ℹ 주간 모니터링 체크포인트</b><br/>'
    '• 1주차 종료 시: 누적 25% 달성 여부 (전자 88건, IoT 63건)<br/>'
    '• 2주차 종료 시: 누적 50% 달성 여부 (전자 175건, IoT 125건)<br/>'
    '• 3주차 종료 시: 누적 75% 달성 여부 (전자 263건, IoT 188건)<br/>'
    '• 4주차 종료 시: 100% 달성 마감 (전자 350건, IoT 250건)',
    important_s))

doc.build(story)
print(f"\n[DONE] PDF saved: {output_path}")
