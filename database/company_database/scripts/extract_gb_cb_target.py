# -*- coding: utf-8 -*-
"""
extract_gb_cb_target.py
경북/충북 타겟 기업 리스트 추출 스크립트

필터 조건:
  1. 업종: KSIC 중분류 10, 11, 24, 26, 29, 42, 56
  2. 종사자수: 10인 ~ 299인
  3. 지역: 경북 북부권/서부권, 충북 북부권 (11개 시군구)
"""
import sys
import io
import os
import csv
from datetime import datetime

# UTF-8 출력 래퍼
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ==========================================
# 1. CONFIG
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

CONFIG = {
    "BASE_DATA_PATH": os.path.join(BASE_DIR, "output", "factory_on", "202601",
                                    "company_cleaned_260305_1400.csv"),
    "TARGET_KSIC_CODES": {"10", "11", "24", "26", "29", "42", "56"},
    "MIN_EMPLOYEES": 10,
    "MAX_EMPLOYEES": 299,
    "TARGET_REGIONS": {
        "gyeongbuk_north": {
            "label": "gyeongbuk_bukbu",
            "label_kr": "경북 북부권",
            "sido": "경상북도",
            "sigungu": ["안동시", "영주시", "상주시", "예천군", "의성군"],
        },
        "gyeongbuk_west": {
            "label": "gyeongbuk_seobu",
            "label_kr": "경북 서부권",
            "sido": "경상북도",
            "sigungu": ["구미시", "김천시"],
        },
        "chungbuk_north": {
            "label": "chungbuk_bukbu",
            "label_kr": "충북 북부권",
            "sido": "충청북도",
            "sigungu": ["제천시", "충주시", "단양군", "괴산군"],
        },
    },
    "OUTPUT_DIR": os.path.join(BASE_DIR, "output", "target_extraction"),
}

TIMESTAMP = datetime.now().strftime("%y%m%d_%H%M")

# KSIC 중분류 코드-이름 매핑
KSIC_MID_NAMES = {
    "10": "식료품 제조업",
    "11": "음료 제조업",
    "24": "1차 금속 제조업",
    "26": "전자부품/컴퓨터/통신장비 제조업",
    "29": "기타 기계 및 장비 제조업",
    "42": "전문직별 공사업",
    "56": "음식점 및 주점업",
}


def build_region_lookup():
    """(sido, sigungu) -> 권역명 매핑 딕셔너리 생성"""
    lookup = {}
    for key, info in CONFIG["TARGET_REGIONS"].items():
        for sg in info["sigungu"]:
            lookup[(info["sido"], sg)] = info["label_kr"]
    return lookup


