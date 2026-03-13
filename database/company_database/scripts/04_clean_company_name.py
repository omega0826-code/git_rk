# -*- coding: utf-8 -*-
"""
04_clean_company_name.py - 기업명 정제 모듈 v1.2
원본 회사명은 유지하고, 정규화/영문/중복검사용 컬럼을 추가합니다.

v1.2 변경:
  - 회사명_정규화: 영문 -> 한글 외래어 변환 (괄호 안 한글 우선 활용)
  - 회사명_영문: 정규화 결과의 전체 영문 표현 (외래어 역변환 + 고유어 음역)
"""

import re
import pandas as pd
from collections import defaultdict

# ──────────────────────────────────────────
# 법인 표기 제거 패턴 (순서 중요: 긴 패턴 먼저)
# ──────────────────────────────────────────
CORP_PATTERNS = [
    r"농업회사법인\s*주식회사",
    r"농업회사법인\s*\(주\)",
    r"농업회사법인",
    r"영농조합법인",
    r"사회적협동조합",
    r"유한책임회사",
    r"사단법인",
    r"재단법인",
    r"협동조합",
    r"합자회사",
    r"합명회사",
    r"주식회사",
    r"유한회사",
    r"\(주\)",
    r"\(유\)",
    r"\(한\)",
    r"\(사\)",
    r"㈜",
    r"㈜",
]

# ──────────────────────────────────────────
# 영문 -> 한글 외래어 매핑 (단어/약어 단위, 긴 패턴 먼저)
# ──────────────────────────────────────────
ENGLISH_TO_KOREAN_WORDS = {
    # 복합 약어 (& 포함)
    "F&B": "에프앤비",
    "F&C": "에프앤씨",
    "C&F": "씨앤에프",
    "C&N": "씨앤엔",
    "M&F": "엠앤에프",
    "P&E": "피앤이",
    "P&W": "피앤더블유",
    "R&D": "알앤디",
    "E&G": "이앤지",
    "E&C": "이앤씨",
    "E&S": "이앤에스",
    "F&D": "에프앤디",
    # 일반 단어
    "AUTO":      "오토",
    "TECH":      "테크",
    "POWER":     "파워",
    "STEEL":     "스틸",
    "COLOR":     "컬러",
    "COMPANY":   "컴퍼니",
    "HOME":      "홈",
    "FOOD":      "푸드",
    "GLOBAL":    "글로벌",
    "SYSTEM":    "시스템",
    "SYSTEMS":   "시스템즈",
    "ENGINEERING": "엔지니어링",
    "ENGINEER":  "엔지니어",
    "SOLUTION":  "솔루션",
    "WORLD":     "월드",
    "KOREA":     "코리아",
    "PRIME":     "프라임",
    "MARINE":    "마린",
    "PRECISION": "프리시전",
    # 3글자 약어
    "ENG": "이엔지",
    "IPC": "아이피씨",
    "PMC": "피엠씨",
    "GMP": "지엠피",
    "LED": "엘이디",
    "JMC": "제이엠씨",
    "TMC": "티엠씨",
    "NSK": "엔에스케이",
    "RGB": "알지비",
    "HMO": "에이치엠오",
    "ANC": "에이앤씨",
    "MNC": "엠엔씨",
    "LKS": "엘케이에스",
    "AFW": "에이에프더블유",
    # 2글자 약어
    "OA": "오에이",
    "FS": "에프에스",
    "SJ": "에스제이",
    "YK": "와이케이",
    "SH": "에스에이치",
    "HS": "에이치에스",
    "HK": "에이치케이",
    "MS": "엠에스",
    "DK": "디케이",
    "FK": "에프케이",
    "SK": "에스케이",
    "NK": "엔케이",
    "BH": "비에이치",
}

