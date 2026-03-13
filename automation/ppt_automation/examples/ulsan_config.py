# -*- coding: utf-8 -*-
"""
울산 일자리 미스매치 프로젝트 — 차트 설정 예시

이 파일은 create_chart_pptx.py에서 사용하는 TABLES 설정의 예시입니다.
새 프로젝트에서는 이 파일을 복사하여 Excel 구조에 맞게 수정하세요.
"""

# ─── 이 파일의 값을 스크립트에 복사하여 사용 ───

# 입력 Excel 파일
XLSX = r"d:\git_rk\project\25_121_ulsan\output\(OUTPUT)울산 일자리 미스매치_260205_1822.xlsx"
SHEET = "Sheet1"

# 출력 PPTX 위치 (타임스탬프 자동 추가)
OUT_DIR = r"d:\git_rk\project\25_121_ulsan\output\wording"
OUT_PREFIX = "울산_미스매치_차트_PPT"

# ─── TABLES 설정 ───
# Cfg(idx, title, total_row, name_row, data_col=4, n_col=3, chart="hbar", end_row=0)
#
# idx       : 표 번호
# title     : 슬라이드 제목
# total_row : "전 체" 합계 행 (Excel 행 번호)
# name_row  : 항목명 행 (Excel 행 번호)
# data_col  : 데이터 시작 열 (기본 4 = D열)
# n_col     : 응답자 수(n) 열 (기본 3 = C열)
# chart     : "hbar" | "pie" | "donut" | "radar" | "stacked"
# end_row   : stacked 전용 — 데이터 마지막 행

TABLES_CONFIG = """
Cfg(1,  "응답자 일반현황",                          3,   4, data_col=3, chart="pie"),
Cfg(2,  "일자리 정보 탐색 활용 경로 (중복응답)",    21,  19),
Cfg(3,  "취업 준비 중 느끼는 어려움 (중복응답)",    39,  37),
Cfg(4,  "대학에서 제공 받았으면 하는 지원 (중복응답)", 57, 55),
Cfg(5,  "필요 취업 정보 (1순위)",                   75,  73),
Cfg(6,  "필요 취업 정보 (1순위+2순위)",             93,  91),
Cfg(7,  "부족 역량 (1순위)",                        111, 109),
Cfg(8,  "부족 역량 (1순위+2순위)",                  129, 127),
Cfg(9,  "취업 시 고려 요소 (1순위)",                147, 145),
Cfg(10, "취업 시 고려 요소 (1순위+2순위)",          165, 163),
Cfg(11, "대학교별 취업 희망 업종",                  183, 181, chart="stacked", end_row=226),
Cfg(12, "대학교별 취업 희망 직군",                  232, 230, chart="stacked", end_row=267),
Cfg(13, "울산 지역 기업 인식 수준 (평균 점수)",     289, 288, chart="radar"),
Cfg(14, "졸업 후 희망 취업 지역",                   307, 305, chart="pie"),
Cfg(15, "울산 정주환경이 타지역 취업에 미친 영향",  325, 323, chart="donut"),
Cfg(16, "타지역 취업에 영향을 미친 정주환경 요인 (중복응답)", 343, 341),
Cfg(17, "울산 지역 청년 정착 정책 (1순위)",         361, 359),
Cfg(18, "울산 지역 청년 정착 정책 (1순위+2순위)",   379, 377),
"""

# ─── 사용법 ───
# create_chart_pptx.py의 TABLES 리스트에 위 설정을 복사하여 사용
# XLSX, OUT 경로도 스크립트 하단 __main__ 블록에서 수정
