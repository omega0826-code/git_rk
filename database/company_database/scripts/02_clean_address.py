# -*- coding: utf-8 -*-
"""
02_clean_address.py - 공장주소 정제 모듈
공장주소(도로명)와 공장주소_지번을 정제합니다.
기존 address_cleaning_guideline.md 패턴을 확장 적용합니다.
"""

import re
import pandas as pd

# ──────────────────────────────────────────
# 시도 오타 수정 매핑
# ──────────────────────────────────────────
SIDO_CORRECTIONS = {
    "경산북도": "경상북도",
    "경상남북도": "경상북도",
    "대구시": "대구광역시",
    "대구광역시시": "대구광역시",
    "대구광여깃": "대구광역시",
    "부삭광역시": "부산광역시",
    "부선광역시": "부산광역시",
    "인천관역시": "인천광역시",
    "충청북도도": "충청북도",
    "경기고": "경기도",
    "전북특별자치고": "전북특별자치도",
    "충천남도": "충청남도",
    "충천북도": "충청북도",
    "강원특별자지도": "강원특별자치도",
    # v1.6: 불완전/구 시도명 교정
    "제주특별자치": "제주특별자치도",
    "제주도": "제주특별자치도",
    "전라북도": "전북특별자치도",
    "강원도": "강원특별자치도",
}

# ──────────────────────────────────────────
# 시도 약어 확장
# ──────────────────────────────────────────
SIDO_ABBREV = {
    "서울": "서울특별시",
    "부산": "부산광역시",
    "대구": "대구광역시",
    "인천": "인천광역시",
    "광주": "광주광역시",
    "대전": "대전광역시",
    "울산": "울산광역시",
    "세종": "세종특별자치시",
    "경기": "경기도",
    "강원": "강원특별자치도",
    "충북": "충청북도",
    "충남": "충청남도",
    "전북": "전북특별자치도",
    "전남": "전라남도",
    "경북": "경상북도",
    "경남": "경상남도",
    "제주": "제주특별자치도",
}

# ──────────────────────────────────────────
# 유효한 시도 목록
# ──────────────────────────────────────────
VALID_SIDO = {
    "서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시",
    "대전광역시", "울산광역시", "세종특별자치시", "경기도",
    "강원특별자치도", "충청북도", "충청남도", "전북특별자치도",
    "전라남도", "경상북도", "경상남도", "제주특별자치도",
}

