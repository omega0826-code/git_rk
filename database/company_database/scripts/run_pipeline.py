# -*- coding: utf-8 -*-
"""
run_pipeline.py - 전국공장등록현황 데이터 정제 통합 파이프라인 (v1.6)
모든 정제 단계를 순차적으로 실행하고 결과를 저장합니다.

산출물:
  output/factory_on/{YYYYMM}/factory_cleaned_YYMMDD_HHMM.csv  - 정제 완료 데이터
  output/factory_on/{YYYYMM}/factory_deleted_YYMMDD_HHMM.csv  - 삭제 데이터
  logs/factory_on/{YYYYMM}/cleaning_log_YYMMDD_HHMM.md        - 정제 결과 리포트
"""

import os
import sys
import time
from datetime import datetime

import pandas as pd

# 스크립트 디렉토리를 path에 추가
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from importlib import import_module
add_nid_mod = import_module("01_add_nid")
clean_address_mod = import_module("02_clean_address")
clean_phone_mod = import_module("03_clean_phone")
clean_company_mod = import_module("04_clean_company_name")
clean_industry_mod = import_module("05_clean_industry")
split_deleted_mod = import_module("06_split_deleted")
quality_check_mod = import_module("07_quality_check")

# ──────────────────────────────────────────
# 경로 설정 (v1.3 디렉토리 구조)
# ──────────────────────────────────────────
BASE_DIR = os.path.dirname(SCRIPT_DIR)          # company_database/
DATA_PERIOD = "202601"                           # 기준월
RAW_DIR = os.path.join(BASE_DIR, "raw_data", "factory_on", DATA_PERIOD, "raw")
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "factory_on", DATA_PERIOD)
LOGS_DIR = os.path.join(BASE_DIR, "logs", "factory_on", DATA_PERIOD)

# 파일명 인수 받기 (기본값 설정)
target_filename = "(2026.01월말기준)_전국(개별,계획)입주업체현황.csv"
if len(sys.argv) > 1:
    target_filename = sys.argv[1]

RAW_FILE = os.path.join(RAW_DIR, target_filename)
FILE_PREFIX = "cleaned" if "공장" in target_filename or "National" in target_filename else ("company" if "입주" in target_filename else "data")

# 타임스탬프
TIMESTAMP = datetime.now().strftime("%y%m%d_%H%M")


