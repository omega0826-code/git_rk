# -*- coding: utf-8 -*-
"""XLS/XLSX 파서 — SPSS 교차분석 테이블 자동 탐지 및 데이터 추출"""
import re
import pandas as pd


def find_tables(df, skip_labels=None):
    """SPSS 교차분석 테이블 시작 행(title row)과 제목을 자동 탐지"""
    if skip_labels is None:
        skip_labels = {'학년', '성별', '소속 대학', '거주지', '전 체'}

    tables = []
    for i, row in df.iterrows():
        v = row[0]
        if pd.notna(v):
            s = str(v).strip()
            if s in skip_labels or not s:
                continue
            if any(s.startswith(p) for p in ('SQ', 'A', 'B', 'C', 'D', 'Q', '[', '\u25a0')):
                tables.append((i, s))
    return tables


def extract_bar_data(df, title_row, next_title_row=None):
    """
    SPSS 교차분석 테이블에서 전체(total) 행의 항목별 빈도/비율 추출.

    구조:
      title_row + 0: 테이블 제목
      title_row + 1: 구분 행
      title_row + 2: 항목명 행 (name_row)
      title_row + 3: 빈도/비율 행
      title_row + 4: 전체 행 (total_row)

    Returns:
      (labels, pcts, freqs, n)
    """
    name_row_idx = title_row + 2
    total_row_idx = title_row + 4

    if total_row_idx >= len(df):
        return [], [], [], 0

    name_row = df.iloc[name_row_idx]
    total_row = df.iloc[total_row_idx]

    n_val = total_row[2]
    n = int(n_val) if pd.notna(n_val) else 0

    labels, pcts, freqs = [], [], []

    for col in range(3, len(name_row)):
        nm = name_row[col]
        if pd.isna(nm):
            continue
        nm = str(nm).strip()
        if nm in ('빈도', '비율', '구 분', '평균', '응답수', '.'):
            continue
        if not nm:
            continue
        if len(nm) > 22:
            nm = nm[:20] + "..."

        fv = total_row[col] if col < len(total_row) and pd.notna(total_row[col]) else 0
        pv = total_row[col + 1] if (col + 1) < len(total_row) and pd.notna(total_row[col + 1]) else 0

        try:
            fv = float(fv)
            pv = float(pv) * 100
        except (ValueError, TypeError):
            continue

        labels.append(nm)
        freqs.append(fv)
        pcts.append(round(pv, 1))

    return labels, pcts, freqs, n


def load_xls(path, sheet_name="Sheet1"):
    """XLS/XLSX 파일을 DataFrame으로 로드"""
    return pd.read_excel(path, sheet_name=sheet_name, header=None)


def get_table_ranges(df, tables):
    """테이블 목록에서 각 테이블의 범위(다음 테이블 시작까지) 계산"""
    ranges = []
    for i, (row, title) in enumerate(tables):
        next_row = tables[i + 1][0] if i + 1 < len(tables) else len(df)
        ranges.append((row, title, next_row))
    return ranges
