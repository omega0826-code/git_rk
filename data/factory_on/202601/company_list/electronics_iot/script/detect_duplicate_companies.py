# -*- coding: utf-8 -*-
"""
detect_duplicate_companies.py
- 공장DB(company_electronics_iot_extracted_F.csv)와
  예비 리스트(preliminary_comany_list.csv) 간 중복 업체 교차 검출
- find_duplicates.py의 normalize_company() 로직 재활용
- 결과: 파일 A에 6개 컬럼(중복_nid + 출처 5개) 추가

작성일: 2026-03-10
"""
import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import os
import re
import pandas as pd
from datetime import datetime

# ──────────────────────────────────────────
# 경로 설정
# ──────────────────────────────────────────
BASE_DIR = r"d:\git_rk\output\company_database\factory_on\202601"
FILE_A = os.path.join(BASE_DIR, "company_electronics_iot_extracted_F.csv")
FILE_B = os.path.join(BASE_DIR, "progress", "preliminary_comany_list.csv")
TIMESTAMP = datetime.now().strftime("%y%m%d_%H%M")

# ──────────────────────────────────────────
# 정규화 상수 (find_duplicates.py에서 복사)
# ──────────────────────────────────────────
CORP_PATTERNS = [
    r"\(?\s*주\s*\)?\s*",
    r"주식회사",
    r"\(?\s*유\s*\)?\s*",
    r"\(?\s*사\s*\)?\s*",
    r"유한회사",
    r"유한책임회사",
    r"합명회사",
    r"합자회사",
    r"합자조합",
    r"농업회사법인",
    r"영농조합법인",
    r"사회적기업",
    r"사회적협동조합",
    r"협동조합",
    r"\(사\)",
    r"㈜",
    r"㈜",
]

ENGLISH_TO_KOREAN_WORDS = {
    "F&B": "에프앤비", "F&C": "에프앤씨", "C&F": "씨앤에프",
    "C&N": "씨앤엔", "M&F": "엠앤에프", "P&E": "피앤이",
    "E&C": "이앤씨", "E&S": "이앤에스", "C&I": "씨앤아이",
    "R&D": "알앤디",
    "TECHNOLOGY": "테크놀로지", "ENGINEERING": "엔지니어링",
    "SYSTEMS": "시스템즈", "SYSTEM": "시스템",
    "PRECISION": "프리시전", "SOLUTION": "솔루션",
    "SOLUTIONS": "솔루션즈", "DIGITAL": "디지털",
    "ELECTRONICS": "일렉트로닉스", "ELECTRIC": "일렉트릭",
    "NETWORK": "네트워크", "GLOBAL": "글로벌",
    "SILICON": "실리콘", "ENERGY": "에너지",
    "POWER": "파워", "WORLD": "월드",
    "TECH": "테크", "AUTO": "오토",
    "FOOD": "푸드", "HOME": "홈",
    "SOFT": "소프트", "WAVE": "웨이브",
    "LINE": "라인", "STAR": "스타",
    "TOP": "탑", "MAX": "맥스",
    "NET": "넷", "BIO": "바이오",
    "LED": "엘이디", "IOT": "아이오티",
    "ICT": "아이씨티",
    "SK": "에스케이", "LG": "엘지", "SJ": "에스제이",
    "DK": "디케이", "MS": "엠에스",
}

ALPHA_TO_KOREAN = {
    "A": "에이", "B": "비", "C": "씨", "D": "디", "E": "이",
    "F": "에프", "G": "지", "H": "에이치", "I": "아이", "J": "제이",
    "K": "케이", "L": "엘", "M": "엠", "N": "엔", "O": "오",
    "P": "피", "Q": "큐", "R": "알", "S": "에스", "T": "티",
    "U": "유", "V": "브이", "W": "더블유", "X": "엑스", "Y": "와이",
    "Z": "제트",
}

_ENG_TO_KOR_KEYS = sorted(ENGLISH_TO_KOREAN_WORDS.keys(), key=len, reverse=True)


# ──────────────────────────────────────────
# 정규화 함수 (find_duplicates.py에서 복사)
# ──────────────────────────────────────────
def _english_to_korean(text):
    upper = text.upper()
    for key in _ENG_TO_KOR_KEYS:
        if key in upper:
            upper = upper.replace(key, ENGLISH_TO_KOREAN_WORDS[key])
    def replace_remaining_alpha(match):
        chars = match.group(0).upper()
        return "".join(ALPHA_TO_KOREAN.get(c, c) for c in chars)
    upper = re.sub(r"[A-Za-z]+", replace_remaining_alpha, upper)
    return upper


