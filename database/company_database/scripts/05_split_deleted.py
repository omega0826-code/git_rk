# -*- coding: utf-8 -*-
"""
05_split_deleted.py - 삭제 데이터 분리 모듈
주소/전화번호 결함 데이터를 별도 CSV로 분리합니다.
삭제 기준: 1개라도 결함이면 삭제 데이터로 이동
"""

import pandas as pd


def split_deleted(df: pd.DataFrame) -> tuple:
    """
    결함 태그 기반으로 삭제 데이터와 정상 데이터를 분리합니다.
    Returns: (정상_df, 삭제_df, 통계_dict)
    """
    stats = {
        "총_건수": len(df),
        "주소결함_삭제": 0,
        "전화번호결함_삭제": 0,
        "복합결함_삭제": 0,
        "정상": 0,
    }

    delete_reasons = []

    for idx in df.index:
        addr_tag = str(df.at[idx, "_주소태그"]) if pd.notna(df.at[idx, "_주소태그"]) else ""
        phone_tag = str(df.at[idx, "_전화태그"]) if pd.notna(df.at[idx, "_전화태그"]) else ""

        reasons = []
        if addr_tag and "[삭제:" in addr_tag:
            reasons.append(addr_tag)
        if phone_tag and "[삭제:" in phone_tag:
            reasons.append(phone_tag)

        if reasons:
            if len(reasons) == 2:
                stats["복합결함_삭제"] += 1
            elif "주소결함" in reasons[0]:
                stats["주소결함_삭제"] += 1
            else:
                stats["전화번호결함_삭제"] += 1
            delete_reasons.append("; ".join(reasons))
        else:
            stats["정상"] += 1
            delete_reasons.append("")

    df["삭제사유"] = delete_reasons

    # 분리
    mask_deleted = df["삭제사유"] != ""
    deleted_df = df[mask_deleted].copy()
    normal_df = df[~mask_deleted].copy()

    # 내부 태그 컬럼 제거 (최종 출력용)
    internal_cols = ["_주소태그", "_전화태그"]
    for col in internal_cols:
        if col in normal_df.columns:
            normal_df = normal_df.drop(columns=[col])
        if col in deleted_df.columns:
            deleted_df = deleted_df.drop(columns=[col])

    # 정상 데이터에서 삭제사유 컬럼 제거
    if "삭제사유" in normal_df.columns:
        normal_df = normal_df.drop(columns=["삭제사유"])

    return normal_df, deleted_df, stats


if __name__ == "__main__":
    test_data = {
        "nid": ["FC202601-00000001", "FC202601-00000002", "FC202601-00000003"],
        "회사명": ["정상기업", "주소결함기업", "전화결함기업"],
        "_주소태그": ["", "[삭제:주소결함] 빈칸", ""],
        "_전화태그": ["", "", "[삭제:전화번호결함] 빈칸"],
    }
    test_df = pd.DataFrame(test_data)
    normal, deleted, stats = split_deleted(test_df)
    print(f"정상: {len(normal)}건")
    print(f"삭제: {len(deleted)}건")
    print(f"통계: {stats}")
    if len(deleted) > 0:
        print(f"\n삭제 데이터:")
        print(deleted[["nid", "회사명", "삭제사유"]].to_string())