def ensure_dirs():
    """출력 디렉토리 생성"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)


def load_data() -> pd.DataFrame:
    """원본 CSV 로딩"""
    print(f"[1/7] 원본 데이터 로딩: {RAW_FILE}")
    df = pd.read_csv(RAW_FILE, dtype=str, encoding="utf-8")
    print(f"       → {len(df)}행 × {len(df.columns)}컬럼 로딩 완료")
    return df


def step_nid(df: pd.DataFrame) -> tuple:
    """Step 1: nid 부여"""
    print(f"\n[2/7] nid 부여 (FC202601-NNNNNNNN)")
    df = add_nid_mod.add_nid(df)
    validation = add_nid_mod.validate_nid(df)
    print(f"       → nid 부여 완료: {validation['total']}건, 유일성: {'OK' if validation['valid'] else 'FAIL'}")
    return df, validation


def step_address(df: pd.DataFrame) -> tuple:
    """Step 2: 주소 정제"""
    print(f"\n[3/7] 주소 정제 (공장주소 + 공장주소_지번)")
    df, addr_stats = clean_address_mod.clean_addresses(df)
    print(f"       → 오타수정: {addr_stats['오타수정']}건")
    print(f"       → 약어확장: {addr_stats['약어확장']}건")
    print(f"       → 시도시군구분리: {addr_stats.get('시도시군구분리', 0)}건")
    print(f"       → 붙어쓰기보정: {addr_stats['붙어쓰기보정']}건")
    print(f"       → 붙어쓰기 토큰화: {addr_stats.get('붙어쓰기_토큰화', 0)}건")
    print(f"       → 공백정규화: {addr_stats['공백정규화']}건")
    print(f"       → 주소결함: {addr_stats['주소결함']}건")
    print(f"       → 읍면동 추출: {addr_stats['읍면동_추출']}건")
    print(f"       → 읍면동 미추출: {addr_stats['읍면동_미추출']}건")
    print(f"       → 시도명 정상: {addr_stats.get('시도명_정상', 0)}건")
    print(f"       → 시도명 미상: {addr_stats.get('시도명_미상', 0)}건")
    print(f"       → 시도 역매핑: {addr_stats.get('시도_역매핑', 0)}건")
    print(f"       → 구(기초) 추출: {addr_stats.get('구기초_추출', 0)}건")
    print(f"       → 시도/시군구 최종 미추출: {addr_stats.get('시도시군구_최종미추출', 0)}건")
    return df, addr_stats


def step_phone(df: pd.DataFrame) -> tuple:
    """Step 3: 전화번호 정제"""
    print(f"\n[4/7] 전화번호 정제")
    df, phone_stats = clean_phone_mod.clean_phone(df)
    print(f"       → 유효: {phone_stats['유효']}건")
    print(f"       → 포맷팅복원: {phone_stats['포맷팅_복원']}건")
    print(f"       → 빈칸: {phone_stats['빈칸']}건")
    print(f"       → 특수번호: {phone_stats['특수번호']}건")
    print(f"       → 무효: {phone_stats['무효']}건")
    return df, phone_stats


def step_company(df: pd.DataFrame) -> tuple:
    """Step 4: 기업명 정제"""
    print(f"\n[5/7] 기업명 정제")
    df, comp_stats = clean_company_mod.clean_company_names(df)
    print(f"       → 법인표기포함: {comp_stats['법인표기_포함']}건")
    print(f"       → 영문포함: {comp_stats['영문_포함']}건")
    print(f"       → 영문변환: {comp_stats['영문_변환']}건")
    print(f"       → 중복그룹: {comp_stats['중복_그룹']}건 ({comp_stats['중복_건수']}건)")
    print(f"       → 회사명결함: {comp_stats.get('회사명결함', 0)}건")
    return df, comp_stats


def step_industry(df: pd.DataFrame) -> tuple:
    """Step 5: 업종(KSIC) 정제"""
    print(f"\n[6/7] 업종(KSIC) 정제 및 분류 매핑")
    df, ind_stats = clean_industry_mod.clean_industry(df)
    print(f"       → 정상: {ind_stats['정상']}건")
    print(f"       → 차수 11: {ind_stats['차수_11']}건")
    print(f"       → 차수 10→변환: {ind_stats['차수_10_변환']}건")
    print(f"       → 차수 기타→11가정: {ind_stats['차수_기타_11가정']}건")
    print(f"       → 빈칸 결함: {ind_stats['빈칸_결함']}건")
    print(f"       → 무효코드 결함: {ind_stats['무효코드_결함']}건")
    print(f"       → 변환실패 결함: {ind_stats['변환실패_결함']}건")
    print(f"       → 분류매핑실패 결함: {ind_stats['분류매핑실패_결함']}건")
    return df, ind_stats


def step_split(df: pd.DataFrame) -> tuple:
    """Step 6: 삭제 데이터 분리"""
    print(f"\n[7/7] 삭제 데이터 분리")
    normal_df, deleted_df, split_stats = split_deleted_mod.split_deleted(df)
    print(f"       → 정상 데이터: {split_stats['정상']}건")
    print(f"       → 주소결함 삭제: {split_stats['주소결함_삭제']}건")
    print(f"       → 전화번호결함 삭제: {split_stats['전화번호결함_삭제']}건")
    print(f"       → 업종결함 삭제: {split_stats['업종결함_삭제']}건")
    print(f"       → 회사명결함 삭제: {split_stats.get('회사명결함_삭제', 0)}건")
    print(f"       → 복합결함 삭제: {split_stats['복합결함_삭제']}건")
    total_deleted = split_stats['주소결함_삭제'] + split_stats['전화번호결함_삭제'] + split_stats['업종결함_삭제'] + split_stats.get('회사명결함_삭제', 0) + split_stats['복합결함_삭제']
    print(f"       → 총 삭제: {total_deleted}건")
    return normal_df, deleted_df, split_stats


def reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    """컬럼 순서 재배치"""
    cols = list(df.columns)

    # 이동 대상 컬럼들을 먼저 제거
    move_cols = ["시도명", "시군구명", "구(기초)", "읍면동명",
                 "공장주소_클리닝", "공장주소_지번_클리닝",
                 "회사명_정규화", "회사명_영문", "회사명_비고",
                 "대표업종코드(대)", "대표업종명(대)", "대표업종코드(중)", "대표업종명(중)"]
    for mc in move_cols:
        if mc in cols:
            cols.remove(mc)

    # 1. 회사명 우측에 정규화/영문/비고 삽입
    if "회사명" in cols:
        idx = cols.index("회사명") + 1
        for c in ["회사명_정규화", "회사명_영문", "회사명_비고"]:
            if c in df.columns:
                cols.insert(idx, c)
                idx += 1

    # 2. 대표업종 좌측에 업종 대/중분류 4개 컬럼 삽입
    if "대표업종" in cols:
        idx = cols.index("대표업종")
        for c in ["대표업종코드(대)", "대표업종명(대)", "대표업종코드(중)", "대표업종명(중)"]:
            if c in df.columns:
                cols.insert(idx, c)
                idx += 1

    # 3. 공장주소 좌측에 시도명/시군구명/구(기초)/읍면동명 삽입 (v1.5)
    if "공장주소" in cols:
        idx = cols.index("공장주소")
        for c in ["시도명", "시군구명", "구(기초)", "읍면동명"]:
            if c in df.columns:
                cols.insert(idx, c)
                idx += 1

    # 4. 공장주소 우측에 공장주소_클리닝 삽입
    if "공장주소" in cols:
        idx = cols.index("공장주소") + 1
        if "공장주소_클리닝" in df.columns:
            cols.insert(idx, "공장주소_클리닝")

    # 5. 공장주소_지번 우측에 공장주소_지번_클리닝 삽입
    if "공장주소_지번" in cols:
        idx = cols.index("공장주소_지번") + 1
        if "공장주소_지번_클리닝" in df.columns:
            cols.insert(idx, "공장주소_지번_클리닝")

    return df[cols]


def save_results(normal_df: pd.DataFrame, deleted_df: pd.DataFrame):
    """정제 결과 CSV 저장"""
    # 컬럼 재배치
    normal_df = reorder_columns(normal_df)
    deleted_df = reorder_columns(deleted_df)

    prefix_name = "factory" if FILE_PREFIX == "cleaned" else "company"
    cleaned_path = os.path.join(OUTPUT_DIR, f"{prefix_name}_cleaned_{TIMESTAMP}.csv")
    deleted_path = os.path.join(OUTPUT_DIR, f"{prefix_name}_deleted_{TIMESTAMP}.csv")

    normal_df.to_csv(cleaned_path, index=False, encoding="utf-8-sig")
    deleted_df.to_csv(deleted_path, index=False, encoding="utf-8-sig")

    print(f"\n=== 파일 저장 완료 ===")
    print(f"  정제 데이터: {cleaned_path} ({len(normal_df)}행)")
    print(f"  삭제 데이터: {deleted_path} ({len(deleted_df)}행)")

    return cleaned_path, deleted_path


def generate_report(
    raw_df: pd.DataFrame,
    normal_df: pd.DataFrame,
    deleted_df: pd.DataFrame,
    total_rows: int,
    nid_validation: dict,
    addr_stats: dict,
    phone_stats: dict,
    comp_stats: dict,
    ind_stats: dict,
    split_stats: dict,
    cleaned_path: str,
    deleted_path: str,
    elapsed: float,
    sec_quality: str = "",
) -> str:
    """통합 정제 결과 리포트 생성 (v1.6)"""
    prefix_name = "factory" if FILE_PREFIX == "cleaned" else "company"
    report_path = os.path.join(LOGS_DIR, f"{prefix_name}_cleaning_log_{TIMESTAMP}.md")

    raw_n = total_rows
    cln_n = len(normal_df)
    del_n = len(deleted_df)
    total_deleted = split_stats['주소결함_삭제'] + split_stats['전화번호결함_삭제'] + split_stats.get('업종결함_삭제', 0) + split_stats.get('회사명결함_삭제', 0) + split_stats['복합결함_삭제']

    def pct(n: int, total: int = 0) -> str:
        if total == 0:
            total = raw_n
        if total == 0:
            return "0.0%"
        return f"{n/total*100:.1f}%"

    # === 1. 종합 요약 ===
    sec1 = f"""## 1. 종합 요약

