import pandas as pd
import os
import math
from datetime import datetime

# ==========================================
# 1. 설정 (Configuration)
# ==========================================
NOW_STR = datetime.now().strftime('%y%m%d_%H%M')
DATE_YMD = datetime.now().strftime('%y%m%d')

CONFIG = {
    # 정제된 대상 기업 데이터
    "BASE_DATA_PATH": r"d:\git_rk\database\company_database\output\factory_on\202601\company_cleaned_260305_1400.csv",
    
    # 파주 산업단지 입주업종 정의 파일
    "KSIC_FILTER_PATH": r"d:\git_rk\database\project\Paju_Industrial_Complex_Demand_Survey\Industries_Located_in_Paju_General_Industrial_Complex.csv",
    
    # 수도권 과밀억제권역 정의 파일
    "ZONE_FILTER_PATH": r"d:\git_rk\database\company_database\reference\law\Metropolitan Area Overcrowding Control Zone_260305_0909.csv",
    
    # 최종 추출결과 저장 경로
    "OUTPUT_PATH": rf"d:\git_rk\database\company_database\output\target_extraction\paju_overcrowding_zone_{NOW_STR}.csv",
    
    # 로그 파일 경로
    "LOG_PATH": rf"d:\git_rk\database\company_database\logs\target_extraction\extraction_log_{NOW_STR}.md"
}

def create_dirs():
    os.makedirs(os.path.dirname(CONFIG["OUTPUT_PATH"]), exist_ok=True)
    os.makedirs(os.path.dirname(CONFIG["LOG_PATH"]), exist_ok=True)