# ──────────────────────────────────────────
# 시군구 → 시도 역매핑 사전 (시도명 누락 시 fallback)
# ──────────────────────────────────────────
SIGUNGU_TO_SIDO = {
    # 서울특별시 자치구 (25)
    "종로구": "서울특별시", "중구": "서울특별시", "용산구": "서울특별시",
    "성동구": "서울특별시", "광진구": "서울특별시", "동대문구": "서울특별시",
    "중랑구": "서울특별시", "성북구": "서울특별시", "강북구": "서울특별시",
    "도봉구": "서울특별시", "노원구": "서울특별시", "은평구": "서울특별시",
    "서대문구": "서울특별시", "마포구": "서울특별시", "양천구": "서울특별시",
    "강서구": "서울특별시", "구로구": "서울특별시", "금천구": "서울특별시",
    "영등포구": "서울특별시", "동작구": "서울특별시", "관악구": "서울특별시",
    "서초구": "서울특별시", "강남구": "서울특별시", "송파구": "서울특별시",
    "강동구": "서울특별시",
    # 부산광역시 자치구/군 (16)
    "부산진구": "부산광역시", "동래구": "부산광역시", "남구": "부산광역시",
    "북구": "부산광역시", "해운대구": "부산광역시", "사하구": "부산광역시",
    "금정구": "부산광역시", "연제구": "부산광역시", "수영구": "부산광역시",
    "사상구": "부산광역시", "기장군": "부산광역시",
    # 대구광역시 자치구/군 (8)
    "수성구": "대구광역시", "달서구": "대구광역시", "달성군": "대구광역시",
    "군위군": "대구광역시",
    # 인천광역시 자치구/군 (10)
    "미추홀구": "인천광역시", "연수구": "인천광역시", "남동구": "인천광역시",
    "부평구": "인천광역시", "계양구": "인천광역시", "서구": "인천광역시",
    "강화군": "인천광역시", "옹진군": "인천광역시",
    # 광주광역시 자치구 (5)
    "동구": "광주광역시", "광산구": "광주광역시",
    # 대전광역시 자치구 (5)
    "대덕구": "대전광역시", "유성구": "대전광역시",
    # 울산광역시 자치구/군 (5)
    "울주군": "울산광역시",
    # ─ 경기도 시/군 (31) ─
    "수원시": "경기도", "성남시": "경기도", "안양시": "경기도",
    "부천시": "경기도", "광명시": "경기도", "평택시": "경기도",
    "동두천시": "경기도", "안산시": "경기도", "고양시": "경기도",
    "과천시": "경기도", "구리시": "경기도", "남양주시": "경기도",
    "오산시": "경기도", "시흥시": "경기도", "군포시": "경기도",
    "의왕시": "경기도", "하남시": "경기도", "용인시": "경기도",
    "파주시": "경기도", "이천시": "경기도", "안성시": "경기도",
    "김포시": "경기도", "화성시": "경기도", "광주시": "경기도",
    "양주시": "경기도", "포천시": "경기도", "여주시": "경기도",
    "연천군": "경기도", "가평군": "경기도", "양평군": "경기도",
    "의정부시": "경기도",
    # ─ 강원특별자치도 시/군 (18) ─
    "춘천시": "강원특별자치도", "원주시": "강원특별자치도", "강릉시": "강원특별자치도",
    "동해시": "강원특별자치도", "태백시": "강원특별자치도", "속초시": "강원특별자치도",
    "삼척시": "강원특별자치도", "홍천군": "강원특별자치도", "횡성군": "강원특별자치도",
    "영월군": "강원특별자치도", "평창군": "강원특별자치도", "정선군": "강원특별자치도",
    "철원군": "강원특별자치도", "화천군": "강원특별자치도", "양구군": "강원특별자치도",
    "인제군": "강원특별자치도", "고성군": "강원특별자치도", "양양군": "강원특별자치도",
    # ─ 충청북도 시/군 (11) ─
    "청주시": "충청북도", "충주시": "충청북도", "제천시": "충청북도",
    "보은군": "충청북도", "옥천군": "충청북도", "영동군": "충청북도",
    "증평군": "충청북도", "진천군": "충청북도", "괴산군": "충청북도",
    "음성군": "충청북도", "단양군": "충청북도",
    # ─ 충청남도 시/군 (15) ─
    "천안시": "충청남도", "공주시": "충청남도", "보령시": "충청남도",
    "아산시": "충청남도", "서산시": "충청남도", "논산시": "충청남도",
    "계룡시": "충청남도", "당진시": "충청남도", "금산군": "충청남도",
    "부여군": "충청남도", "서천군": "충청남도", "청양군": "충청남도",
    "홍성군": "충청남도", "예산군": "충청남도", "태안군": "충청남도",
    # ─ 전북특별자치도 시/군 (14) ─
    "전주시": "전북특별자치도", "군산시": "전북특별자치도", "익산시": "전북특별자치도",
    "정읍시": "전북특별자치도", "남원시": "전북특별자치도", "김제시": "전북특별자치도",
    "완주군": "전북특별자치도", "진안군": "전북특별자치도", "무주군": "전북특별자치도",
    "장수군": "전북특별자치도", "임실군": "전북특별자치도", "순창군": "전북특별자치도",
    "고창군": "전북특별자치도", "부안군": "전북특별자치도",
    # ─ 전라남도 시/군 (22) ─
    "목포시": "전라남도", "여수시": "전라남도", "순천시": "전라남도",
    "나주시": "전라남도", "광양시": "전라남도", "담양군": "전라남도",
    "곡성군": "전라남도", "구례군": "전라남도", "고흥군": "전라남도",
    "보성군": "전라남도", "화순군": "전라남도", "장흥군": "전라남도",
    "강진군": "전라남도", "해남군": "전라남도", "영암군": "전라남도",
    "무안군": "전라남도", "함평군": "전라남도", "영광군": "전라남도",
    "장성군": "전라남도", "완도군": "전라남도", "진도군": "전라남도",
    "신안군": "전라남도",
    # ─ 경상북도 시/군 (23) ─
    "포항시": "경상북도", "경주시": "경상북도", "김천시": "경상북도",
    "안동시": "경상북도", "구미시": "경상북도", "영주시": "경상북도",
    "영천시": "경상북도", "상주시": "경상북도", "문경시": "경상북도",
    "경산시": "경상북도", "의성군": "경상북도", "청송군": "경상북도",
    "영양군": "경상북도", "영덕군": "경상북도", "청도군": "경상북도",
    "고령군": "경상북도", "성주군": "경상북도", "칠곡군": "경상북도",
    "예천군": "경상북도", "봉화군": "경상북도", "울진군": "경상북도",
    "울릉군": "경상북도",
    # ─ 경상남도 시/군 (18) ─
    "창원시": "경상남도", "진주시": "경상남도", "통영시": "경상남도",
    "사천시": "경상남도", "김해시": "경상남도", "밀양시": "경상남도",
    "거제시": "경상남도", "양산시": "경상남도", "의령군": "경상남도",
    "함안군": "경상남도", "창녕군": "경상남도", "고성군": "경상남도",
    "남해군": "경상남도", "하동군": "경상남도", "산청군": "경상남도",
    "함양군": "경상남도", "거창군": "경상남도", "합천군": "경상남도",
    # ─ 제주특별자치도 시 (2) ─
    "제주시": "제주특별자치도", "서귀포시": "제주특별자치도",
}