### 1.1 데이터 개요

| 구분 | 건수 | 비중 |
| :--- | ---: | ---: |
| 전체 원본 (모집단) | {raw_n:,} | 100% |
| 정제 데이터 (Cleaned) | {cln_n:,} | {pct(cln_n)} |
| 삭제 데이터 (Deleted) | {del_n:,} | {pct(del_n)} |

### 1.2 삭제 사유별 분류

| 삭제 사유 | 건수 | 비중 |
| :--- | ---: | ---: |
| 주소결함 | {split_stats['주소결함_삭제']:,} | {pct(split_stats['주소결함_삭제'])} |
| 전화번호결함 | {split_stats['전화번호결함_삭제']:,} | {pct(split_stats['전화번호결함_삭제'])} |
| 업종결함 | {split_stats.get('업종결함_삭제', 0):,} | {pct(split_stats.get('업종결함_삭제', 0))} |
| 회사명결함 | {split_stats.get('회사명결함_삭제', 0):,} | {pct(split_stats.get('회사명결함_삭제', 0))} |
| 복합결함 (2개 이상) | {split_stats['복합결함_삭제']:,} | {pct(split_stats['복합결함_삭제'])} |
| **합계** | **{total_deleted:,}** | **{pct(total_deleted)}** |"""

    # === 2.1 nid ===
    sec_nid = f"""### 2.1 고유식별자(nid) 부여