def parse_employees(val):
    """종업원합계 문자열을 int로 변환, 실패시 None"""
    if val is None:
        return None
    val = str(val).strip()
    if val == "" or val.lower() == "nan":
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def main():
    print("=" * 60)
    print("  gyeongbuk/chungbuk Target Company Extraction")
    print(f"  Timestamp: {TIMESTAMP}")
    print("=" * 60)

    # 출력 디렉토리 생성
    os.makedirs(CONFIG["OUTPUT_DIR"], exist_ok=True)

    region_lookup = build_region_lookup()
    target_ksic = CONFIG["TARGET_KSIC_CODES"]
    min_emp = CONFIG["MIN_EMPLOYEES"]
    max_emp = CONFIG["MAX_EMPLOYEES"]

    # 컬럼 인덱스 (나중에 헤더에서 찾기)
    col_idx = {}
    required_cols = [
        "nid", "대표업종코드(중)", "대표업종명(중)", "종업원합계",
        "시도명", "시군구명"
    ]

    # 통계 변수
    total_rows = 0
    pass_ksic = 0
    pass_emp = 0
    pass_region = 0

    # 지역별, 업종별 카운트
    region_counts = {}
    industry_counts = {}
    cross_counts = {}  # (region, ksic_code) -> count

    results = []
    header_out = None

    print("\n[1/4] Loading and filtering data...")
    src_path = CONFIG["BASE_DATA_PATH"]

    with open(src_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)

        # 헤더에서 인덱스 찾기
        for col_name in required_cols:
            if col_name in header:
                col_idx[col_name] = header.index(col_name)
            else:
                print(f"  [WARN] Column '{col_name}' not found!")
                return

        # 출력 헤더: 원본 + 권역명
        header_out = header + ["권역명"]

        for row in reader:
            total_rows += 1

            # Filter A: KSIC 중분류
            ksic_code = row[col_idx["대표업종코드(중)"]].strip()
            if ksic_code not in target_ksic:
                continue
            pass_ksic += 1

            # Filter B: 종사자수
            emp = parse_employees(row[col_idx["종업원합계"]])
            if emp is None or emp < min_emp or emp > max_emp:
                continue
            pass_emp += 1

            # Filter C: 지역
            sido = row[col_idx["시도명"]].strip()
            sigungu = row[col_idx["시군구명"]].strip()
            region_name = region_lookup.get((sido, sigungu))
            if region_name is None:
                continue
            pass_region += 1

            # 통계 집계
            region_key = f"{sido} {sigungu}"
            region_counts[region_key] = region_counts.get(region_key, 0) + 1
            industry_counts[ksic_code] = industry_counts.get(ksic_code, 0) + 1
            cross_key = (region_key, ksic_code)
            cross_counts[cross_key] = cross_counts.get(cross_key, 0) + 1

            results.append(row + [region_name])

    print(f"  Total rows scanned: {total_rows:,}")
    print(f"  Pass KSIC filter : {pass_ksic:,}")
    print(f"  Pass Employee filter: {pass_emp:,}")
    print(f"  Pass Region filter : {pass_region:,} (FINAL)")

    # --- 결과 저장 ---
    print(f"\n[2/4] Saving results...")

    out_base = f"gb_cb_target_{TIMESTAMP}"
    result_path = os.path.join(CONFIG["OUTPUT_DIR"], f"{out_base}.csv")
    pivot_region_path = os.path.join(CONFIG["OUTPUT_DIR"], f"{out_base}_pivot_region.csv")
    pivot_industry_path = os.path.join(CONFIG["OUTPUT_DIR"], f"{out_base}_pivot_industry.csv")
    log_path = os.path.join(CONFIG["OUTPUT_DIR"], f"{out_base}_log.md")

    # 메인 결과 CSV
    with open(result_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header_out)
        writer.writerows(results)
    print(f"  Result: {result_path} ({len(results):,} rows)")

    # --- 피벗 테이블 생성 ---
    print(f"\n[3/4] Generating pivot tables...")

    # 모든 지역, 업종 키
    all_regions = sorted(region_counts.keys())
    all_industries = sorted(industry_counts.keys())

    # 피벗 1: 지역(행) x 업종(열)
    with open(pivot_region_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        ind_headers = [f"{k} ({KSIC_MID_NAMES.get(k, '')})" for k in all_industries]
        writer.writerow(["지역(시도 시군구)"] + ind_headers + ["합계"])
        for reg in all_regions:
            row_vals = [cross_counts.get((reg, ind), 0) for ind in all_industries]
            writer.writerow([reg] + row_vals + [sum(row_vals)])
        # 합계 행
        totals = [sum(cross_counts.get((reg, ind), 0) for reg in all_regions) for ind in all_industries]
        writer.writerow(["합계"] + totals + [sum(totals)])
    print(f"  Pivot (region x industry): {pivot_region_path}")

    # 피벗 2: 업종(행) x 지역(열)
    with open(pivot_industry_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["업종코드(명)"] + all_regions + ["합계"])
        for ind in all_industries:
            label = f"{ind} ({KSIC_MID_NAMES.get(ind, '')})"
            row_vals = [cross_counts.get((reg, ind), 0) for reg in all_regions]
            writer.writerow([label] + row_vals + [sum(row_vals)])
        totals = [sum(cross_counts.get((reg, ind), 0) for ind in all_industries) for reg in all_regions]
        writer.writerow(["합계"] + totals + [sum(totals)])
    print(f"  Pivot (industry x region): {pivot_industry_path}")

    # --- 로그/리포트 생성 ---
    print(f"\n[4/4] Generating report...")

    # 피벗 마크다운 생성 (지역 x 업종)
    ind_headers_md = [f"{k} ({KSIC_MID_NAMES.get(k, '')})" for k in all_industries]
    pivot_md_lines = []
    pivot_md_lines.append("| 지역 | " + " | ".join(ind_headers_md) + " | 합계 |")
    pivot_md_lines.append("|" + "------|" * (len(ind_headers_md) + 2))
    for reg in all_regions:
        vals = [str(cross_counts.get((reg, ind), 0)) for ind in all_industries]
        total = sum(cross_counts.get((reg, ind), 0) for ind in all_industries)
        pivot_md_lines.append(f"| {reg} | " + " | ".join(vals) + f" | {total} |")
    total_vals = [str(sum(cross_counts.get((reg, ind), 0) for reg in all_regions)) for ind in all_industries]
    pivot_md_lines.append(f"| **합계** | " + " | ".join(total_vals) + f" | **{len(results)}** |")
    pivot_md = "\n".join(pivot_md_lines)

    # 권역별 소계
    region_group_counts = {}
    for key, info in CONFIG["TARGET_REGIONS"].items():
        label = info["label_kr"]
        cnt = sum(region_counts.get(f"{info['sido']} {sg}", 0) for sg in info["sigungu"])
        region_group_counts[label] = cnt

    region_group_md = "\n".join(
        f"| {label} | {cnt:,} |"
        for label, cnt in region_group_counts.items()
    )

    # 업종별 요약
    industry_md_lines = []
    for ind in sorted(industry_counts.keys()):
        cnt = industry_counts[ind]
        name = KSIC_MID_NAMES.get(ind, "")
        industry_md_lines.append(f"| {ind} | {name} | {cnt:,} |")
    industry_md = "\n".join(industry_md_lines)

    log_content = f"""# 경북/충북 타겟 기업 리스트 추출 결과 리포트

> **추출일시**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> **원본 데이터**: `company_cleaned_260305_1400.csv`
> **추출 조건**: KSIC 중분류 (10,11,24,26,29,42,56) + 종사자수 10~299인 + 경북/충북 11개 시군구

---

## 1. 추출 결과 요약

| 항목 | 건수 | 비율 |
|------|------|------|
| 전체 원본 | {total_rows:,} | 100% |
| 1차 업종 필터 통과 | {pass_ksic:,} | {pass_ksic/total_rows*100:.1f}% |
| 2차 종사자수 필터 통과 | {pass_emp:,} | {pass_emp/total_rows*100:.1f}% |
| **3차 지역 필터 통과 (최종)** | **{pass_region:,}** | **{pass_region/total_rows*100:.2f}%** |

---

## 2. 권역별 분포

| 권역 | 건수 |
|------|------|
{region_group_md}
| **합계** | **{len(results):,}** |

---

## 3. 업종별 분포

| KSIC 코드 | 업종명 | 건수 |
|-----------|--------|------|
{industry_md}

---

## 4. 교차 통계 (지역 x 업종)

{pivot_md}

---

## 5. 산출물

| 파일 | 설명 |
|------|------|
| `{out_base}.csv` | 타겟 기업 리스트 ({len(results):,}건) |
| `{out_base}_pivot_region.csv` | 교차 통계: 지역(행) x 업종(열) |
| `{out_base}_pivot_industry.csv` | 교차 통계: 업종(행) x 지역(열) |
| `{out_base}_log.md` | 본 리포트 |

---

## 6. 검증

| 항목 | 결과 |
|------|------|
| nid 유일성 | 확인 필요 |
| 업종 코드 범위 | 모두 TARGET_KSIC_CODES 내 |
| 종사자수 범위 | 모두 10~299인 |
| 지역 유효성 | 모두 TARGET_REGIONS 내 |
"""

    with open(log_path, "w", encoding="utf-8") as f:
        f.write(log_content)
    print(f"  Report: {log_path}")

    # --- 검증 ---
    print(f"\n=== Verification ===")
    nids = [r[col_idx["nid"]] for r in results]
    unique_nids = len(set(nids))
    nid_ok = unique_nids == len(nids)
    print(f"  nid uniqueness: {'[OK]' if nid_ok else '[FAIL]'} ({unique_nids}/{len(nids)})")

    print(f"\n=== Done (Total: {len(results):,} companies extracted) ===")


if __name__ == "__main__":
    main()