# ──────────────────────────────────────────
# 일반시 산하 기초구 매핑 (시명 → 구 목록)
# 특별시/광역시 자치구는 포함하지 않음
# ──────────────────────────────────────────
CITY_GU_MAP = {
    "수원시": {"장안구", "권선구", "팔달구", "영통구"},
    "성남시": {"수정구", "중원구", "분당구"},
    "안양시": {"만안구", "동안구"},
    "안산시": {"상록구", "단원구"},
    "고양시": {"덕양구", "일산동구", "일산서구"},
    "용인시": {"처인구", "기흥구", "수지구"},
    "청주시": {"흥덕구", "서원구", "상당구", "청원구"},
    "천안시": {"서북구", "동남구"},
    "전주시": {"완산구", "덕진구"},
    "포항시": {"남구", "북구"},
    "창원시": {"의창구", "성산구", "마산합포구", "마산회원구", "진해구"},
}

# ──────────────────────────────────────────
# 시도-시군구 붙어쓰기 분리 패턴
# 예: "부산광역시기장군" → "부산광역시 기장군"
# ──────────────────────────────────────────
_SIDO_NAMES_SORTED = sorted(VALID_SIDO, key=len, reverse=True)  # 긴 이름 우선
_SIDO_GROUP = "|".join(re.escape(s) for s in _SIDO_NAMES_SORTED)
JOINED_SIDO_SIGUNGU_PATTERN = re.compile(
    rf"^({_SIDO_GROUP})([가-힣]+(?:시|군|구))"
)

# ──────────────────────────────────────────
# 붙어쓰기 보정 패턴 (시군구 내부 구가 붙은 경우)
# ──────────────────────────────────────────
JOINED_SIGUNGU_PATTERNS = [
    # 충청북도 청주시흥덕구 → 충청북도 청주시 흥덕구
    (r"(청주시)(흥덕구|서원구|상당구|청원구)", r"\1 \2"),
    # 충청남도 천안시서북구 → 충청남도 천안시 서북구
    (r"(천안시)(서북구|동남구)", r"\1 \2"),
    # 용인시처인구 → 용인시 처인구
    (r"(용인시)(처인구|기흥구|수지구)", r"\1 \2"),
]

# ──────────────────────────────────────────
# 읍면동 추출 패턴
# ──────────────────────────────────────────
# 지번 주소에서: {시도} {시군구} [{구}] {읍|면} ...
EUPMYEONDONG_JIBUN_PATTERN = re.compile(
    r'(?:[가-힣]+[시군구]\s+)'
    r'(?:[가-힣]+[구]\s+)?'
    r'([가-힣]+(?:읍|면))\s'
)
# 지번 주소에서 동 추출: {시도} {시군구} [{구}] {동}{N가} ...
DONG_JIBUN_PATTERN = re.compile(
    r'(?:[가-힣]+[시군구]\s+)'
    r'(?:[가-힣]+[구]\s+)?'
    r'([가-힣\d]+동(?:\d+가)?)\s'
)
# 도로명 주소 괄호 내 동명: (xxx동), (xxx동, 건물명)
DONG_PAREN_PATTERN = re.compile(
    r'\(([가-힣\d]+동(?:\d+가)?)(?:,|\))'
)
# 지번 주소에서 리 추출 (읍면 다음): {읍|면} {리} ...
RI_JIBUN_PATTERN = re.compile(
    r'(?:[가-힣]+(?:읍|면)\s+)'
    r'([가-힣]+리)\s'
)