| 항목 | 값 |
| :--- | :--- |
| 형식 | `FC202601-NNNNNNNN` |
| 총 부여 | {nid_validation['total']:,} |
| 유일성 검증 | OK |"""

    # === 2.2 주소 정제 ===
    addr_fix_total = addr_stats['오타수정'] + addr_stats['약어확장'] + addr_stats.get('시도시군구분리', 0) + addr_stats['붙어쓰기보정'] + addr_stats.get('붙어쓰기_토큰화', 0) + addr_stats['공백정규화']
    raw_addr_miss = int(raw_df['공장주소'].isna().sum()) + int((raw_df['공장주소'].fillna('').str.strip() == '').sum()) if '공장주소' in raw_df.columns else 0
    cln_addr_miss = int(normal_df['공장주소_클리닝'].isna().sum()) + int((normal_df['공장주소_클리닝'].fillna('').str.strip() == '').sum()) if '공장주소_클리닝' in normal_df.columns else 0
    del_addr_miss = int(deleted_df['공장주소_클리닝'].isna().sum()) + int((deleted_df['공장주소_클리닝'].fillna('').str.strip() == '').sum()) if '공장주소_클리닝' in deleted_df.columns else 0
    cln_emd = int((normal_df['읍면동명'].fillna('').str.strip() != '').sum()) if '읍면동명' in normal_df.columns else 0
    del_emd = int((deleted_df['읍면동명'].fillna('').str.strip() != '').sum()) if '읍면동명' in deleted_df.columns else 0

    sec_addr = f"""### 2.2 주소 정제

#### 정제 항목별 통계

| 정제 유형 | 건수 | 비중 |
| :--- | ---: | ---: |
| 시도 오타 수정 | {addr_stats['오타수정']:,} | {pct(addr_stats['오타수정'])} |
| 시도 약어 확장 | {addr_stats['약어확장']:,} | {pct(addr_stats['약어확장'])} |
| 시도-시군구 분리 | {addr_stats.get('시도시군구분리', 0):,} | {pct(addr_stats.get('시도시군구분리', 0))} |
| 붙어쓰기 보정 | {addr_stats['붙어쓰기보정']:,} | {pct(addr_stats['붙어쓰기보정'])} |
| 붙어쓰기 토큰화 | {addr_stats.get('붙어쓰기_토큰화', 0):,} | {pct(addr_stats.get('붙어쓰기_토큰화', 0))} |
| 공백 정규화 | {addr_stats['공백정규화']:,} | {pct(addr_stats['공백정규화'])} |
| **수정 합계** | **{addr_fix_total:,}** | **{pct(addr_fix_total)}** |
| 주소결함 | {addr_stats['주소결함']:,} | {pct(addr_stats['주소결함'])} |
| 읍면동 추출 | {addr_stats['읍면동_추출']:,} | {pct(addr_stats['읍면동_추출'])} |
| 읍면동 미추출 | {addr_stats['읍면동_미추출']:,} | {pct(addr_stats['읍면동_미추출'])} |
| 시도명 정상 | {addr_stats.get('시도명_정상', 0):,} | {pct(addr_stats.get('시도명_정상', 0))} |
| 시도명 미상 | {addr_stats.get('시도명_미상', 0):,} | {pct(addr_stats.get('시도명_미상', 0))} |
| 시도 역매핑 | {addr_stats.get('시도_역매핑', 0):,} | {pct(addr_stats.get('시도_역매핑', 0))} |
| 구(기초) 추출 | {addr_stats.get('구기초_추출', 0):,} | {pct(addr_stats.get('구기초_추출', 0))} |

#### 모집단 vs 정제 vs 삭제 비교

| 구분 | 모집단 (Raw) | 정제 (Cleaned) | 삭제 (Deleted) |
| :--- | ---: | ---: | ---: |
| 주소 결측치 | {raw_addr_miss:,}건 ({pct(raw_addr_miss)}) | {cln_addr_miss:,}건 | {del_addr_miss:,}건 |
| 텍스트 보정 | {addr_fix_total:,}건 ({pct(addr_fix_total)}) | {addr_fix_total:,}건 보정 | - |
| 읍면동 추출 | - | {cln_emd:,}건 ({pct(cln_emd)}) | {del_emd:,}건 ({pct(del_emd)}) |
| 읍면동 미추출 | - | {cln_n - cln_emd:,}건 | {del_n - del_emd:,}건 |