def extract_target_companies():
    create_dirs()
    
    print("1. 데이터를 로딩합니다...")
    df_base = pd.read_csv(CONFIG["BASE_DATA_PATH"], dtype={'대표업종코드(중)': str})
    raw_count = len(df_base)
    
    df_ksic = pd.read_csv(CONFIG["KSIC_FILTER_PATH"], dtype={'KSIC2_CD': str})
    valid_ksic_codes = df_ksic['KSIC2_CD'].dropna().str.strip().tolist()
    
    df_zone = pd.read_csv(CONFIG["ZONE_FILTER_PATH"])
    
    print("2. 파주 산단 타겟 업종(KSIC) 필터링 진행 중...")
    df_base['업종코드_매핑용'] = df_base['대표업종코드(중)'].str.strip()
    df_filtered = df_base[df_base['업종코드_매핑용'].isin(valid_ksic_codes)].copy()
    ksic_count = len(df_filtered)
    print(f"  → 업종 필터 통과: {ksic_count:,}건")
    
    print("3. 수도권 과밀억제권역 필터링 진행 중...")
    zone_records = df_zone.to_dict('records')
    
    def is_in_overcrowding_zone(row):
        sido = str(row.get('시도명', '')).strip()
        sigungu = str(row.get('시군구명', '')).strip()
        dong = str(row.get('읍면동명', '')).strip()
        
        for z in zone_records:
            z_sido = str(z.get('시도', '')).strip()
            
            z_sigungu_val = z.get('시군구')
            if isinstance(z_sigungu_val, float) and math.isnan(z_sigungu_val):
                z_sigungu = ""
            else:
                z_sigungu = str(z_sigungu_val).strip() if pd.notna(z_sigungu_val) else ""
            
            z_dong_val = z.get('읍면동')
            if isinstance(z_dong_val, float) and math.isnan(z_dong_val):
                z_dong = ""
            else:
                z_dong = str(z_dong_val).strip() if pd.notna(z_dong_val) else ""
            
            if sido == z_sido:
                if not z_sigungu: return True
                
                if sigungu == z_sigungu or z_sigungu in sigungu:
                    if not z_dong: 
                        return True
                    else:
                        if dong == z_dong:
                            return True
        return False

    df_filtered['과밀억제권역_여부'] = df_filtered.apply(is_in_overcrowding_zone, axis=1)
    df_final = df_filtered[df_filtered['과밀억제권역_여부'] == True].copy()
    
    df_final.drop(columns=['업종코드_매핑용', '과밀억제권역_여부'], inplace=True, errors='ignore')
    final_count = len(df_final)
    print(f"  → 과밀억제권역 필터 통과: {final_count:,}건")
    
    # 4. 피벗 테이블 (교차 통계) 생성
    # KSIC 업종코드에 업종명 결합 ("코드 (이름)" 형태)
    df_ksic['KSIC_LABEL'] = df_ksic['KSIC2_CD'].astype(str).str.strip() + " (" + df_ksic['KSIC2_NAME'].astype(str).str.strip().str.replace(r'\r|\n', '', regex=True) + ")"
    ksic_mapping = dict(zip(df_ksic['KSIC2_CD'].str.strip(), df_ksic['KSIC_LABEL']))
    
    col_col = '대표업종코드(중)' if '대표업종코드(중)' in df_final.columns else '대표업종(중)'
    df_final['업종_컬럼명_매핑'] = df_final[col_col].map(ksic_mapping).fillna(df_final[col_col])
    
    # 지역(행: 시도+시군구)
    df_final['지역_행'] = df_final['시도명'].astype(str) + " " + df_final['시군구명'].astype(str)
    
    # 피벗 1: 지역 (행) x 업종 (열)
    pivot_df_region_row = pd.crosstab(df_final['지역_행'], df_final['업종_컬럼명_매핑'], margins=True, margins_name='총계')
    pivot_df_region_row.index.name = '지역(시도 시군구)'
    pivot_df_region_row.columns.name = '업종코드(명)'
    pivot_md_region_row = pivot_df_region_row.to_markdown()

    # 피벗 2: 업종 (행) x 지역 (열)
    pivot_df_industry_row = pd.crosstab(df_final['업종_컬럼명_매핑'], df_final['지역_행'], margins=True, margins_name='총계')
    pivot_df_industry_row.index.name = '업종코드(명)'
    pivot_df_industry_row.columns.name = '지역(시도 시군구)'
    pivot_md_industry_row = pivot_df_industry_row.to_markdown()

    # 결과물 경로 정의
    pivot_region_csv_path = CONFIG["OUTPUT_PATH"].replace('.csv', '_pivot_region.csv')
    pivot_industry_csv_path = CONFIG["OUTPUT_PATH"].replace('.csv', '_pivot_industry.csv')

    # 5. 결과 및 로그 저장
    df_final.drop(columns=['업종_컬럼명_매핑', '지역_행'], inplace=True, errors='ignore')
    df_final.to_csv(CONFIG["OUTPUT_PATH"], index=False, encoding='utf-8-sig')
    print(f"4. 최종 타겟 업체 {final_count:,}건 저장 완료: {CONFIG['OUTPUT_PATH']}")
    
    pivot_df_region_row.to_csv(pivot_region_csv_path, encoding='utf-8-sig')
    pivot_df_industry_row.to_csv(pivot_industry_csv_path, encoding='utf-8-sig')
    print(f"   (교차 통계 피벗 CSV 파일 2종 생성: {os.path.basename(pivot_region_csv_path)}, {os.path.basename(pivot_industry_csv_path)})")

    log_content = f"""# 타겟 업체 추출 로그

> **실행 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> **추출 기준**: 수도권 과밀억제권역 지역 & 파주 산업단지 입주 가능 업종 (KSIC 2자리)

## 1. 입력 데이터 및 매핑 컬럼
* **베이스 데이터 (정제본)**: `{os.path.basename(CONFIG["BASE_DATA_PATH"])}`
  - *사용 컬럼*: `대표업종코드(중)`, `시도명`, `시군구명`, `읍면동명`
* **업종 필터 (파주 산단 지정 업종)**: `{os.path.basename(CONFIG["KSIC_FILTER_PATH"])}`
  - *사용 컬럼*: `KSIC2_CD` (베이스 데이터의 `대표업종코드(중)`와 매칭)
* **지역 필터 (수도권 과밀억제권역)**: `{os.path.basename(CONFIG["ZONE_FILTER_PATH"])}`
  - *사용 컬럼*: `시도`, `시군구`, `읍면동` (해당 지역 범위 내 포함 여부 판단)


## 2. 추출 통계
| 단계 | 기준 | 통과 건수 | 보존율 (vs 모집단) |
| :--- | :--- | ---: | ---: |
| **0. 모집단** | 정제 완료 데이터 전체 | {raw_count:,}건 | 100% |
| **1. 업종 필터** | 파주 산단 입주업종 코드 매칭 | {ksic_count:,}건 | {ksic_count/raw_count*100:.1f}% |
| **2. 지역 필터** | 수도권 과밀억제권역 매칭 | **{final_count:,}건** | **{final_count/raw_count*100:.1f}%** |

## 3. 타겟 업체 교차 분포

### 3.1 지역(행) x 업종(열) 통계
{pivot_md_region_row}

### 3.2 업종(행) x 지역(열) 통계
{pivot_md_industry_row}

## 4. 산출물 파일
* **최종 타겟 데이터**: `{CONFIG["OUTPUT_PATH"]}`
* **지역시군구 행 교차 통계 CSV**: `{pivot_region_csv_path}`
* **대표업종코드 행 교차 통계 CSV**: `{pivot_industry_csv_path}`
"""
    
    with open(CONFIG["LOG_PATH"], 'w', encoding='utf-8') as f:
        f.write(log_content)
    print(f"5. 추출 기록 로그 및 지역 분포 통계 저장 완료: {CONFIG['LOG_PATH']}")

if __name__ == "__main__":
    extract_target_companies()
