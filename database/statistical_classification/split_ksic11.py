"""
KSIC11 (한국표준산업분류 11차) 분류별 CSV 분리 스크립트

대분류(KSIC1), 중분류(KSIC2), 소분류(KSIC3), 세분류(KSIC4), 세세분류(KSIC5)
각각을 별도 CSV 파일로 저장합니다.
"""

import csv
import os
from datetime import datetime
from typing import Dict, List, Tuple

# 상수 정의
INPUT_FILE: str = os.path.join(os.path.dirname(__file__), "KSIC11.csv")
OUTPUT_DIR: str = os.path.dirname(__file__)
HEADER_ROW_COUNT: int = 3  # 상단 헤더 3줄 스킵
TIMESTAMP: str = datetime.now().strftime("%Y%m%d_%H%M%S")

# 분류 레벨 정의: (레벨명, 코드컬럼인덱스, 명칭컬럼인덱스)
CLASSIFICATION_LEVELS: List[Tuple[str, int, int]] = [
    ("KSIC1", 0, 1),   # 대분류: 코드(col0), 항목명(col1)
    ("KSIC2", 2, 3),   # 중분류: 코드(col2), 항목명(col3)
    ("KSIC3", 4, 5),   # 소분류: 코드(col4), 항목명(col5)
    ("KSIC4", 6, 7),   # 세분류: 코드(col6), 항목명(col7)
    ("KSIC5", 8, 9),   # 세세분류: 코드(col8), 항목명(col9)
]


def read_ksic_data(filepath: str) -> List[List[str]]:
    """KSIC11 CSV 파일을 읽어 데이터 행만 반환합니다.

    Args:
        filepath: CSV 파일 경로

    Returns:
        헤더를 제외한 데이터 행 리스트
    """
    rows: List[List[str]] = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i < HEADER_ROW_COUNT:
                continue
            rows.append(row)
    return rows


def extract_classification(
    rows: List[List[str]],
    code_col: int,
    name_col: int,
) -> List[Tuple[str, str]]:
    """특정 분류 레벨의 고유 (코드, 항목명) 쌍을 추출합니다.

    Args:
        rows: 전체 데이터 행 리스트
        code_col: 코드 컬럼 인덱스
        name_col: 항목명 컬럼 인덱스

    Returns:
        중복 제거된 (코드, 항목명) 리스트 (등장 순서 유지)
    """
    seen: set = set()
    result: List[Tuple[str, str]] = []

    for row in rows:
        if len(row) <= max(code_col, name_col):
            continue

        code: str = row[code_col].strip()
        name: str = row[name_col].strip()

        if code and name and code not in seen:
            seen.add(code)
            result.append((code, name))

    return result


def save_classification_csv(
    data: List[Tuple[str, str]],
    level_name: str,
    output_dir: str,
) -> str:
    """분류 데이터를 CSV 파일로 저장합니다.

    Args:
        data: (코드, 항목명) 리스트
        level_name: 분류 레벨명 (예: KSIC1)
        output_dir: 출력 디렉토리

    Returns:
        저장된 파일 경로
    """
    filename: str = f"{level_name}_{TIMESTAMP}.csv"
    filepath: str = os.path.join(output_dir, filename)

    code_header: str = f"{level_name}_cd"
    name_header: str = f"{level_name}_name"

    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([code_header, name_header])
        for code, name in data:
            writer.writerow([code, name])

    return filepath


def main() -> None:
    """메인 실행 함수"""
    print(f"입력 파일: {INPUT_FILE}")
    rows = read_ksic_data(INPUT_FILE)
    print(f"총 데이터 행 수: {len(rows)}")

    for level_name, code_col, name_col in CLASSIFICATION_LEVELS:
        data = extract_classification(rows, code_col, name_col)
        filepath = save_classification_csv(data, level_name, OUTPUT_DIR)
        print(f"  {level_name}: {len(data)}건 -> {os.path.basename(filepath)}")

    print("완료!")


if __name__ == "__main__":
    main()