def extract_eupmyeondong(road_addr: str, jibun_addr: str) -> str:
    """
    정제된 주소에서 읍면동명을 추출합니다.
    우선순위: 지번주소(읍면) → 지번주소(동) → 도로명 괄호 내 동명 → 도로명(동)
    Returns: 읍면동명 문자열 (추출 실패 시 빈 문자열)
    """
    # 1차: 지번 주소에서 읍/면 추출
    if jibun_addr:
        m = EUPMYEONDONG_JIBUN_PATTERN.search(jibun_addr)
        if m:
            return m.group(1)
        # 2차: 지번 주소에서 동 추출
        m = DONG_JIBUN_PATTERN.search(jibun_addr)
        if m:
            return m.group(1)

    # 3차: 도로명 주소 괄호 내 동명
    if road_addr:
        m = DONG_PAREN_PATTERN.search(road_addr)
        if m:
            return m.group(1)

    # 4차: 도로명 주소에서도 동 패턴 시도
    if road_addr:
        m = DONG_JIBUN_PATTERN.search(road_addr)
        if m:
            return m.group(1)

    return ""


def normalize_whitespace(text: str) -> str:
    """공백 정규화: 앞뒤 trim + 연속 공백 제거"""
    if not isinstance(text, str):
        return ""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def correct_sido(addr: str) -> tuple:
    """시도 오타 수정 및 약어 확장. (수정된주소, 수정내역) 반환"""
    if not addr:
        return addr, None

    parts = addr.split(maxsplit=1)
    first = parts[0]
    rest = parts[1] if len(parts) > 1 else ""

    # 오타 수정
    if first in SIDO_CORRECTIONS:
        corrected = SIDO_CORRECTIONS[first]
        new_addr = f"{corrected} {rest}".strip()
        return new_addr, f"오타수정: {first}→{corrected}"

    # 약어 확장
    if first in SIDO_ABBREV:
        expanded = SIDO_ABBREV[first]
        new_addr = f"{expanded} {rest}".strip()
        return new_addr, f"약어확장: {first}→{expanded}"

    return addr, None


def fix_joined_sido_sigungu(addr: str) -> tuple:
    """시도-시군구 붙어쓰기 분리. (수정된주소, 수정내역) 반환
    예: '부산광역시기장군 ...' → '부산광역시 기장군 ...'
    """
    if not addr:
        return addr, None

    parts = addr.split(maxsplit=1)
    first = parts[0]
    rest = parts[1] if len(parts) > 1 else ""

    m = JOINED_SIDO_SIGUNGU_PATTERN.match(first)
    if m:
        sido = m.group(1)
        sigungu = m.group(2)
        # 시도 뒤에 시군구가 바로 붙은 경우만 (완전히 분리되는 케이스)
        if sido + sigungu == first:
            new_addr = f"{sido} {sigungu} {rest}".strip()
            return new_addr, f"시도시군구분리: {first}→{sido} {sigungu}"
    return addr, None


def fix_joined_sigungu(addr: str) -> tuple:
    """시군구 붙어쓰기 보정. (수정된주소, 수정내역) 반환"""
    if not addr:
        return addr, None

    original = addr
    for pattern, replacement in JOINED_SIGUNGU_PATTERNS:
        addr = re.sub(pattern, replacement, addr)

    if addr != original:
        return addr, f"붙어쓰기보정"
    return addr, None


