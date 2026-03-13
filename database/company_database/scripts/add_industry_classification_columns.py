import sys, io
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""
전자산업 / 가전 IoT 업종 분류 컬럼 추가 스크립트

- 입력: company_cleaned_260307_1754F.csv
- 분류기준 파일: (classification)electronic_.csv, (classification)home_appliance_IoT.csv
- 처리:
  - 업종코드_전체 컬럼의 코드 중 전자산업 분류 코드와 하나라도 일치 → 전자산업 = 'O'
  - 업종코드_전체 컬럼의 코드 중 가전IoT 분류 코드와 하나라도 일치 → IoT = 'O'
  - 두 컬럼은 '대표업종' 컬럼 좌측에 삽입
- 출력: company_cleaned_260307_1754F_classified.csv
"""

import pandas as pd
import re

# ── 경로 설정 ──────────────────────────────────────────────────────────────
BASE_DIR = r"d:\git_rk\database"
MAIN_FILE = BASE_DIR + r"\company_database\output\factory_on\202601\company_cleaned_260307_1754F.csv"
ELECTRONIC_FILE = (
    BASE_DIR
    + r"\project\Survey_on_the_Supply_and_Demand_of_Personnel"
    r"\industry_classification\(classification)electronic_.csv"
)
IOT_FILE = (
    BASE_DIR
    + r"\project\Survey_on_the_Supply_and_Demand_of_Personnel"
    r"\industry_classification\(classification)home_appliance_IoT_industry.csv"
)
OUTPUT_FILE = BASE_DIR + r"\company_database\output\factory_on\202601\company_cleaned_260307_1754F_classified.csv"


def load_code_set(filepath: str) -> set:
    """분류 CSV에서 업종코드 집합을 반환 (문자열 5자리)."""
    df = pd.read_csv(filepath, dtype=str, encoding="utf-8")
    codes = set(df["KSIC5_code"].str.strip())
    return codes


def parse_codes(code_str: str) -> set:
    """
    '업종코드_전체' 컬럼 값에서 개별 5자리 코드를 추출.
    예) '26410' → {'26410'}
        '"26410, 26421"' → {'26410', '26421'}
    """
    if pd.isna(code_str) or not str(code_str).strip():
        return set()
    # 따옴표·공백 제거 후 숫자 코드만 추출
    codes = re.findall(r"\d{5}", str(code_str))
    return set(codes)


def classify_row(code_str: str, ref_set: set) -> str:
    row_codes = parse_codes(code_str)
    return "O" if row_codes & ref_set else ""


def main():
    print("분류 코드 로드 중...")
    electronic_codes = load_code_set(ELECTRONIC_FILE)
    iot_codes = load_code_set(IOT_FILE)
    print(f"  전자산업 코드 수: {len(electronic_codes)}")
    print(f"  가전 IoT 코드 수: {len(iot_codes)}")

    print("메인 파일 로드 중 (약 22만 행)...")
    df = pd.read_csv(MAIN_FILE, dtype=str, encoding="utf-8")
    print(f"  총 행 수: {len(df):,}")

    # 업종코드_전체 컬럼 기반으로 분류
    print("분류 컬럼 생성 중...")
    df["전자산업"] = df["업종코드_전체"].apply(lambda x: classify_row(x, electronic_codes))
    df["IoT"] = df["업종코드_전체"].apply(lambda x: classify_row(x, iot_codes))

    # '대표업종' 컬럼 좌측(앞)에 삽입
    target_col = "대표업종"
    if target_col not in df.columns:
        raise ValueError(f"'{target_col}' 컬럼이 존재하지 않습니다. 컬럼 목록: {list(df.columns)}")

    insert_pos = df.columns.get_loc(target_col)

    # 새 컬럼 제거 후 원하는 위치에 재삽입
    electronic_vals = df.pop("전자산업")
    iot_vals = df.pop("IoT")
    df.insert(insert_pos, "전자산업", electronic_vals)
    df.insert(insert_pos + 1, "IoT", iot_vals)

    print(f"저장 중: {OUTPUT_FILE}")
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    # 통계 출력
    elec_cnt = (df["전자산업"] == "O").sum()
    iot_cnt = (df["IoT"] == "O").sum()
    print(f"\n[완료] 결과 저장: {OUTPUT_FILE}")
    print(f"  전자산업 O 표시 건수: {elec_cnt:,}")
    print(f"  가전 IoT O 표시 건수: {iot_cnt:,}")


if __name__ == "__main__":
    main()
