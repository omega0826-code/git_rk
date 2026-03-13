# -*- coding: utf-8 -*-
"""
05_clean_industry.py - 업종(KSIC) 정제 및 분류 매핑 모듈
KSIC 11차 기준으로 대표업종 코드를 표준화하고,
대분류(KSIC1)·중분류(KSIC2) 코드 및 명칭을 파생합니다.
"""

import os
import re
import csv
import glob
from typing import Optional

import pandas as pd


# ──────────────────────────────────────────
# 참조 데이터 경로 (statistical classification/)
# ──────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # database/
STAT_CLASS_DIR = os.path.join(DB_ROOT, "statistical_classification")
KSIC_11TH_DIR = os.path.join(STAT_CLASS_DIR, "11th")
KSIC_MAPPING_FILE = os.path.join(STAT_CLASS_DIR, "KSIC10th-KSIC11th.csv")


def _find_csv(directory: str, prefix: str) -> str:
    """디렉토리에서 prefix로 시작하는 CSV 파일 경로 반환.

    Args:
        directory: 검색 디렉토리
        prefix: 파일명 접두사 (예: "KSIC1_")

    Returns:
        매칭된 CSV 파일의 절대 경로

    Raises:
        FileNotFoundError: 매칭 파일이 없는 경우
    """
    pattern = os.path.join(directory, f"{prefix}*.csv")
    matches = glob.glob(pattern)
    if not matches:
        raise FileNotFoundError(f"'{prefix}*.csv' 파일을 찾을 수 없습니다: {directory}")
    return matches[0]


def _load_ksic1() -> dict:
    """KSIC 대분류(KSIC1) CSV를 로드하여 {코드: 명칭} 딕셔너리 반환.

    Returns:
        {"A": "농업, 임업 및 어업(01~03)", ...}
    """
    path = _find_csv(KSIC_11TH_DIR, "KSIC1_")
    result = {}
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            result[row["KSIC1_cd"].strip()] = row["KSIC1_name"].strip()
    return result


def _load_ksic2() -> dict:
    """KSIC 중분류(KSIC2) CSV를 로드하여 {코드: 명칭} 딕셔너리 반환.

    Returns:
        {"10": "식료품 제조업", "11": "음료 제조업", ...}
    """
    path = _find_csv(KSIC_11TH_DIR, "KSIC2_")
    result = {}
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            result[row["KSIC2_cd"].strip()] = row["KSIC2_name"].strip()
    return result