# ──────────────────────────────────────────
# 알파벳 단위 한글 매핑 (fallback)
# ──────────────────────────────────────────
ALPHABET_TO_KOREAN = {
    "A": "에이", "B": "비", "C": "씨", "D": "디", "E": "이",
    "F": "에프", "G": "지", "H": "에이치", "I": "아이", "J": "제이",
    "K": "케이", "L": "엘", "M": "엠", "N": "엔", "O": "오",
    "P": "피", "Q": "큐", "R": "알", "S": "에스", "T": "티",
    "U": "유", "V": "브이", "W": "더블유", "X": "엑스", "Y": "와이",
    "Z": "제트",
}

# ──────────────────────────────────────────
# 한글 외래어 -> 영문 역변환 매핑 (긴 패턴 먼저 매칭)
# ──────────────────────────────────────────
KOREAN_TO_ENGLISH = {
    # 복합 외래어 (긴 것 먼저)
    "엔지니어링": "engineering",
    "엔지니어": "engineer",
    "시스템즈": "systems",
    "프리시전": "precision",
    "에프앤비": "fnb",
    "에프앤씨": "fnc",
    "에프앤디": "fnd",
    "씨앤에프": "cnf",
    "씨앤엔": "cnn",
    "엠앤에프": "mnf",
    "피앤더블유": "pnw",
    "피앤이": "pne",
    "이앤지": "eng",
    "이앤씨": "enc",
    "이앤에스": "ens",
    "알앤디": "rnd",
    "에이앤씨": "anc",
    "에이에프더블유": "afw",
    "에이치엠오": "hmo",
    "엔에스케이": "nsk",
    "아이피씨": "ipc",
    "제이엠씨": "jmc",
    "에이치케이": "hk",
    "에스에이치": "sh",
    "에이치에스": "hs",
    "비에이치": "bh",
    "글로벌": "global",
    "솔루션": "solution",
    "시스템": "system",
    "컴퍼니": "company",
    "코리아": "korea",
    "프라임": "prime",
    "마린": "marine",
    "스틸": "steel",
    "컬러": "color",
    "피엠씨": "pmc",
    "지엠피": "gmp",
    "엘이디": "led",
    "티엠씨": "tmc",
    "알지비": "rgb",
    "엠엔씨": "mnc",
    "엘케이에스": "lks",
    "에프에스": "fs",
    "에스제이": "sj",
    "와이케이": "yk",
    "에프케이": "fk",
    "에스케이": "sk",
    "엔케이": "nk",
    "디케이": "dk",
    "엠에스": "ms",
    "오에이": "oa",
    "오토": "auto",
    "테크": "tech",
    "파워": "power",
    "푸드": "food",
    "월드": "world",
    "홈": "home",
    # 알파벳 단위 역매핑 (단독, 짧은 것은 마지막)
    "더블유": "w",
    "에이치": "h",
    "에이": "a",
    "에프": "f",
    "에스": "s",
    "엑스": "x",
    "제이": "j",
    "케이": "k",
    "아이": "i",
    "브이": "v",
    "와이": "y",
    "제트": "z",
    "엠": "m",
    "엔": "n",
    "알": "r",
    "피": "p",
    "큐": "q",
    "씨": "c",
    "디": "d",
    "이": "e",
    "비": "b",
    "지": "g",
    "오": "o",
    "유": "u",
    "티": "t",
    "엘": "l",
}

# 길이 내림차순 정렬된 키 리스트 (매칭 시 긴 패턴 우선)
_KOREAN_TO_ENG_KEYS = sorted(KOREAN_TO_ENGLISH.keys(), key=len, reverse=True)
_ENG_TO_KOR_KEYS = sorted(ENGLISH_TO_KOREAN_WORDS.keys(), key=len, reverse=True)

# ──────────────────────────────────────────
# 한글 자모 -> 로마자 음역 (국어의 로마자 표기법 기반 간소화)
# ──────────────────────────────────────────
_CHO = list("ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ")
_JUNG = list("ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ")
_JONG = [""] + list("ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ")