def normalize_company(name):
    """사업체명 정규화: 법인표기 제거, 괄호 처리, 영문->한글, 특수문자 제거"""
    if not isinstance(name, str) or not name.strip():
        return ""
    result = name.strip()
    for pattern in CORP_PATTERNS:
        result = re.sub(pattern, "", result)
    paren_match = re.search(r"\(([^)]+)\)", result)
    if paren_match:
        paren_content = paren_match.group(1).strip()
        has_korean_in_paren = bool(re.search(r"[가-힣]", paren_content))
        has_korean_outside = bool(re.search(r"[가-힣]", result[:paren_match.start()]))
        if has_korean_in_paren and not has_korean_outside:
            result = paren_content
        else:
            result = re.sub(r"\([^)]*\)", "", result)
    else:
        result = re.sub(r"\([^)]*\)", "", result)
    result = _english_to_korean(result)
    result = re.sub(r"[^\w가-힣]", "", result)
    result = re.sub(r"[\s\-_.,&]+", "", result)
    return result


# ──────────────────────────────────────────
# 출처 컬럼명
# ──────────────────────────────────────────
SOURCE_COLS = [
    "KEA(한국전자정보통신산업진흥회)",
    "한국AI사물인터넷협회",
    "KES 2025(한국전자전)",
    "기존자료(가전)",
    "기존자료(IoT)",
]