#### 파생 컬럼
- `공장주소_클리닝` / `공장주소_지번_클리닝`: 정제된 주소
- `시도명` / `시군구명` / `구(기초)` / `읍면동명`: 주소 기반 행정구역 추출"""

    # === 2.3 전화번호 정제 ===
    raw_phone_miss = int(raw_df['전화번호'].isna().sum()) + int((raw_df['전화번호'].fillna('').str.strip() == '').sum()) if '전화번호' in raw_df.columns else 0
    phone_defect = phone_stats['빈칸'] + phone_stats['특수번호'] + phone_stats['무효']

    sec_phone = f"""### 2.3 전화번호 정제

#### 정제 항목별 통계

| 유형 | 건수 | 비중 |
| :--- | ---: | ---: |
| 유효 (통과) | {phone_stats['유효']:,} | {pct(phone_stats['유효'])} |
| 포맷팅 복원 | {phone_stats['포맷팅_복원']:,} | {pct(phone_stats['포맷팅_복원'])} |
| 빈칸 (삭제) | {phone_stats['빈칸']:,} | {pct(phone_stats['빈칸'])} |
| 특수번호 (삭제) | {phone_stats['특수번호']:,} | {pct(phone_stats['특수번호'])} |
| 무효 (삭제) | {phone_stats['무효']:,} | {pct(phone_stats['무효'])} |
| **결함 소계** | **{phone_defect:,}** | **{pct(phone_defect)}** |

#### 모집단 vs 정제 vs 삭제 비교

| 구분 | 모집단 (Raw) | 정제 (Cleaned) | 삭제 (Deleted) |
| :--- | ---: | ---: | ---: |
| 유효 전화번호 | {phone_stats['유효']:,}건 ({pct(phone_stats['유효'])}) | {phone_stats['유효']:,}건 (100%) | 0건 |
| 결측치(빈칸) | {raw_phone_miss:,}건 ({pct(raw_phone_miss)}) | 0건 | {phone_stats['빈칸']:,}건 |
| 특수번호 | {phone_stats['특수번호']:,}건 ({pct(phone_stats['특수번호'])}) | 0건 | {phone_stats['특수번호']:,}건 |
| 무효 번호 | {phone_stats['무효']:,}건 ({pct(phone_stats['무효'])}) | 0건 | {phone_stats['무효']:,}건 |"""

    # === 2.4 기업명 정제 ===
    raw_uc = raw_df['회사명'].nunique() if '회사명' in raw_df.columns else 0
    cln_uc = normal_df['회사명'].nunique() if '회사명' in normal_df.columns else 0
    del_uc = deleted_df['회사명'].nunique() if '회사명' in deleted_df.columns else 0
    cln_un = normal_df['회사명_정규화'].nunique() if '회사명_정규화' in normal_df.columns else 0
    del_un = deleted_df['회사명_정규화'].nunique() if '회사명_정규화' in deleted_df.columns else 0
    cln_corp = int(normal_df['회사명'].fillna('').str.contains(r'\(주\)|주식회사|\(유\)|\(사\)', regex=True).sum()) if '회사명' in normal_df.columns else 0
    del_corp = int(deleted_df['회사명'].fillna('').str.contains(r'\(주\)|주식회사|\(유\)|\(사\)', regex=True).sum()) if '회사명' in deleted_df.columns else 0
    cln_eng = int(normal_df['회사명'].fillna('').str.contains(r'[a-zA-Z]', regex=True).sum()) if '회사명' in normal_df.columns else 0
    del_eng = int(deleted_df['회사명'].fillna('').str.contains(r'[a-zA-Z]', regex=True).sum()) if '회사명' in deleted_df.columns else 0
    cln_dup = int(normal_df['회사명_비고'].fillna('').str.contains(r'\[중복\]', regex=True).sum()) if '회사명_비고' in normal_df.columns else 0
    del_dup = int(deleted_df['회사명_비고'].fillna('').str.contains(r'\[중복\]', regex=True).sum()) if '회사명_비고' in deleted_df.columns else 0

    sec_comp = f"""### 2.4 기업명 정제

#### 정제 항목별 통계

| 유형 | 건수 | 비중 |
| :--- | ---: | ---: |
| 법인 표기 포함 | {comp_stats['법인표기_포함']:,} | {pct(comp_stats['법인표기_포함'])} |
| 영문 포함 | {comp_stats['영문_포함']:,} | {pct(comp_stats['영문_포함'])} |
| 영문 변환 | {comp_stats['영문_변환']:,} | {pct(comp_stats['영문_변환'])} |
| 중복 그룹 | {comp_stats['중복_그룹']:,} | {pct(comp_stats['중복_그룹'])} |
| 중복 건수 | {comp_stats['중복_건수']:,} | {pct(comp_stats['중복_건수'])} |

#### 모집단 vs 정제 vs 삭제 비교