def _load_ksic10_to_11() -> dict:
    """KSIC 10차→11차 매핑 CSV를 로드.

    1:N 관계(세분)의 경우 첫 번째 매핑만 사용합니다.

    Returns:
        {"27400": "27220", ...} (10차 코드→11차 코드)
    """
    result = {}
    if not os.path.exists(KSIC_MAPPING_FILE):
        return result
    with open(KSIC_MAPPING_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            old_cd = row["KSIC10_cd"].strip()
            new_cd = row["KSIC11_cd"].strip()
            if old_cd not in result:  # 1:N인 경우 첫 번째만
                result[old_cd] = new_cd
    return result


def _build_mid_to_major(ksic1: dict) -> dict:
    """중분류 코드(2자리)→대분류 코드(알파벳) 매핑 딕셔너리 생성.

    KSIC1 명칭에 포함된 "(10~34)" 형태의 범위 정보를 파싱합니다.

    Args:
        ksic1: _load_ksic1()의 반환값

    Returns:
        {"01": "A", "02": "A", ..., "10": "C", ..., "99": "U"}
    """
    mid_to_major: dict = {}
    for code, name in ksic1.items():
        match = re.search(r"\((\d+)~?(\d+)?\)", name)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else start
            for mid in range(start, end + 1):
                mid_to_major[f"{mid:02d}"] = code
    return mid_to_major


def _clean_name(name: str) -> str:
    """대분류명에서 코드 범위 괄호 제거.

    Args:
        name: "제조업(10~34)"

    Returns:
        "제조업"
    """
    return re.sub(r"\(\d+~?\d*\)", "", name).strip()


def clean_industry(df: pd.DataFrame) -> tuple:
    """업종(KSIC) 정제 및 분류 매핑 수행.

    Args:
        df: 정제 대상 데이터프레임 (대표업종, 차수 컬럼 필요)

    Returns:
        (df, stats_dict) 튜플
    """
    # 참조 데이터 로드
    ksic1 = _load_ksic1()
    ksic2 = _load_ksic2()
    mapping_10to11 = _load_ksic10_to_11()
    mid_to_major = _build_mid_to_major(ksic1)

    stats = {
        "총_건수": len(df),
        "정상": 0,
        "빈칸_결함": 0,
        "무효코드_결함": 0,
        "변환실패_결함": 0,
        "분류매핑실패_결함": 0,
        "차수_11": 0,
        "차수_10_변환": 0,
        "차수_기타_11가정": 0,
    }

    # 결과 컬럼 초기화
    major_codes = []      # 대분류 코드
    major_names = []      # 대분류명
    mid_codes = []        # 중분류 코드
    mid_names = []        # 중분류명
    industry_tags = []    # 결함 태그

    for idx in df.index:
        raw_code = str(df.at[idx, "대표업종"]).strip() if pd.notna(df.at[idx, "대표업종"]) else ""
        raw_revision = str(df.at[idx, "차수"]).strip() if "차수" in df.columns and pd.notna(df.at[idx, "차수"]) else ""

        # ① 빈칸 검사
        if not raw_code or raw_code == "nan":
            stats["빈칸_결함"] += 1
            industry_tags.append("[삭제:업종결함] 빈칸")
            major_codes.append("")
            major_names.append("")
            mid_codes.append("")
            mid_names.append("")
            continue

        # ② 무효 코드 검사 (숫자 5자리)
        if not raw_code.isdigit() or len(raw_code) != 5:
            stats["무효코드_결함"] += 1
            industry_tags.append(f"[삭제:업종결함] 무효코드({raw_code})")
            major_codes.append("")
            major_names.append("")
            mid_codes.append("")
            mid_names.append("")
            continue

        # ③ 차수별 처리
        code_11 = raw_code  # 기본: 11차로 가정
        if raw_revision == "10":
            # 10차→11차 변환 시도
            if raw_code in mapping_10to11:
                code_11 = mapping_10to11[raw_code]
                stats["차수_10_변환"] += 1
            else:
                stats["변환실패_결함"] += 1
                industry_tags.append(f"[삭제:업종결함] 변환실패({raw_code})")
                major_codes.append("")
                major_names.append("")
                mid_codes.append("")
                mid_names.append("")
                continue
        elif raw_revision == "11":
            stats["차수_11"] += 1
        else:
            # 0, 빈칸, 9, 8 등 → 11차로 가정
            stats["차수_기타_11가정"] += 1

        # ④ 중분류 매핑
        mid_cd = code_11[:2]
        if mid_cd not in ksic2:
            stats["분류매핑실패_결함"] += 1
            industry_tags.append(f"[삭제:업종결함] 분류매핑실패({code_11})")
            major_codes.append("")
            major_names.append("")
            mid_codes.append("")
            mid_names.append("")
            continue

        # ⑤ 대분류 역매핑
        major_cd = mid_to_major.get(mid_cd, "")
        if not major_cd:
            stats["분류매핑실패_결함"] += 1
            industry_tags.append(f"[삭제:업종결함] 분류매핑실패({code_11})")
            major_codes.append("")
            major_names.append("")
            mid_codes.append("")
            mid_names.append("")
            continue

        # ⑥ 성공
        stats["정상"] += 1
        industry_tags.append("")
        major_codes.append(major_cd)
        major_names.append(_clean_name(ksic1.get(major_cd, "")))
        mid_codes.append(mid_cd)
        mid_names.append(ksic2.get(mid_cd, ""))

    # 컬럼 추가
    df["_업종태그"] = industry_tags
    df["대표업종코드(대)"] = major_codes
    df["대표업종명(대)"] = major_names
    df["대표업종코드(중)"] = mid_codes
    df["대표업종명(중)"] = mid_names

    return df, stats


if __name__ == "__main__":
    # 간단 테스트
    test_data = {
        "대표업종": ["18112", "26519", "99999", "", "27400"],
        "차수": ["11", "11", "11", "11", "10"],
    }
    test_df = pd.DataFrame(test_data)
    result_df, test_stats = clean_industry(test_df)
    print("=== 테스트 결과 ===")
    print(result_df[["대표업종", "차수", "대표업종코드(대)", "대표업종명(대)",
                      "대표업종코드(중)", "대표업종명(중)", "_업종태그"]].to_string())
    print(f"\n통계: {test_stats}")