def main():
    print("=" * 60)
    print("  중복 업체 교차 검출 (공장DB vs 예비 리스트)")
    print(f"  실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # ── 1. 데이터 로딩 ──
    print("\n[1/4] 데이터 로딩...")
    df_a = pd.read_csv(FILE_A, encoding="utf-8-sig", dtype=str)
    df_b = pd.read_csv(FILE_B, encoding="utf-8-sig", dtype=str)
    df_a = df_a.fillna("")
    df_b = df_b.fillna("")
    print(f"  파일 A (공장DB): {len(df_a)}행, {len(df_a.columns)}컬럼")
    print(f"  파일 B (예비리스트): {len(df_b)}행, {len(df_b.columns)}컬럼")

    # ── 2. 정규화 ──
    print("\n[2/4] 회사명 정규화...")

    # 파일 A: 회사명
    df_a["_매칭키"] = df_a["회사명"].apply(normalize_company)
    a_valid = (df_a["_매칭키"] != "").sum()
    print(f"  파일 A 정규화: {a_valid}건 유효 / {len(df_a) - a_valid}건 빈칸")

    # 파일 B: 사업체명
    df_b["_매칭키"] = df_b["사업체명"].apply(normalize_company)
    b_valid = (df_b["_매칭키"] != "").sum()
    print(f"  파일 B 정규화: {b_valid}건 유효 / {len(df_b) - b_valid}건 빈칸")

    # 정규화 예시 출력
    print("\n  [정규화 예시 - 파일 B]")
    for _, row in df_b.head(5).iterrows():
        print(f"    {row['사업체명']} -> {row['_매칭키']}")

    # ── 3. 교차 매칭 ──
    print("\n[3/4] 교차 매칭...")

    # 파일 B의 매칭키 -> 행 정보 딕셔너리 (동일 매칭키를 가진 B 행이 여러 개일 수 있음)
    b_lookup = {}
    for idx, row in df_b.iterrows():
        key = row["_매칭키"]
        if key:
            if key not in b_lookup:
                b_lookup[key] = []
            b_lookup[key].append(row)

    # 파일 A에 추가할 컬럼 초기화
    df_a["중복_nid"] = ""
    for col in SOURCE_COLS:
        df_a[col + "_dup"] = ""

    # 매칭 수행
    match_count = 0
    matched_b_nids = set()

    for idx in df_a.index:
        key = df_a.at[idx, "_매칭키"]
        if key and key in b_lookup:
            b_rows = b_lookup[key]
            # 첫 번째 매칭된 B 행의 정보 사용 (복수 매칭 시 NID를 ;로 연결)
            nids = []
            source_vals = {col: [] for col in SOURCE_COLS}

            for b_row in b_rows:
                nid_val = str(b_row.get("NID", ""))
                nids.append(nid_val)
                matched_b_nids.add(nid_val)
                for col in SOURCE_COLS:
                    val = str(b_row.get(col, ""))
                    if val and val != "nan":
                        source_vals[col].append(val)

            df_a.at[idx, "중복_nid"] = "; ".join(nids)
            for col in SOURCE_COLS:
                vals = list(set(source_vals[col]))
                if vals:
                    df_a.at[idx, col + "_dup"] = "; ".join(vals)

            match_count += 1

    print(f"  매칭 완료: {match_count}건 (파일 A {len(df_a)}행 중)")
    print(f"  매칭된 파일 B 업체: {len(matched_b_nids)}개 (파일 B {len(df_b)}행 중)")

    # ── 4. 컬럼 정리 및 저장 ──
    print("\n[4/4] 결과 저장...")

    # _dup 접미사 제거하여 최종 컬럼명 설정
    rename_map = {col + "_dup": col for col in SOURCE_COLS}

    # 기존 SOURCE_COLS와 충돌 확인 (파일 A에 이미 있을 수 있음)
    existing_source_cols = [col for col in SOURCE_COLS if col in df_a.columns and col + "_dup" in df_a.columns]
    # 기존 컬럼이 있으면 삭제
    for col in existing_source_cols:
        # _dup가 아닌 원래 컬럼은 삭제하지 않음 (파일 A에는 원래 없음)
        pass

    df_a = df_a.rename(columns=rename_map)

    # nid 우측에 6개 컬럼 배치
    cols = list(df_a.columns)
    nid_idx = cols.index("nid")
    insert_cols = ["중복_nid"] + SOURCE_COLS

    # 삽입할 컬럼을 원래 위치에서 제거
    for c in insert_cols:
        if c in cols:
            cols.remove(c)

    # nid 바로 다음에 삽입
    for i, c in enumerate(insert_cols):
        cols.insert(nid_idx + 1 + i, c)

    # _매칭키 제거
    if "_매칭키" in cols:
        cols.remove("_매칭키")

    df_a = df_a[cols]

    # 저장 - 파일 A 결과
    output_file = os.path.join(
        BASE_DIR, "progress",
        f"company_electronics_iot_dup_checked_{TIMESTAMP}.csv"
    )
    df_a.to_csv(output_file, index=False, encoding="utf-8-sig")

    # ── 파일 B 매칭 결과 저장 ──
    # 파일 A의 매칭키 -> (nid, 회사명) 리스트 구축
    a_lookup = {}
    for idx in df_a.index:
        key = df_a.at[idx, "_매칭키"] if "_매칭키" in df_a.columns else ""
        if not key:
            # _매칭키가 이미 제거되었으므로 회사명에서 재생성
            key = normalize_company(df_a.at[idx, "회사명"])
        if key:
            if key not in a_lookup:
                a_lookup[key] = []
            a_lookup[key].append((df_a.at[idx, "nid"], df_a.at[idx, "회사명"]))

    df_b["매칭_공장DB_nid"] = ""
    df_b["매칭_공장DB_회사명"] = ""
    df_b["매칭_건수"] = 0

    for idx in df_b.index:
        key = df_b.at[idx, "_매칭키"]
        if key and key in a_lookup:
            matched_items = a_lookup[key]
            nids = [item[0] for item in matched_items]
            names = list(set(item[1] for item in matched_items))
            df_b.at[idx, "매칭_공장DB_nid"] = "; ".join(nids[:10])  # 최대 10개
            if len(nids) > 10:
                df_b.at[idx, "매칭_공장DB_nid"] += f" ... (+{len(nids)-10})"
            df_b.at[idx, "매칭_공장DB_회사명"] = "; ".join(names[:5])
            if len(names) > 5:
                df_b.at[idx, "매칭_공장DB_회사명"] += f" ... (+{len(names)-5})"
            df_b.at[idx, "매칭_건수"] = len(nids)

    # _매칭키 컬럼 제거
    df_b_out = df_b.drop(columns=["_매칭키"])

    output_file_b = os.path.join(
        BASE_DIR, "progress",
        f"preliminary_comany_list_dup_checked_{TIMESTAMP}.csv"
    )
    df_b_out.to_csv(output_file_b, index=False, encoding="utf-8-sig")

    b_matched = (df_b["매칭_건수"].astype(int) > 0).sum()
    print(f"  파일 B 매칭 결과: {b_matched}개 업체가 공장DB에 존재")

    # ── 통계 출력 ──
    print("\n" + "=" * 60)
    print("  교차 매칭 결과 요약")
    print("=" * 60)
    print(f"\n  [전체]")
    print(f"  파일 A 행 수: {len(df_a)}행 (보존 확인)")
    print(f"  중복 매칭: {match_count}건 ({match_count/len(df_a)*100:.2f}%)")
    print(f"  매칭된 B 업체: {len(matched_b_nids)}개 / {len(df_b)}개")

    # 출처별 통계
    print(f"\n  [출처별 매칭 건수 (파일 A 기준)]")
    for col in SOURCE_COLS:
        cnt = (df_a[col] != "").sum()
        print(f"    {col}: {cnt}건")

    # 매칭 예시 상위 10건
    matched = df_a[df_a["중복_nid"] != ""].head(10)
    print(f"\n  [매칭 예시 상위 10건]")
    print(f"  {'nid':<22} {'회사명':<20} {'중복_nid':<10}")
    print(f"  {'-'*22} {'-'*20} {'-'*10}")
    for _, row in matched.iterrows():
        print(f"  {row['nid']:<22} {row['회사명']:<20} {row['중복_nid']:<10}")

    print(f"\n  [산출 파일]")
    print(f"  A: {os.path.basename(output_file)}")
    print(f"  B: {os.path.basename(output_file_b)}")
    print("=" * 60)

    return df_a, df_b, match_count, len(matched_b_nids)


if __name__ == "__main__":
    main()