| 구분 | 모집단 (Raw) | 정제 (Cleaned) | 삭제 (Deleted) |
| :--- | ---: | ---: | ---: |
| 고유 회사명(원본) | {raw_uc:,}건 | {cln_uc:,}건 ({pct(cln_uc, raw_uc)}) | {del_uc:,}건 ({pct(del_uc, raw_uc)}) |
| 고유 회사명(정규화) | - | {cln_un:,}건 | {del_un:,}건 |
| 법인 표기 | {comp_stats['법인표기_포함']:,}건 | {cln_corp:,}건 | {del_corp:,}건 |
| 영문 포함 | {comp_stats['영문_포함']:,}건 | {cln_eng:,}건 | {del_eng:,}건 |
| 중복 태그 | {comp_stats['중복_건수']:,}건 | {cln_dup:,}건 | {del_dup:,}건 |

#### 파생 컬럼
- `회사명_정규화`: 법인표기/괄호 제거, 영문 외래어 변환
- `회사명_영문`: 정규화 결과의 전체 영문 표현
- `회사명_비고`: `[중복]`, `[영문포함]` 등 태그"""

    # === 2.5 업종(KSIC) 정제 ===
    raw_ui = raw_df['대표업종'].nunique() if '대표업종' in raw_df.columns else 0
    cln_ui = normal_df['대표업종'].nunique() if '대표업종' in normal_df.columns else 0
    del_ui = deleted_df['대표업종'].nunique() if '대표업종' in deleted_df.columns else 0
    ind_defect = ind_stats['빈칸_결함'] + ind_stats['무효코드_결함'] + ind_stats['변환실패_결함'] + ind_stats['분류매핑실패_결함']

    sec_ind = f"""### 2.5 업종(KSIC) 정제

#### 정제 항목별 통계

| 유형 | 건수 | 비중 |
| :--- | ---: | ---: |
| 정상 매핑 | {ind_stats['정상']:,} | {pct(ind_stats['정상'])} |
| 차수 11 (그대로) | {ind_stats['차수_11']:,} | {pct(ind_stats['차수_11'])} |
| 차수 10->11 변환 | {ind_stats['차수_10_변환']:,} | {pct(ind_stats['차수_10_변환'])} |
| 차수 기타->11 가정 | {ind_stats['차수_기타_11가정']:,} | {pct(ind_stats['차수_기타_11가정'])} |
| 빈칸 결함 | {ind_stats['빈칸_결함']:,} | {pct(ind_stats['빈칸_결함'])} |
| 무효코드 결함 | {ind_stats['무효코드_결함']:,} | {pct(ind_stats['무효코드_결함'])} |
| 변환실패 결함 | {ind_stats['변환실패_결함']:,} | {pct(ind_stats['변환실패_결함'])} |
| 매핑실패 결함 | {ind_stats['분류매핑실패_결함']:,} | {pct(ind_stats['분류매핑실패_결함'])} |
| **결함 소계** | **{ind_defect:,}** | **{pct(ind_defect)}** |

#### 모집단 vs 정제 vs 삭제 비교

| 구분 | 모집단 (Raw) | 정제 (Cleaned) | 삭제 (Deleted) |
| :--- | ---: | ---: | ---: |
| 정상 매핑 | {ind_stats['정상']:,}건 ({pct(ind_stats['정상'])}) | {ind_stats['정상']:,}건 | 0건 |
| 고유 업종코드 | {raw_ui:,}종 | {cln_ui:,}종 | {del_ui:,}종 |
| 결함 소계 | {ind_defect:,}건 ({pct(ind_defect)}) | 0건 | {ind_defect:,}건 |