def tokenize_full_address(addr: str) -> tuple:
    """완전 붙어쓰기된 주소를 행정구역 경계에서 토큰화합니다.
    예: '경기도수원시장안구이목동123' → '경기도 수원시 장안구 이목동 123'
    Returns: (토큰화된_주소, 수정내역 or None)
    """
    if not addr:
        return addr, None

    # 이미 공백이 있으면 토큰화 불필요
    if " " in addr:
        return addr, None

    original = addr

    # 1단계: 시도명 분리 (VALID_SIDO 중 매칭되는 접두사)
    for sido in _SIDO_NAMES_SORTED:  # 긴 이름 우선
        if addr.startswith(sido):
            addr = sido + " " + addr[len(sido):]
            break

    # 2단계: 시군구 경계 분리 (시/군/구로 끝나는 단위)
    # "수원시장안구이목동" → "수원시 장안구 이목동"
    addr = re.sub(r'([가-힣]+시)([가-힣])', r'\1 \2', addr)
    addr = re.sub(r'([가-힣]+군)([가-힣])', r'\1 \2', addr)
    addr = re.sub(r'([가-힣]+구)([가-힣])', r'\1 \2', addr)

    # 3단계: 읍면동리 경계 분리
    addr = re.sub(r'([가-힣]+읍)([가-힣])', r'\1 \2', addr)
    addr = re.sub(r'([가-힣]+면)([가-힣])', r'\1 \2', addr)
    addr = re.sub(r'([가-힣]+동)(\d)', r'\1 \2', addr)
    addr = re.sub(r'([가-힣]+리)(\d)', r'\1 \2', addr)

    # 4단계: 도로명(로/길) 경계 분리
    addr = re.sub(r'([가-힣]+로)(\d)', r'\1 \2', addr)
    addr = re.sub(r'([가-힣]+길)(\d)', r'\1 \2', addr)

    # 연속 공백 정리
    addr = re.sub(r'\s+', ' ', addr).strip()

    if addr != original:
        return addr, "붙어쓰기_토큰화"
    return addr, None


def clean_single_address(addr: str) -> tuple:
    """
    단일 주소를 정제합니다.
    Returns: (정제된_주소, [수정내역_리스트])
    """
    changes = []

    # 1. 공백 정규화
    cleaned = normalize_whitespace(addr)
    if cleaned != addr and addr and isinstance(addr, str) and addr.strip():
        changes.append("공백정규화")

    if not cleaned:
        return "", changes

    # 2. 완전 붙어쓰기 주소 토큰화 (v1.5)
    cleaned, change = tokenize_full_address(cleaned)
    if change:
        changes.append(change)

    # 3. 시도 오타/약어 수정
    cleaned, change = correct_sido(cleaned)
    if change:
        changes.append(change)

    # 4. 시도-시군구 붙어쓰기 분리 (예: 부산광역시기장군 → 부산광역시 기장군)
    cleaned, change = fix_joined_sido_sigungu(cleaned)
    if change:
        changes.append(change)

    # 5. 시군구 내부 붙어쓰기 보정 (예: 청주시흥덕구 → 청주시 흥덕구)
    cleaned, change = fix_joined_sigungu(cleaned)
    if change:
        changes.append(change)

    return cleaned, changes


def is_address_valid(road_addr: str, jibun_addr: str) -> tuple:
    """
    주소 유효성 검사.
    Returns: (유효여부, 태그)
    """
    road = normalize_whitespace(str(road_addr)) if pd.notna(road_addr) else ""
    jibun = normalize_whitespace(str(jibun_addr)) if pd.notna(jibun_addr) else ""

    # 양쪽 모두 빈칸
    if not road and not jibun:
        return False, "[삭제:주소결함] 도로명+지번 모두 빈칸"

    # 시도명만 있고 상세 없는 경우 검사
    for addr_type, addr in [("도로명", road), ("지번", jibun)]:
        if addr:
            parts = addr.split()
            if len(parts) <= 1 and parts[0] in VALID_SIDO:
                # 상대편 주소도 불완전하면 삭제
                other = jibun if addr_type == "도로명" else road
                if not other or len(other.split()) <= 1:
                    return False, f"[삭제:주소결함] 주소불완전({addr})"

    return True, None