_CHO_ROMAN = {
    "ㄱ": "g", "ㄲ": "kk", "ㄴ": "n", "ㄷ": "d", "ㄸ": "tt",
    "ㄹ": "r", "ㅁ": "m", "ㅂ": "b", "ㅃ": "pp", "ㅅ": "s",
    "ㅆ": "ss", "ㅇ": "", "ㅈ": "j", "ㅉ": "jj", "ㅊ": "ch",
    "ㅋ": "k", "ㅌ": "t", "ㅍ": "p", "ㅎ": "h",
}

_JUNG_ROMAN = {
    "ㅏ": "a", "ㅐ": "ae", "ㅑ": "ya", "ㅒ": "yae", "ㅓ": "eo",
    "ㅔ": "e", "ㅕ": "yeo", "ㅖ": "ye", "ㅗ": "o", "ㅘ": "wa",
    "ㅙ": "wae", "ㅚ": "oe", "ㅛ": "yo", "ㅜ": "u", "ㅝ": "wo",
    "ㅞ": "we", "ㅟ": "wi", "ㅠ": "yu", "ㅡ": "eu", "ㅢ": "ui",
    "ㅣ": "i",
}

_JONG_ROMAN = {
    "": "", "ㄱ": "k", "ㄲ": "k", "ㄳ": "k", "ㄴ": "n",
    "ㄵ": "n", "ㄶ": "n", "ㄷ": "t", "ㄹ": "l", "ㄺ": "l",
    "ㄻ": "m", "ㄼ": "l", "ㄽ": "l", "ㄾ": "l", "ㄿ": "l",
    "ㅀ": "l", "ㅁ": "m", "ㅂ": "p", "ㅄ": "p", "ㅅ": "t",
    "ㅆ": "t", "ㅇ": "ng", "ㅈ": "t", "ㅊ": "t", "ㅋ": "k",
    "ㅌ": "t", "ㅍ": "p", "ㅎ": "t",
}


def hangul_to_roman(text: str) -> str:
    """한글 텍스트를 로마자로 음역합니다 (국어 로마자 표기법 간소화).

    Args:
        text: 한글 텍스트

    Returns:
        로마자 음역 결과 (소문자)
    """
    result = []
    for ch in text:
        code = ord(ch)
        # 한글 음절 범위: 0xAC00 ~ 0xD7A3
        if 0xAC00 <= code <= 0xD7A3:
            offset = code - 0xAC00
            cho_idx = offset // (21 * 28)
            jung_idx = (offset % (21 * 28)) // 28
            jong_idx = offset % 28
            cho = _CHO[cho_idx]
            jung = _JUNG[jung_idx]
            jong = _JONG[jong_idx]
            result.append(_CHO_ROMAN.get(cho, ""))
            result.append(_JUNG_ROMAN.get(jung, ""))
            result.append(_JONG_ROMAN.get(jong, ""))
        elif ch.isascii() and ch.isalpha():
            result.append(ch.lower())
        # 숫자, 기타 문자는 무시
    return "".join(result)


def english_to_korean(text: str) -> str:
    """영문 토큰을 한글 외래어로 변환합니다.

    단어/약어 매핑을 먼저 시도하고, 매칭되지 않으면 알파벳 단위로 변환합니다.

    Args:
        text: 영문이 포함된 텍스트 (법인표기/괄호 제거 후)

    Returns:
        영문이 한글로 변환된 텍스트
    """
    if not text:
        return text

    result = text

    # 1단계: 단어/약어 단위 매핑 (대문자 변환 후 매칭, 긴 패턴 먼저)
    for eng_key in _ENG_TO_KOR_KEYS:
        pattern = re.compile(re.escape(eng_key), re.IGNORECASE)
        result = pattern.sub(ENGLISH_TO_KOREAN_WORDS[eng_key], result)

    # 2단계: 남은 영문 알파벳을 개별 변환
    def replace_remaining_alpha(match):
        """매칭된 영문 연속 문자열을 알파벳 단위로 한글 변환"""
        eng_seq = match.group(0)
        return "".join(ALPHABET_TO_KOREAN.get(c.upper(), c) for c in eng_seq)

    result = re.sub(r"[A-Za-z]+", replace_remaining_alpha, result)

    return result


