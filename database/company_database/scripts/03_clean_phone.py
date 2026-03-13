# -*- coding: utf-8 -*-
"""
03_clean_phone.py - 전화번호 정제 모듈
허용: 지역번호(02, 031~064 등), 070, 휴대폰(010)
비허용: ARS, 1800, 1XXX 등 특수번호, 빈칸
"""

import re
import pandas as pd

# ──────────────────────────────────────────
# 한국 지역번호 목록
# ──────────────────────────────────────────
AREA_CODES = {
    "02",   # 서울
    "031", "032", "033",  # 경기, 인천, 강원
    "041", "042", "043", "044",  # 충남, 대전, 충북, 세종
    "051", "052", "053", "054", "055",  # 부산, 울산, 대구, 경북, 경남
    "061", "062", "063", "064",  # 전남, 광주, 전북, 제주
    "070",  # 인터넷전화
    "010",  # 휴대폰
}

# ──────────────────────────────────────────
# 유효한 전화번호 정규식 패턴
# ──────────────────────────────────────────
PHONE_PATTERNS = [
    # 02-XXX-XXXX 또는 02-XXXX-XXXX
    r"^02-\d{3,4}-\d{4}$",
    # 0XX-XXX-XXXX 또는 0XX-XXXX-XXXX (지역번호 3자리)
    r"^0\d{2}-\d{3,4}-\d{4}$",
    # 070-XXXX-XXXX
    r"^070-\d{4}-\d{4}$",
    # 010-XXXX-XXXX
    r"^010-\d{4}-\d{4}$",
]

COMPILED_PATTERNS = [re.compile(p) for p in PHONE_PATTERNS]


def normalize_phone(raw: str) -> str:
    """전화번호 정규화: 공백 제거, 특수문자 하이픈 통일"""
    if not isinstance(raw, str):
        return ""
    raw = raw.strip()
    if not raw:
        return ""

    # 괄호, 점, 공백 등을 하이픈으로 변환
    phone = re.sub(r"[().\s]+", "-", raw)
    # 연속 하이픈 정리
    phone = re.sub(r"-+", "-", phone)
    # 앞뒤 하이픈 제거
    phone = phone.strip("-")

    return phone


def try_format_phone(raw_digits: str) -> str:
    """
    하이픈 없는 숫자열을 전화번호 형식으로 포맷팅 시도.
    예: '0315316863' → '031-531-6863'
    """
    digits = re.sub(r"\D", "", raw_digits)

    if not digits or not digits.startswith("0"):
        return ""

    # 02-XXXX-XXXX (10자리)
    if digits.startswith("02") and len(digits) in (9, 10):
        mid_len = len(digits) - 6  # 3 or 4
        return f"02-{digits[2:2+mid_len]}-{digits[2+mid_len:]}"

    # 010/070-XXXX-XXXX (11자리)
    if digits[:3] in ("010", "070") and len(digits) == 11:
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"

    # 0XX-XXX-XXXX (10자리) 또는 0XX-XXXX-XXXX (11자리)
    if digits[:3] in AREA_CODES and len(digits) in (10, 11):
        mid_len = len(digits) - 7  # 3 or 4
        return f"{digits[:3]}-{digits[3:3+mid_len]}-{digits[3+mid_len:]}"

    return ""


def is_valid_phone(phone: str) -> bool:
    """정규화된 전화번호가 유효한 패턴인지 검사"""
    return any(p.match(phone) for p in COMPILED_PATTERNS)


def is_special_number(raw: str) -> bool:
    """ARS, 1800 등 특수번호 감지"""
    if not isinstance(raw, str):
        return False
    upper = raw.upper().strip()
    # ARS 번호
    if upper.startswith("ARS"):
        return True
    # 1XXX 형태 (1800, 1600, 1855 등)
    digits = re.sub(r"\D", "", upper)
    if digits and digits[0] == "1" and not digits.startswith("0"):
        return True
    return False


def clean_phone(df: pd.DataFrame, phone_col: str = "전화번호") -> tuple:
    """
    DataFrame의 전화번호를 정제합니다.
    Returns: (정제된_df, 통계_dict)
    """
    stats = {
        "총_건수": len(df),
        "빈칸": 0,
        "특수번호": 0,
        "유효": 0,
        "포맷팅_복원": 0,
        "무효": 0,
    }

    phone_tags = []

    for idx in df.index:
        raw = str(df.at[idx, phone_col]) if pd.notna(df.at[idx, phone_col]) else ""
        raw = raw.strip()

        # 빈칸
        if not raw:
            stats["빈칸"] += 1
            phone_tags.append("[삭제:전화번호결함] 빈칸")
            continue

        # 특수번호 감지
        if is_special_number(raw):
            stats["특수번호"] += 1
            phone_tags.append(f"[삭제:전화번호결함] 특수번호({raw})")
            continue

        # 정규화
        normalized = normalize_phone(raw)

        # 이미 유효한 형식인지 검사
        if is_valid_phone(normalized):
            stats["유효"] += 1
            phone_tags.append("")
            continue

        # 포맷팅 시도
        formatted = try_format_phone(raw)
        if formatted and is_valid_phone(formatted):
            stats["포맷팅_복원"] += 1
            df.at[idx, phone_col] = formatted
            phone_tags.append("")
            continue

        # 하이픈 포함된 상태에서도 지역번호 확인
        digits = re.sub(r"\D", "", normalized)
        formatted2 = try_format_phone(digits)
        if formatted2 and is_valid_phone(formatted2):
            stats["포맷팅_복원"] += 1
            df.at[idx, phone_col] = formatted2
            phone_tags.append("")
            continue

        # 무효
        stats["무효"] += 1
        phone_tags.append(f"[삭제:전화번호결함] 무효({raw})")

    df["_전화태그"] = phone_tags

    return df, stats


if __name__ == "__main__":
    test_data = {
        "전화번호": [
            "031-531-6863",     # 유효
            "070-7723-9277",    # 유효
            "02-585-5152",      # 유효
            "010-1234-5678",    # 유효
            "ARS-1833-2334",    # 특수번호
            "18001435",         # 특수번호 (1800)
            "",                 # 빈칸
            "032-7658-248",     # 무효 (끝자리 3자리)
            "054-7487-708",     # 무효 (끝자리 3자리)
            "0315316863",       # 포맷팅 가능
        ]
    }
    test_df = pd.DataFrame(test_data)
    result, stats = clean_phone(test_df)
    print("=== 전화번호 정제 결과 ===")
    for i, row in result.iterrows():
        print(f"  {row['전화번호']:20s} → 태그: {row['_전화태그']}")
    print(f"\n통계: {stats}")
