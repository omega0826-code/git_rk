# -*- coding: utf-8 -*-
"""
01_add_nid.py - nid(고유넘버) 부여 모듈
전국공장등록현황 데이터에 고유 식별번호를 부여합니다.
형식: FC202601-NNNNNNNN (접두어 + 년월 + 8자리 일련번호)
"""

import pandas as pd

NID_PREFIX = "FC202601"
NID_DIGITS = 8


def add_nid(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame 첫 번째 컬럼으로 nid를 삽입합니다."""
    nids = [f"{NID_PREFIX}-{str(i).zfill(NID_DIGITS)}" for i in range(1, len(df) + 1)]
    df.insert(0, "nid", nids)
    return df


def validate_nid(df: pd.DataFrame) -> dict:
    """nid 유일성 검증"""
    total = len(df)
    unique = df["nid"].nunique()
    return {
        "total": total,
        "unique": unique,
        "valid": total == unique,
    }


if __name__ == "__main__":
    # 단독 실행 테스트
    test_df = pd.DataFrame({"A": range(10)})
    result = add_nid(test_df)
    print(result.head())
    print(validate_nid(result))