def korean_to_english_key(text: str) -> str:
    """한글 정규화 텍스트를 전체 영문으로 변환합니다.

    외래어 부분은 영문 역변환, 한글 고유어 부분은 로마자 음역을 적용합니다.

    Args:
        text: 한글 정규화 텍스트 (회사명_정규화)

    Returns:
        전체 영문 소문자 표현 (회사명_영문)
    """
    if not text:
        return ""

    result = text
    # 1단계: 외래어 -> 영문 역변환 (긴 패턴 먼저)
    for kor_key in _KOREAN_TO_ENG_KEYS:
        if kor_key in result:
            result = result.replace(kor_key, KOREAN_TO_ENGLISH[kor_key])

    # 2단계: 남은 한글 -> 로마자 음역
    parts = []
    i = 0
    while i < len(result):
        ch = result[i]
        if 0xAC00 <= ord(ch) <= 0xD7A3:
            # 한글 음절 연속 구간 모으기
            kor_start = i
            while i < len(result) and 0xAC00 <= ord(result[i]) <= 0xD7A3:
                i += 1
            parts.append(hangul_to_roman(result[kor_start:i]))
        elif ch.isascii() and ch.isalpha():
            parts.append(ch.lower())
            i += 1
        else:
            # 숫자, 특수문자 등은 건너뜀
            i += 1
    return "".join(parts)


def normalize_company_name(name: str) -> str:
    """기업명 정규화 v1.2:

    1. 법인 표기 제거
    2. 괄호 처리 (괄호 안 한글이면 해당 부분 활용)
    3. 영문 -> 한글 외래어 변환
    4. 특수문자/공백 제거

    Args:
        name: 원본 회사명

    Returns:
        정규화된 회사명 (한글 중심)
    """
    if not isinstance(name, str) or not name.strip():
        return ""

    result = name.strip()

    # 1. 법인 표기 제거
    for pattern in CORP_PATTERNS:
        result = re.sub(pattern, "", result)

    # 2. 괄호 처리: 괄호 안에 한글이 있으면 괄호 밖 영문 대신 괄호 안 한글 사용
    # 예: ISK(아이에스케이) -> 아이에스케이
    # 예: 테스코(TESCO) -> 테스코 (괄호 안이 영문이면 그냥 제거)
    paren_match = re.search(r"\(([^)]+)\)", result)
    if paren_match:
        paren_content = paren_match.group(1).strip()
        has_korean_in_paren = bool(re.search(r"[가-힣]", paren_content))
        has_korean_outside = bool(re.search(r"[가-힣]", result[:paren_match.start()]))

        if has_korean_in_paren and not has_korean_outside:
            # 괄호 밖이 영문이고 괄호 안이 한글 -> 괄호 안 한글을 사용
            result = paren_content
        else:
            # 괄호 제거
            result = re.sub(r"\([^)]*\)", "", result)
    else:
        result = re.sub(r"\([^)]*\)", "", result)

    # 3. 영문 -> 한글 외래어 변환
    result = english_to_korean(result)

    # 4. 공백/특수문자 제거
    result = re.sub(r"[^\w가-힣]", "", result)
    result = re.sub(r"[\s\-_.,&]+", "", result)
    # 숫자 제거 (선택적: 회사명에서 숫자는 보통 불필요)
    # result = re.sub(r"\d+", "", result)

    return result


