# -*- coding: utf-8 -*-
"""
전국공장등록현황 엑셀(xlsx) → CSV 변환 스크립트

Description:
    - 원본 xlsx 파일을 UTF-8 BOM CSV로 변환합니다.

Usage:
    python convert_xlsx_to_csv.py
    python convert_xlsx_to_csv.py --raw-dir /path/to/raw

Author: Data Analyst
Created: 2026-03-01
Updated: 2026-03-02
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd

# ============================================================
# 상수 정의
# ============================================================
BASE_DIR: Path = Path(__file__).resolve().parent.parent
RAW_DIR: Path = BASE_DIR / "202601" / "raw"
DEFAULT_ENCODING: str = "utf-8-sig"

# 변환 대상 파일 목록 (xlsx basename → csv basename)
TARGET_FILES: dict[str, str] = {
    "(2026.01월말기준)_전국공장등록현황.xlsx":
        "(2026.01월말기준)_전국공장등록현황.csv",
    "(2026.01월말기준)_전국(개별,계획)입주업체현황.xlsx":
        "(2026.01월말기준)_전국(개별,계획)입주업체현황.csv",
}


# ============================================================
# 핵심 함수
# ============================================================
def convert_xlsx_to_csv(
    xlsx_path: Path,
    csv_path: Path,
    encoding: str = DEFAULT_ENCODING,
) -> int:
    """엑셀 파일을 CSV로 변환합니다.

    Args:
        xlsx_path: 원본 xlsx 파일 경로
        csv_path: 저장할 csv 파일 경로
        encoding: 출력 인코딩 (기본: utf-8-sig)

    Returns:
        변환된 행 수
    """
    print(f"  [읽기] {xlsx_path.name} ...")
    df = pd.read_excel(xlsx_path, engine="openpyxl")
    df.to_csv(csv_path, index=False, encoding=encoding)
    print(f"  [저장] {csv_path.name} (행: {len(df):,}, 열: {len(df.columns)})")
    return len(df)



def main() -> None:
    """메인 실행 함수."""
    parser = argparse.ArgumentParser(
        description="전국공장등록현황 XLSX → CSV 변환 스크립트"
    )
    parser.add_argument(
        "--raw-dir", type=str, default=None,
        help="원본 파일 디렉토리 (기본: 스크립트 기준 상대경로)"
    )
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir) if args.raw_dir else RAW_DIR

    print("=" * 60)
    print(f"  전국공장등록현황 XLSX → CSV 변환")
    print(f"  실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  원본 경로: {raw_dir}")
    print("=" * 60)

    if not raw_dir.exists():
        print(f"[오류] 디렉토리가 존재하지 않습니다: {raw_dir}")
        sys.exit(1)

    # 1) XLSX → CSV 변환
    converted_files: list[Path] = []
    for xlsx_name, csv_name in TARGET_FILES.items():
        xlsx_path = raw_dir / xlsx_name
        csv_path = raw_dir / csv_name

        if not xlsx_path.exists():
            print(f"\n[건너뜀] 파일 없음: {xlsx_name}")
            continue

        print(f"\n--- {xlsx_name} ---")
        convert_xlsx_to_csv(xlsx_path, csv_path)
    print(f"\n{'=' * 60}")
    print(f"  모든 작업 완료!")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
