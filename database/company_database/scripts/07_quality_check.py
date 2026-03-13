# -*- coding: utf-8 -*-
"""
07_quality_check.py - 정제 후 데이터 품질 분석 모듈 (v1.6)
정제 완료된 DataFrame의 컬럼별 결측값, 고유값, 주소 품질,
숫자 컬럼 이상치 등을 분석합니다.
"""

import pandas as pd


def check_quality(df: pd.DataFrame) -> dict:
    """
    정제 데이터의 컬럼별 품질을 분석합니다.

    Args:
        df: 정제 완료 DataFrame

    Returns:
        품질 분석 결과 dict
    """
    total = len(df)

    # ── 1. 컬럼별 결측/고유값 ──
    columns_info = {}
    for col in df.columns:
        nan_cnt = int(df[col].isna().sum())
        empty_cnt = int((df[col].fillna("").str.strip() == "").sum())
        missing_total = empty_cnt  # 빈문자열은 NaN을 포함
        unique_cnt = int(df[col].dropna().nunique())
        pct = f"{missing_total / total * 100:.1f}%" if total > 0 else "0.0%"
        columns_info[col] = {
            "nan_count": nan_cnt,
            "empty_count": empty_cnt,
            "missing_total": missing_total,
            "missing_pct": pct,
            "unique_count": unique_cnt,
        }

    # ── 2. 주소 품질 ──
    address_quality = {}
    addr_cols = {"시도명": "sido_empty", "시군구명": "sigungu_empty",
                 "구(기초)": "gu_empty", "읍면동명": "emd_empty"}
    for col, key in addr_cols.items():
        if col in df.columns:
            empty = int((df[col].fillna("").str.strip() == "").sum())
            address_quality[key] = empty
        else:
            address_quality[key] = -1  # 컬럼 없음

    # 시군구명에 공백 포함 (시+구 합산 잔존)
    sigungu_space = 0
    if "시군구명" in df.columns:
        sigungu_space = int(df["시군구명"].fillna("").str.contains(" ", na=False).sum())
    address_quality["sigungu_space_residual"] = sigungu_space

    # 구(기초) 채워진 건수
    if "구(기초)" in df.columns:
        address_quality["gu_filled"] = int((df["구(기초)"].fillna("").str.strip() != "").sum())

    # ── 3. 숫자 컬럼 이상치 ──
    numeric_cols = ["남자종업원", "여자종업원", "외국인남자종업원", "외국인여자종업원",
                    "종업원합계", "용지면적", "제조시설면적", "부대시설면적", "건축면적"]
    numeric_issues = []
    for col in numeric_cols:
        if col in df.columns:
            non_empty = df[col].dropna().loc[lambda x: x.str.strip() != ""]
            bad_mask = pd.to_numeric(non_empty, errors="coerce").isna()
            bad_cnt = int(bad_mask.sum())
            samples = non_empty[bad_mask].head(3).tolist() if bad_cnt > 0 else []
            numeric_issues.append({
                "col": col,
                "bad_count": bad_cnt,
                "samples": samples,
            })

    return {
        "total_rows": total,
        "total_columns": len(df.columns),
        "columns": columns_info,
        "address_quality": address_quality,
        "numeric_issues": numeric_issues,
    }


def generate_quality_section(quality_stats: dict, total_rows: int) -> str:
    """품질 분석 결과를 마크다운 리포트 섹션으로 변환합니다."""

    def pct(n, t=0):
        if t == 0:
            t = total_rows
        if t == 0:
            return "0.0%"
        return f"{n/t*100:.1f}%"

    lines = []
    lines.append("## 5. 데이터 품질 분석")
    lines.append("")
    lines.append(f"> 정제 데이터 **{total_rows:,}건** × **{quality_stats['total_columns']}컬럼** 기준")
    lines.append("")

    # 5.1 컬럼별 결측값
    lines.append("### 5.1 컬럼별 결측값 현황")
    lines.append("")
    lines.append("| 컬럼 | 결측(NaN) | 빈문자열 | 결측합계 | 비중 | 고유값 |")
    lines.append("| :--- | ---: | ---: | ---: | ---: | ---: |")

    for col, info in quality_stats["columns"].items():
        lines.append(
            f"| {col} | {info['nan_count']:,} | {info['empty_count']:,} | "
            f"{info['missing_total']:,} | {info['missing_pct']} | {info['unique_count']:,} |"
        )

    # 5.2 주소 품질
    aq = quality_stats["address_quality"]
    lines.append("")
    lines.append("### 5.2 주소 품질 요약")
    lines.append("")
    lines.append("| 항목 | 건수 | 비중 |")
    lines.append("| :--- | ---: | ---: |")

    addr_items = [
        ("시도명 빈칸", aq.get("sido_empty", 0)),
        ("시군구명 빈칸", aq.get("sigungu_empty", 0)),
        ("읍면동명 빈칸", aq.get("emd_empty", 0)),
        ("구(기초) 채워진 건", aq.get("gu_filled", 0)),
        ("시군구 공백 잔존(시+구 합산)", aq.get("sigungu_space_residual", 0)),
    ]
    for label, cnt in addr_items:
        if cnt >= 0:
            lines.append(f"| {label} | {cnt:,} | {pct(cnt)} |")

    # 5.3 숫자 컬럼
    issues = quality_stats["numeric_issues"]
    if issues:
        lines.append("")
        lines.append("### 5.3 숫자 컬럼 이상치")
        lines.append("")
        has_issues = any(i["bad_count"] > 0 for i in issues)
        if has_issues:
            lines.append("| 컬럼 | 비숫자 건수 | 샘플 |")
            lines.append("| :--- | ---: | :--- |")
            for item in issues:
                if item["bad_count"] > 0:
                    samples_str = ", ".join(str(s) for s in item["samples"])
                    lines.append(f"| {item['col']} | {item['bad_count']:,} | {samples_str} |")
        else:
            lines.append("> 모든 숫자 컬럼 정상 (비숫자 값 0건)")

    return "\n".join(lines)


if __name__ == "__main__":
    # 테스트
    test_data = {
        "nid": ["FC202601-00000001", "FC202601-00000002", "FC202601-00000003"],
        "회사명": ["정상기업", "테스트", ""],
        "시도명": ["경기도", "서울특별시", ""],
        "시군구명": ["수원시", "강남구", ""],
        "구(기초)": ["장안구", "", ""],
        "읍면동명": ["이목동", "역삼동", ""],
        "종업원합계": ["10", "abc", "5"],
    }
    test_df = pd.DataFrame(test_data)
    result = check_quality(test_df)

    print(f"총 행: {result['total_rows']}")
    print(f"\n컬럼별 결측:")
    for col, info in result["columns"].items():
        print(f"  {col}: 결측 {info['missing_total']}건 ({info['missing_pct']}), 고유값 {info['unique_count']}")

    print(f"\n주소 품질: {result['address_quality']}")
    print(f"\n숫자 이상치: {result['numeric_issues']}")

    print("\n" + "=" * 60)
    section = generate_quality_section(result, result["total_rows"])
    print(section)