def clean_company_names(df: pd.DataFrame, name_col: str = "회사명") -> tuple:
    """DataFrame의 기업명을 정제합니다.

    Args:
        df: 원본 DataFrame
        name_col: 회사명 컬럼명

    Returns:
        (정제된_df, 통계_dict)
    """
    stats = {
        "총_건수": len(df),
        "법인표기_포함": 0,
        "영문_포함": 0,
        "영문_변환": 0,
        "중복_그룹": 0,
        "중복_건수": 0,
        "회사명결함": 0,
    }

    normalized_names = []
    english_names = []
    notes = []
    company_tags = []  # v1.6: 회사명 결함 태그

    for idx in df.index:
        raw_name = str(df.at[idx, name_col]) if pd.notna(df.at[idx, name_col]) else ""

        # 원본에서 영문 존재 여부 확인
        has_english = bool(re.search(r"[A-Za-z]", raw_name))

        # 법인 표기 포함 여부
        has_corp = any(re.search(p, raw_name) for p in CORP_PATTERNS)
        if has_corp:
            stats["법인표기_포함"] += 1

        # 정규화 (영문 -> 한글 외래어 변환 포함)
        norm = normalize_company_name(raw_name)
        normalized_names.append(norm)

        # 영문 컬럼: 정규화 결과를 전체 영문으로 변환
        eng_key = korean_to_english_key(norm)
        english_names.append(eng_key)

        # v1.6: 정규화 결과가 빈 문자열 → 회사명 결함 (특수문자만 입력)
        if not norm and raw_name.strip():
            company_tags.append(f"[삭제:회사명결함] 회사명확인불가({raw_name.strip()})")
            stats["회사명결함"] += 1
        else:
            company_tags.append("")

        # 통계 및 비고
        note_parts = []
        if has_english:
            stats["영문_포함"] += 1
            # 원본 영문 추출 (표시용)
            orig_eng = " ".join(re.findall(r"[A-Za-z]+", raw_name))
            stats["영문_변환"] += 1
            note_parts.append(f"[영문포함] {orig_eng}")
        notes.append("; ".join(note_parts))

    df["회사명_정규화"] = normalized_names
    df["회사명_영문"] = english_names

    # 중복 검사
    name_groups = defaultdict(list)
    for idx, norm in zip(df.index, normalized_names):
        if norm:
            name_groups[norm].append(idx)

    for norm, indices in name_groups.items():
        if len(indices) > 1:
            stats["중복_그룹"] += 1
            stats["중복_건수"] += len(indices)
            if "nid" in df.columns:
                row_refs = [df.at[i, "nid"] for i in indices]
            else:
                row_refs = [str(i + 1) for i in indices]
            dup_info = f"[중복] {len(indices)}건 - {', '.join(map(str, row_refs))}"
            for i in indices:
                if notes[i]:
                    notes[i] += f"; {dup_info}"
                else:
                    notes[i] = dup_info

    df["회사명_비고"] = notes
    df["_회사명태그"] = company_tags  # v1.6: 내부 태그 컬럼

    return df, stats


if __name__ == "__main__":
    import sys, io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    test_data = {
        "회사명": [
            "MS AUTO",
            "(주)친한F&B",
            "에이치케이파워 주식회사",
            "세광PMC",
            "ISK(아이에스케이)",
            "삼성기업",
            "(주)대일테크",
            "주식회사 대일테크",
            "에본(주) (EVON Co. Ltd)",
            "삼성기업",
            "KMTC정밀",
            "(주)RGB COLOR",
            "A.F.W(주)",
            "에이치엠오건강드림영농조합법인(HMO)",
        ]
    }
    test_df = pd.DataFrame(test_data)
    result, stats = clean_company_names(test_df)
    print("=== v1.2 test ===")
    for i, row in result.iterrows():
        print(f"  {row['회사명']:38s} | norm: {row['회사명_정규화']:18s} | eng: {row['회사명_영문']:20s} | note: {row['회사명_비고']}")
    print(f"\nstats: {stats}")