#### 파생 컬럼
- `대표업종코드(대)` / `대표업종명(대)`: KSIC 대분류
- `대표업종코드(중)` / `대표업종명(중)`: KSIC 중분류"""

    # === 3.1 시도별 분포 ===
    sido_col = '시도명'
    sec_sido_lines = []
    if sido_col in normal_df.columns and sido_col in deleted_df.columns:
        cln_sido = normal_df[sido_col].fillna('').value_counts()
        del_sido = deleted_df[sido_col].fillna('').value_counts()
        all_sido = sorted(set(cln_sido.index) | set(del_sido.index))

        # 표 A: 전체 모집단 기준
        sec_sido_lines.append("### 3.1 시도별 분포")
        sec_sido_lines.append("")
        sec_sido_lines.append("#### (A) 전체 모집단 기준")
        sec_sido_lines.append("")
        sec_sido_lines.append(f"> 전체 모집단: **{raw_n:,}건** (정제: {cln_n:,}건 / 삭제: {del_n:,}건)")
        sec_sido_lines.append("")
        sec_sido_lines.append("| 시도명 | 정제 | 정제비중 | 삭제 | 삭제비중 | 합계 | 전체비중 |")
        sec_sido_lines.append("| :--- | ---: | ---: | ---: | ---: | ---: | ---: |")
        for sido in all_sido:
            label = sido if sido else "(미상)"
            c = int(cln_sido.get(sido, 0))
            d = int(del_sido.get(sido, 0))
            t = c + d
            sec_sido_lines.append(f"| {label} | {c:,} | {pct(c)} | {d:,} | {pct(d)} | {t:,} | {pct(t)} |")
        sec_sido_lines.append(f"| **합계** | **{cln_n:,}** | **{pct(cln_n)}** | **{del_n:,}** | **{pct(del_n)}** | **{raw_n:,}** | **100%** |")

        # 표 B: 정제 기업수 기준 비중
        sec_sido_lines.append("")
        sec_sido_lines.append("#### (B) 정제 기업수 기준 비중")
        sec_sido_lines.append("")
        sec_sido_lines.append(f"> 정제 데이터: **{cln_n:,}건** 기준")
        sec_sido_lines.append("")
        sec_sido_lines.append("| 시도명 | 정제 기업수 | 비중 |")
        sec_sido_lines.append("| :--- | ---: | ---: |")
        cln_sido_sorted = cln_sido.sort_values(ascending=False)
        for sido in cln_sido_sorted.index:
            label = sido if sido else "(미상)"
            c = int(cln_sido_sorted[sido])
            sec_sido_lines.append(f"| {label} | {c:,} | {pct(c, cln_n)} |")
        sec_sido_lines.append(f"| **합계** | **{cln_n:,}** | **100%** |")
    sec_sido = "\n".join(sec_sido_lines)

    # === 3.2 KSIC 중분류별 ===
    ksic_name_col = '대표업종명(중)'
    ksic_code_col = '대표업종코드(중)'
    sec_ksic_lines = []
    if ksic_name_col in normal_df.columns and ksic_name_col in deleted_df.columns:
        def _lbl(row):
            code = str(row.get(ksic_code_col, '')).strip() if pd.notna(row.get(ksic_code_col)) else ''
            name = str(row.get(ksic_name_col, '')).strip() if pd.notna(row.get(ksic_name_col)) else ''
            if code and name:
                return f"{code} ({name})"
            elif name:
                return name
            return '(미매핑)'
        def _code_key(row):
            code = str(row.get(ksic_code_col, '')).strip() if pd.notna(row.get(ksic_code_col)) else ''
            return code
        cln_labels = normal_df.apply(_lbl, axis=1)
        del_labels = deleted_df.apply(_lbl, axis=1)
        cln_codes = normal_df.apply(_code_key, axis=1)
        del_codes = deleted_df.apply(_code_key, axis=1)
        cln_ksic = cln_labels.value_counts()
        del_ksic = del_labels.value_counts()
        merged = {}
        for k in set(cln_ksic.index) | set(del_ksic.index):
            c = int(cln_ksic.get(k, 0))
            d = int(del_ksic.get(k, 0))
            merged[k] = (c, d, c + d)
        # 코드순 정렬: 레이블에서 코드 부분 추출
        def _sort_key(item):
            label = item[0]
            if label.startswith('('):
                return 'ZZZ'
            code_part = label.split(' ')[0] if ' ' in label else label
            return code_part.zfill(5)
        sorted_ksic = sorted(merged.items(), key=_sort_key)

        # 표 A: 전체 모집단 기준 (전체 업종, 코드순)
        sec_ksic_lines.append("### 3.2 KSIC 중분류별 분포")
        sec_ksic_lines.append("")
        sec_ksic_lines.append("#### (A) 전체 모집단 기준")
        sec_ksic_lines.append("")
        sec_ksic_lines.append(f"> 전체 모집단: **{raw_n:,}건** (정제: {cln_n:,}건 / 삭제: {del_n:,}건)")
        sec_ksic_lines.append("")
        sec_ksic_lines.append("| KSIC 중분류 | 정제 | 정제비중 | 삭제 | 삭제비중 | 합계 | 전체비중 |")
        sec_ksic_lines.append("| :--- | ---: | ---: | ---: | ---: | ---: | ---: |")
        for k, (c, d, t) in sorted_ksic:
            sec_ksic_lines.append(f"| {k} | {c:,} | {pct(c)} | {d:,} | {pct(d)} | {t:,} | {pct(t)} |")
        sec_ksic_lines.append(f"| **합계** | **{cln_n:,}** | **{pct(cln_n)}** | **{del_n:,}** | **{pct(del_n)}** | **{raw_n:,}** | **100%** |")

        # 표 B: 정제 기업수 기준 비중 (전체 업종, 코드순)
        sec_ksic_lines.append("")
        sec_ksic_lines.append("#### (B) 정제 기업수 기준 비중")
        sec_ksic_lines.append("")
        sec_ksic_lines.append(f"> 정제 데이터: **{cln_n:,}건** 기준")
        sec_ksic_lines.append("")
        sec_ksic_lines.append("| KSIC 중분류 | 정제 기업수 | 비중 |")
        sec_ksic_lines.append("| :--- | ---: | ---: |")
        cln_only = {k: v[0] for k, v in merged.items() if v[0] > 0}
        sorted_cln_only = sorted(cln_only.items(), key=lambda x: _sort_key(x))
        for k, c in sorted_cln_only:
            sec_ksic_lines.append(f"| {k} | {c:,} | {pct(c, cln_n)} |")
        sec_ksic_lines.append(f"| **합계** | **{cln_n:,}** | **100%** |")
    sec_ksic = "\n".join(sec_ksic_lines)

    # === 4. 산출물 ===
    sec_output = f"""## 4. 산출물