def clean_addresses(df: pd.DataFrame) -> tuple:
    """
    DataFrame의 공장주소를 정제합니다.
    Returns: (정제된_df, 통계_dict)
    """
    stats = {
        "공백정규화": 0,
        "오타수정": 0,
        "약어확장": 0,
        "시도시군구분리": 0,
        "붙어쓰기보정": 0,
        "붙어쓰기_토큰화": 0,
        "주소결함": 0,
        "시도_도로명복사": 0,
        "총_수정": 0,
    }

    # 정제 컬럼 생성
    df["공장주소_클리닝"] = ""
    df["공장주소_지번_클리닝"] = ""

    # 주소 유효성 태그
    addr_tags = []

    for idx in df.index:
        # 도로명 주소 정제
        road_raw = str(df.at[idx, "공장주소"]) if pd.notna(df.at[idx, "공장주소"]) else ""
        road_cleaned, road_changes = clean_single_address(road_raw)
        df.at[idx, "공장주소_클리닝"] = road_cleaned

        # 지번 주소 정제
        jibun_raw = str(df.at[idx, "공장주소_지번"]) if pd.notna(df.at[idx, "공장주소_지번"]) else ""
        jibun_cleaned, jibun_changes = clean_single_address(jibun_raw)
        df.at[idx, "공장주소_지번_클리닝"] = jibun_cleaned

        # 통계 집계
        all_changes = road_changes + jibun_changes
        for c in all_changes:
            if "오타수정" in c:
                stats["오타수정"] += 1
            elif "약어확장" in c:
                stats["약어확장"] += 1
            elif "시도시군구분리" in c:
                stats["시도시군구분리"] += 1
            elif "붙어쓰기보정" in c:
                stats["붙어쓰기보정"] += 1
            elif "붙어쓰기_토큰화" in c:
                stats["붙어쓰기_토큰화"] += 1
            elif "공백정규화" in c:
                stats["공백정규화"] += 1
        if all_changes:
            stats["총_수정"] += 1

        # 유효성 검사
        valid, tag = is_address_valid(road_cleaned, jibun_cleaned)
        if not valid:
            stats["주소결함"] += 1
        addr_tags.append(tag if tag else "")

    df["_주소태그"] = addr_tags

    # ──────────────────────────────────────────
    # 읍면동명, 시도명, 시군구명, 구(기초) 추출 (v1.5)
    # ──────────────────────────────────────────
    eupmyeondong_list = []
    sido_list = []
    sigungu_list = []
    gu_gicho_list = []  # v1.5: 구(기초) 컬럼

    for idx in df.index:
        road_cleaned = str(df.at[idx, "공장주소_클리닝"]) if pd.notna(df.at[idx, "공장주소_클리닝"]) else ""
        jibun_cleaned = str(df.at[idx, "공장주소_지번_클리닝"]) if pd.notna(df.at[idx, "공장주소_지번_클리닝"]) else ""

        # 읍면동
        emd = extract_eupmyeondong(road_cleaned, jibun_cleaned)
        eupmyeondong_list.append(emd)

        # 시도명 / 시군구명 / 구(기초) 파생
        target_addr = road_cleaned if len(road_cleaned) >= len(jibun_cleaned) else jibun_cleaned
        sido = ""
        sigungu = ""
        gu_gicho = ""

        if target_addr:
            parts = target_addr.split()
            sido_candidate = parts[0] if len(parts) > 0 else ""

            if sido_candidate in VALID_SIDO:
                # ── 정상 케이스: 첫 토큰이 유효 시도 ──
                sido = sido_candidate
                sigungu = parts[1] if len(parts) > 1 else ""

                # 일반시 산하 기초구 분리 (v1.5)
                if sigungu in CITY_GU_MAP and len(parts) > 2:
                    gu_candidate = parts[2]
                    if gu_candidate in CITY_GU_MAP[sigungu]:
                        gu_gicho = gu_candidate

            elif sido_candidate in SIGUNGU_TO_SIDO:
                # ── Fallback: 시도 누락, 첫 토큰이 시군구 ──
                sido = SIGUNGU_TO_SIDO[sido_candidate]
                sigungu = sido_candidate

                # 기초구 분리
                if sigungu in CITY_GU_MAP and len(parts) > 1:
                    gu_candidate = parts[1]
                    if gu_candidate in CITY_GU_MAP[sigungu]:
                        gu_gicho = gu_candidate

            elif sido_candidate.endswith("구") and sido_candidate in SIGUNGU_TO_SIDO:
                # ── 서울/광역시 자치구만 있는 경우 ──
                sido = SIGUNGU_TO_SIDO[sido_candidate]
                sigungu = sido_candidate

            else:
                # ── 원본 시도명 컬럼이 존재하면 활용 ──
                if "시도명" in df.columns:
                    orig_sido = str(df.at[idx, "시도명"]) if pd.notna(df.at[idx, "시도명"]) else ""
                    if orig_sido in VALID_SIDO:
                        sido = orig_sido
                        sigungu = sido_candidate if sido_candidate.endswith(("시", "군", "구")) else ""

            # ── v1.6: 시도 여전히 빈칸 → 도로명 주소에서 복사 ──
            if not sido and road_cleaned:
                road_parts = road_cleaned.split()
                if len(road_parts) >= 2 and road_parts[0] in VALID_SIDO:
                    sido = road_parts[0]
                    sigungu = road_parts[1]
                    stats["시도_도로명복사"] += 1
                    # 기초구 분리도 시도
                    if sigungu in CITY_GU_MAP and len(road_parts) > 2:
                        gu_candidate = road_parts[2]
                        if gu_candidate in CITY_GU_MAP[sigungu]:
                            gu_gicho = gu_candidate

        # ── v1.6: 세종특별자치시 특례 (시군구 없는 단층제) ──
        if sido == "세종특별자치시":
            sigungu = "세종특별자치시"

        sido_list.append(sido)
        sigungu_list.append(sigungu)
        gu_gicho_list.append(gu_gicho)

    df["시도명"] = sido_list
    df["시군구명"] = sigungu_list
    df["구(기초)"] = gu_gicho_list  # v1.5 신규
    df["읍면동명"] = eupmyeondong_list

    # ── v1.7: 모든 정제 단계 완료 후 시도명/시군구명 여전히 빈칸이면 삭제 태그 보강 ──
    addr_tags_updated = list(df["_주소태그"])
    sido_sigungu_fail_count = 0
    for i, idx in enumerate(df.index):
        sido_val = sido_list[i]
        sigungu_val = sigungu_list[i]
        if not sido_val or not sigungu_val:
            existing_tag = addr_tags_updated[i]
            fail_tag = "[삭제:주소결함] 시도/시군구 추출불가"
            if existing_tag:
                addr_tags_updated[i] = existing_tag + " | " + fail_tag
            else:
                addr_tags_updated[i] = fail_tag
            sido_sigungu_fail_count += 1
    df["_주소태그"] = addr_tags_updated
    stats["주소결함"] = sum(1 for t in addr_tags_updated if "[삭제:주소결함]" in t)
    stats["시도시군구_최종미추출"] = sido_sigungu_fail_count

    stats["읍면동_추출"] = sum(1 for e in eupmyeondong_list if e)
    stats["읍면동_미추출"] = sum(1 for e in eupmyeondong_list if not e)
    stats["시도명_정상"] = sum(1 for s in sido_list if s)
    stats["시도명_미상"] = sum(1 for s in sido_list if not s)
    stats["시도_역매핑"] = sum(1 for i, s in enumerate(sido_list) if s and sigungu_list[i] and s == SIGUNGU_TO_SIDO.get(sigungu_list[i], ""))
    stats["구기초_추출"] = sum(1 for g in gu_gicho_list if g)

    return df, stats