| 파일 | 경로 |
| :--- | :--- |
| 정제 데이터 | `{os.path.basename(cleaned_path)}` |
| 삭제 데이터 | `{os.path.basename(deleted_path)}` |
| 리포트 | `{os.path.basename(report_path)}` |"""

    # === 전체 조립 ===
    report = f"""# 데이터 정제 결과 리포트

> **원본 파일**: `{target_filename}`
> **정제일시**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> **버전**: v1.6
> **소요 시간**: {elapsed:.1f}초

---

**목차**
1. [종합 요약](#1-종합-요약) - 데이터 개요, 삭제 사유별 분류
2. [정제 단계별 상세](#2-정제-단계별-상세) - nid, 주소, 전화번호, 기업명, 업종
3. [분포 분석](#3-분포-분석) - 시도별, KSIC 중분류별
4. [산출물](#4-산출물)

---

{sec1}

---

## 2. 정제 단계별 상세

> 전체 모집단 **{raw_n:,}건** 기준. 각 단계별 정제 항목 통계와 모집단/정제/삭제 비교표를 함께 제공합니다.

{sec_nid}

---

{sec_addr}

---

{sec_phone}

---

{sec_comp}

---

{sec_ind}

---

## 3. 분포 분석

{sec_sido}

{sec_ksic}

---

{sec_output}

---

{sec_quality}
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"  리포트: {report_path}")
    return report_path


def main():
    """메인 파이프라인 실행 (v1.6)"""
    start_time = time.time()

    print("=" * 60)
    print("  데이터 정제 파이프라인 (v1.6)")
    print(f"  타임스탬프: {TIMESTAMP}")
    print("=" * 60)

    ensure_dirs()

    # 1. 로딩
    df = load_data()
    total_rows = len(df)
    raw_df = df.copy()  # 원본 보관 (비교 통계용)

    # 2. nid 부여
    df, nid_validation = step_nid(df)

    # 3. 주소 정제
    df, addr_stats = step_address(df)

    # 4. 전화번호 정제
    df, phone_stats = step_phone(df)

    # 5. 기업명 정제
    df, comp_stats = step_company(df)

    # 6. 업종(KSIC) 정제
    df, ind_stats = step_industry(df)

    # 7. 삭제 데이터 분리
    normal_df, deleted_df, split_stats = step_split(df)

    # 8. 저장
    cleaned_path, deleted_path = save_results(normal_df, deleted_df)

    # 9. 리포트 생성
    print(f"\n[통계] 통합 리포트 생성 중...")

    # 9-1. 품질 분석 (v1.6)
    print(f"  품질 분석 중...")
    quality_stats = quality_check_mod.check_quality(normal_df)
    sec_quality = quality_check_mod.generate_quality_section(quality_stats, len(normal_df))
    print(f"       → 시도명 빈칸: {quality_stats['address_quality'].get('sido_empty', 0)}건")
    print(f"       → 시군구 공백 잔존: {quality_stats['address_quality'].get('sigungu_space_residual', 0)}건")

    elapsed = time.time() - start_time
    report_path = generate_report(
        raw_df, normal_df, deleted_df,
        total_rows, nid_validation, addr_stats, phone_stats,
        comp_stats, ind_stats, split_stats, cleaned_path, deleted_path,
        elapsed, sec_quality
    )

    # 검증
    print(f"\n=== 검증 ===")
    print(f"  원본: {total_rows}행")
    print(f"  정상+삭제: {len(normal_df) + len(deleted_df)}행")
    assert len(normal_df) + len(deleted_df) == total_rows, "행 수 불일치!"
    print(f"  [OK] 행 수 보존 검증 통과")

    elapsed = time.time() - start_time
    print(f"\n=== 완료 (소요시간: {elapsed:.1f}초) ===")


if __name__ == "__main__":
    main()