if __name__ == "__main__":
    # 단독 테스트 (v1.5 확장)
    test_data = {
        "공장주소": [
            "경기도 수원시 장안구 송정로 100",       # 정상 (시+기초구)
            "충청북도 청주시흥덕구 송정동",           # 시군구 붙어쓰기
            "수원시 장안구 이목동 123",               # 시도 누락
            "경기도수원시장안구이목동123",             # 완전 붙어쓰기
            "서울특별시 강남구 역삼동 123",           # 광역시 자치구
            "부산광역시 해운대구 우동 123",           # 광역시 자치구
            "",                                      # 빈칸
            "경기도",                                 # 불완전
        ],
        "공장주소_지번": [
            "경기도 수원시 장안구 이목동 56",
            "충청북도 청주시흥덕구 송정동 1-25",
            "수원시 장안구 이목동 123",
            "경기도수원시장안구이목동123",
            "서울특별시 강남구 역삼동 123",
            "부산광역시 해운대구 우동 123",
            "",
            "",
        ],
    }
    test_df = pd.DataFrame(test_data)
    result, stats = clean_addresses(test_df)
    print("=== 정제 결과 (v1.5 테스트) ===")
    for col in ["공장주소_클리닝", "공장주소_지번_클리닝", "시도명", "시군구명", "구(기초)", "읍면동명", "_주소태그"]:
        print(f"\n{col}:")
        print(result[col].tolist())
    print(f"\n통계: {stats}")
