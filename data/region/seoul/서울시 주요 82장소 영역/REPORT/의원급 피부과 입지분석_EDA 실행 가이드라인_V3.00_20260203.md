# 의원급 피부과 입지 분석을 위한 EDA 실행 가이드라인

**작성일**: 2026-02-03  
**버전**: 3.00 (스토리텔링 개선 및 산출물 구조화)  
**데이터 기준**: 강남구 주요 82장소 상권 데이터 (2022년 1분기 ~ 2024년 4분기)  
**분석 목적**: 의원급 피부과 최적 입지 선정을 위한 탐색적 데이터 분석

---

## 목차

1. [데이터 개요](#1-데이터-개요)
2. [산출물 디렉토리 구조](#2-산출물-디렉토리-구조)
3. [분석 스토리라인](#3-분석-스토리라인)
4. [단계별 EDA 실행](#4-단계별-eda-실행)
5. [추가 심화 분석](#5-추가-심화-분석)
6. [결과 리포트 작성](#6-결과-리포트-작성)
7. [참고 자료](#7-참고-자료)

---

## 1. 데이터 개요

### 1.1 사용 가능한 데이터셋

강남구 5개 주요 상권(양재역, 가로수길, 강남역, 역삼역, 선릉역)에 대한 9개 CSV 파일:

| 파일명 | 주요 내용 | 활용도 |
|--------|----------|--------|
| `영역-상권.csv` | 상권 기본정보 (좌표, 면적, 행정구역) | ★★★ |
| `점포-상권.csv` | 업종별 점포 수, 개폐업률 (분기별) | ★★★★★ |
| `추정매출-상권.csv` | 업종별 매출액/건수, 시간대/요일/연령대별 분석 | ★★★★★ |
| `상주인구-상권.csv` | 거주 인구 통계 (성별, 연령대별) | ★★★★ |
| `직장인구-상권.csv` | 직장 인구 통계 (성별, 연령대별) | ★★★★ |
| `소득소비-상권.csv` | 월평균 소득, 지출 패턴 | ★★★★ |
| `집객시설-상권.csv` | 지하철역, 버스 정거장, 은행, 약국 등 집객시설 | ★★★★ |
| `길단위인구-상권.csv` | 유동인구 데이터 (시간대별, 연령대별) | ★★★★ |
| `상권변화지표-상권.csv` | 상권 활성화 지표 | ★★★ |

---

## 2. 산출물 디렉토리 구조

분석 결과는 다음과 같은 **분석 주제별 디렉토리 구조**로 저장됩니다:

```
REPORT/
├── 00_스크립트/
│   ├── 01_데이터로딩.py                # 초기 설정 및 데이터 로딩
│   ├── 02_경쟁환경분석.py              # Step 1 스크립트
│   ├── 03_고객분석.py                  # Step 2, 2-1 스크립트
│   ├── 04_인구유동분석.py              # Step 3, 4 스크립트
│   ├── 05_입지조건분석.py              # Step 5, 6 스크립트
│   ├── 06_종합평가.py                  # Step 7 스크립트
│   └── 99_전체실행.py                  # 전체 분석 일괄 실행
│
├── 01_경쟁환경분석/
│   ├── 경쟁환경_분석.csv               # 개폐업률, 성장률 통계
│   ├── 의원_점포수_추이.png            # 시계열 그래프
│   └── 성장률_분석.png                 # 성장률 차트
│
├── 02_고객분석/
│   ├── 타겟층_매출분석.csv             # 여성/연령대별 매출 통계
│   ├── 주중주말_패턴.csv               # 주중/주말 매출 통계
│   ├── 유사업종_비교.csv               # 피부관리실 vs 일반의원
│   ├── 타겟층_매출분석.png             # 4개 차트 통합
│   └── 유사업종_비교분석.png           # 비교 차트
│
├── 03_인구유동분석/
│   ├── 인구구조_분석.csv               # 상주/직장 인구 통계
│   ├── 유동인구_분석.csv               # 유동인구 통계
│   ├── 인구구조_비교.png               # 인구 구조 차트
│   └── 유동인구_분석.png               # 유동인구 차트
│
├── 04_입지조건분석/
│   ├── 접근성_인프라.csv               # 대중교통 및 의료 인프라
│   ├── 소득소비_분석.csv               # 소득 및 의료비 지출
│   ├── 접근성_인프라_분석.png          # 접근성 4개 차트
│   └── 소득_의료비지출_분석.png        # 소득/소비 차트
│
├── 05_종합평가/
│   ├── 종합평가.csv                    # 최종 종합 평가 결과
│   ├── 종합평가_레이더차트.png         # 레이더 차트
│   └── 계절성_분석.png                 # 계절성 패턴
│
└── 06_최종리포트/
    └── 피부과_입지분석_최종보고서.md   # 종합 보고서
```

### 디렉토리 설명

| 디렉토리 | 내용 | 파일 형식 |
|---------|------|----------|
| `00_스크립트/` | 분석 실행 Python 스크립트 | .py |
| `01_경쟁환경분석/` | 시장 규모, 경쟁 강도, 성장률 | CSV + PNG |
| `02_고객분석/` | 타겟층 매출, 주중/주말 패턴, 유사업종 | CSV + PNG |
| `03_인구유동분석/` | 상주/직장 인구, 유동인구 | CSV + PNG |
| `04_입지조건분석/` | 접근성, 인프라, 소득/소비 | CSV + PNG |
| `05_종합평가/` | 9개 지표 통합 평가, 계절성 | CSV + PNG |
| `06_최종리포트/` | 최종 보고서 문서 | MD |

---

## 3. 분석 스토리라인

### 📖 분석의 흐름

피부과 입지 선정은 다음과 같은 **스토리텔링 순서**로 진행됩니다:

#### **Act 1: 시장 이해하기** 🔍
> "강남구 의료 시장은 어떤 상황인가?"

1. **Step 1: 시장 규모 및 경쟁 환경 파악**
   - 상권별 일반의원 수와 추세
   - 개폐업률로 시장 안정성 확인
   - 성장성 있는 상권 식별

#### **Act 2: 고객 이해하기** 👥
> "우리의 타겟 고객은 누구이며, 어디에 있는가?"

2. **Step 2: 타겟 고객층 매출 패턴 분석**
   - 여성 및 20~40대 매출 비중 확인
   - 주중/주말 방문 패턴 파악
   - 피부관리실과 비교하여 피부과 수요 예측

3. **Step 3: 인구 구조 분석**
   - 상주인구 vs 직장인구 비교
   - 타겟층(여성 20~40대) 밀집도 확인

4. **Step 4: 유동인구 분석**
   - 상권 활성화 정도 파악
   - 잠재 고객 규모 추정

#### **Act 3: 입지 조건 평가하기** 📍
> "고객이 방문하기 편리한 곳은 어디인가?"

5. **Step 5: 접근성 및 인프라 분석**
   - 대중교통 편의성 (지하철, 버스)
   - 의료 인프라 집중도 (병원, 약국)

6. **Step 6: 소득 및 소비력 분석**
   - 상권별 소득 수준
   - 의료비 지출 성향

#### **Act 4: 최종 의사결정** 🎯
> "모든 조건을 고려했을 때 최적의 입지는?"

7. **Step 7: 종합 입지 평가**
   - 9개 지표 통합 스코어링
   - 레이더 차트로 상권별 강약점 시각화
   - 최종 입지 추천 (Top 3)

---

## 4. 단계별 EDA 실행

> [!IMPORTANT]
> **실행 전 체크리스트**
> - [ ] `koreanize-matplotlib` 라이브러리 설치 확인: `pip install koreanize-matplotlib`
> - [ ] 데이터 경로 확인: `d:/git_rk/data/서울시 주요 82장소 영역/Gangnam_CSV_20260203_094620/`
> - [ ] 8개 CSV 파일 존재 확인
> - [ ] Python 환경 활성화 확인

### 4.0 초기 설정 및 데이터 로딩

**스크립트 파일**: `REPORT/00_스크립트/01_데이터로딩.py`

**주요 개선사항 (v1.1)**:
- ✅ 파일별 로딩 진행상황 실시간 표시
- ✅ 한글 폰트 설정 최적화 (무한 로딩 방지)
- ✅ 강화된 에러 처리 및 메시지
- ✅ 파일 존재 여부 사전 확인

```python
# -*- coding: utf-8 -*-
"""
의원급 피부과 입지 분석 - 데이터 로딩 및 초기 설정
작성일: 2026-02-03
버전: 1.1 (무한 로딩 오류 수정)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager, rc
from math import pi
import os
import sys
from datetime import datetime

print("="*70)
print("의원급 피부과 입지 분석 - 데이터 로딩 시작")
print("="*70)

# 한글 폰트 설정 (최적화)
print("\n[1/3] 한글 폰트 설정 중...")
try:
    # koreanize_matplotlib는 import 시 자동으로 폰트 설정
    import koreanize_matplotlib
    print("✓ koreanize_matplotlib 로딩 완료")
except ImportError:
    print("⚠ koreanize_matplotlib 미설치 - 대체 폰트 사용")
    try:
        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False
        print("✓ Malgun Gothic 폰트 설정 완료")
    except:
        print("⚠ 한글 폰트 설정 실패 - 기본 폰트 사용")

# 경로 설정
data_path = 'd:/git_rk/data/서울시 주요 82장소 영역/Gangnam_CSV_20260203_094620/'
output_base = 'd:/git_rk/data/서울시 주요 82장소 영역/REPORT/'

# 산출물 디렉토리 생성
print("\n[2/3] 산출물 디렉토리 생성 중...")
dirs = [
    '00_스크립트',
    '01_경쟁환경분석',
    '02_고객분석',
    '03_인구유동분석',
    '04_입지조건분석',
    '05_종합평가',
    '06_최종리포트'
]

for dir_name in dirs:
    os.makedirs(os.path.join(output_base, dir_name), exist_ok=True)

print(f"✓ {len(dirs)}개 디렉토리 생성 완료")

# 데이터 로딩 (파일별 진행상황 표시)
print("\n[3/3] 데이터 로딩 중...")
print("-" * 70)

# 로딩할 파일 목록
files_to_load = [
    ('영역-상권', 'gangnam_서울시 상권분석서비스(영역-상권).csv'),
    ('점포-상권', 'gangnam_서울시 상권분석서비스(점포-상권)_2022년 1분기~2024년 4분기.csv'),
    ('추정매출-상권', 'gangnam_서울시 상권분석서비스(추정매출-상권)__2022년 1분기~2024년 4분기.csv'),
    ('상주인구-상권', 'gangnam_서울시 상권분석서비스(상주인구-상권).csv'),
    ('직장인구-상권', 'gangnam_서울시 상권분석서비스(직장인구-상권).csv'),
    ('소득소비-상권', 'gangnam_서울시 상권분석서비스(소득소비-상권).csv'),
    ('집객시설-상권', 'gangnam_서울시 상권분석서비스(집객시설-상권).csv'),
    ('길단위인구-상권', 'gangnam_서울시 상권분석서비스(길단위인구-상권).csv')
]

dataframes = {}
total_files = len(files_to_load)

try:
    for idx, (name, filename) in enumerate(files_to_load, 1):
        print(f"[{idx}/{total_files}] {name} 로딩 중...", end=' ', flush=True)
        
        file_path = os.path.join(data_path, filename)
        
        # 파일 존재 확인
        if not os.path.exists(file_path):
            print(f"❌ 파일 없음")
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filename}")
        
        # CSV 로딩
        df = pd.read_csv(file_path, encoding='utf-8')
        dataframes[name] = df
        
        print(f"✓ ({df.shape[0]:,} rows, {df.shape[1]} cols)")
    
    print("-" * 70)
    print("✓ 모든 CSV 파일 로딩 완료")
    
except FileNotFoundError as e:
    print(f"\n❌ 파일을 찾을 수 없습니다: {e}")
    print(f"\n확인 사항:")
    print(f"  1. 데이터 경로가 올바른지 확인: {data_path}")
    print(f"  2. CSV 파일이 해당 경로에 존재하는지 확인")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ 데이터 로딩 중 오류 발생: {e}")
    sys.exit(1)

# 데이터프레임 변수 할당
df_area = dataframes['영역-상권']
df_stores = dataframes['점포-상권']
df_sales = dataframes['추정매출-상권']
df_resident = dataframes['상주인구-상권']
df_worker = dataframes['직장인구-상권']
df_income = dataframes['소득소비-상권']
df_facilities = dataframes['집객시설-상권']
df_floating = dataframes['길단위인구-상권']

# 기준년분기 데이터 타입 변환
print("\n데이터 전처리 중...")
for df in [df_stores, df_sales, df_resident, df_worker, df_income, df_facilities, df_floating]:
    if '기준_년분기_코드' in df.columns:
        df['기준_년분기_코드'] = df['기준_년분기_코드'].astype(str)
        df['년도'] = df['기준_년분기_코드'].str[:4].astype(int)
        df['분기'] = df['기준_년분기_코드'].str[4:].astype(int)

# 최신 분기 자동 선택
latest_quarter = df_stores['기준_년분기_코드'].max()

print(f"\n{'='*70}")
print("✅ 데이터 로딩 완료")
print(f"{'='*70}")
print(f"  📅 분석 기준 분기: {latest_quarter}")
print(f"  📍 상권 수: {df_area.shape[0]}")
print(f"  📊 데이터셋 요약:")
print(f"     - 점포 데이터: {df_stores.shape[0]:,} rows")
print(f"     - 매출 데이터: {df_sales.shape[0]:,} rows")
print(f"     - 상주인구 데이터: {df_resident.shape[0]:,} rows")
print(f"     - 직장인구 데이터: {df_worker.shape[0]:,} rows")
print(f"     - 소득소비 데이터: {df_income.shape[0]:,} rows")
print(f"     - 집객시설 데이터: {df_facilities.shape[0]:,} rows")
print(f"     - 유동인구 데이터: {df_floating.shape[0]:,} rows")
print(f"{'='*70}")

# 전역 변수로 저장 (다른 스크립트에서 사용 가능)
if __name__ == "__main__":
    print("\n✅ 데이터 로딩 스크립트 실행 완료")
    print("📌 다음 단계: 02_경쟁환경분석.py 실행")
    print("\n" + "="*70)
```

**실행 방법**:
```bash
cd d:/git_rk/data/서울시 주요 82장소 영역/REPORT/00_스크립트
python 01_데이터로딩.py
```

---

### 🔍 Act 1: 시장 이해하기

### Step 1: 시장 규모 및 경쟁 환경 분석

```python
print("\n" + "="*70)
print("Step 1: 시장 규모 및 경쟁 환경 분석")
print("="*70)

# 1-1. 일반의원(피부과 포함) 경쟁 현황
medical_stores = df_stores[df_stores['서비스_업종_코드'] == 'CS200006'].copy()
medical_latest = medical_stores[medical_stores['기준_년분기_코드'] == latest_quarter]

print(f"\n📊 상권별 일반의원 현황 ({latest_quarter})")
print("-" * 70)
competition_current = medical_latest[['상권_코드_명', '점포_수', '개업_율', '폐업_률', '프랜차이즈_점포_수']].copy()
print(competition_current.to_string(index=False))

# 1-2. 시계열 트렌드 분석
print("\n📈 시계열 트렌드 분석 (2022Q1 ~ 2024Q4)")

plt.figure(figsize=(12, 6))
for location in medical_stores['상권_코드_명'].unique():
    location_data = medical_stores[medical_stores['상권_코드_명'] == location]
    plt.plot(location_data['기준_년분기_코드'], 
             location_data['점포_수'], 
             marker='o', 
             linewidth=2,
             label=location)

plt.title('상권별 일반의원 점포 수 추이', fontsize=14, fontweight='bold')
plt.xlabel('기준 년분기')
plt.ylabel('점포 수')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(output_base + '01_경쟁환경분석/의원_점포수_추이.png', dpi=300, bbox_inches='tight')
plt.show()

# 1-3. 개폐업률 및 성장률 분석
churn_analysis = medical_stores.groupby('상권_코드_명').agg({
    '개업_율': 'mean',
    '폐업_률': 'mean',
    '점포_수': 'mean'
}).round(2)

# 성장률 계산 (2022 vs 2024)
growth_analysis = medical_stores.groupby(['상권_코드_명', '년도'])['점포_수'].mean().unstack()
growth_analysis['성장률(%)'] = (
    (growth_analysis[2024] - growth_analysis[2022]) / growth_analysis[2022] * 100
).round(2)

print("\n📉 상권별 평균 개폐업률 및 성장률")
print("-" * 70)
competition_summary = churn_analysis.join(growth_analysis['성장률(%)'])
print(competition_summary)

# CSV 저장
competition_summary.to_csv(output_base + '01_경쟁환경분석/경쟁환경_분석.csv', encoding='utf-8-sig')
print("\n✓ 저장 완료: 01_경쟁환경분석/경쟁환경_분석.csv")

# 성장률 시각화
fig, ax = plt.subplots(figsize=(10, 6))
growth_analysis['성장률(%)'].plot(kind='bar', ax=ax, color='#2ecc71')
ax.set_title('상권별 일반의원 성장률 (2022 vs 2024)', fontsize=14, fontweight='bold')
ax.set_ylabel('성장률 (%)')
ax.set_xlabel('')
ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(output_base + '01_경쟁환경분석/성장률_분석.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n💡 인사이트:")
print(f"  - 가장 경쟁이 치열한 상권: {competition_current.loc[competition_current['점포_수'].idxmax(), '상권_코드_명']}")
print(f"  - 가장 빠르게 성장하는 상권: {growth_analysis['성장률(%)'].idxmax()}")
```

---

### 👥 Act 2: 고객 이해하기

### Step 2: 타겟 고객층 매출 패턴 분석

```python
print("\n" + "="*70)
print("Step 2: 타겟 고객층 매출 패턴 분석")
print("="*70)

# 2-1. 일반의원 매출 데이터 분석
medical_sales = df_sales[df_sales['서비스_업종_코드'] == 'CS200006'].copy()

# 타겟층 비중 계산
medical_sales['여성_매출_비중'] = (
    medical_sales['여성_매출_금액'] / medical_sales['당월_매출_금액'] * 100
)

medical_sales['2040대_매출_비중'] = (
    (medical_sales['연령대_20_매출_금액'] + 
     medical_sales['연령대_30_매출_금액'] + 
     medical_sales['연령대_40_매출_금액']) / 
    medical_sales['당월_매출_금액'] * 100
)

# 상권별 집계
target_summary = medical_sales.groupby('상권_코드_명').agg({
    '당월_매출_금액': 'mean',
    '여성_매출_비중': 'mean',
    '2040대_매출_비중': 'mean'
}).round(2)

target_summary.columns = ['평균_월매출', '여성_비중(%)', '2040대_비중(%)']

print("\n👩 타겟 고객층 매출 분석")
print("-" * 70)
print(target_summary)

# 2-2. 주중/주말 패턴 분석
medical_sales_latest = medical_sales[medical_sales['기준_년분기_코드'] == latest_quarter].copy()

medical_sales_latest['주중_비중'] = (
    medical_sales_latest['주중_매출_금액'] / 
    medical_sales_latest['당월_매출_금액'] * 100
)

weekday_analysis = medical_sales_latest.groupby('상권_코드_명').agg({
    '주중_매출_금액': 'mean',
    '주말_매출_금액': 'mean',
    '주중_비중': 'mean'
}).round(2)

weekday_analysis.columns = ['주중_매출', '주말_매출', '주중_비중(%)']

print("\n📅 주중/주말 매출 패턴")
print("-" * 70)
print(weekday_analysis)

# CSV 저장
target_summary.to_csv(output_base + '02_고객분석/타겟층_매출분석.csv', encoding='utf-8-sig')
weekday_analysis.to_csv(output_base + '02_고객분석/주중주말_패턴.csv', encoding='utf-8-sig')
print("\n✓ 저장 완료: 02_고객분석/타겟층_매출분석.csv, 주중주말_패턴.csv")

# 2-3. 시각화
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 여성 매출 비중
target_summary['여성_비중(%)'].plot(kind='bar', ax=axes[0, 0], color='#FF6B9D')
axes[0, 0].set_title('상권별 여성 매출 비중', fontsize=12, fontweight='bold')
axes[0, 0].set_ylabel('비중 (%)')
axes[0, 0].set_xlabel('')
axes[0, 0].grid(True, alpha=0.3, axis='y')
axes[0, 0].axhline(y=50, color='red', linestyle='--', alpha=0.5, label='50% 기준선')
axes[0, 0].legend()

# 20~40대 매출 비중
target_summary['2040대_비중(%)'].plot(kind='bar', ax=axes[0, 1], color='#4ECDC4')
axes[0, 1].set_title('상권별 20~40대 매출 비중', fontsize=12, fontweight='bold')
axes[0, 1].set_ylabel('비중 (%)')
axes[0, 1].set_xlabel('')
axes[0, 1].grid(True, alpha=0.3, axis='y')

# 주중/주말 매출 비교
weekday_analysis[['주중_매출', '주말_매출']].plot(
    kind='bar', ax=axes[1, 0], color=['#3498db', '#e74c3c']
)
axes[1, 0].set_title('상권별 주중/주말 매출 비교', fontsize=12, fontweight='bold')
axes[1, 0].set_ylabel('매출 금액 (원)')
axes[1, 0].set_xlabel('')
axes[1, 0].legend(['주중', '주말'])
axes[1, 0].grid(True, alpha=0.3, axis='y')

# 주중 매출 비중
weekday_analysis['주중_비중(%)'].plot(kind='bar', ax=axes[1, 1], color='#9b59b6')
axes[1, 1].set_title('상권별 주중 매출 비중', fontsize=12, fontweight='bold')
axes[1, 1].set_ylabel('비중 (%)')
axes[1, 1].set_xlabel('')
axes[1, 1].grid(True, alpha=0.3, axis='y')
axes[1, 1].axhline(y=70, color='green', linestyle='--', alpha=0.5, label='70% 기준선')
axes[1, 1].legend()

plt.tight_layout()
plt.savefig(output_base + '02_고객분석/타겟층_매출분석.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n💡 인사이트:")
print(f"  - 여성 매출 비중이 가장 높은 상권: {target_summary['여성_비중(%)'].idxmax()}")
print(f"  - 20~40대 매출 비중이 가장 높은 상권: {target_summary['2040대_비중(%)'].idxmax()}")
print(f"  - 주중 매출 비중이 가장 높은 상권: {weekday_analysis['주중_비중(%)'].idxmax()}")
```

### Step 2-1: 유사 업종 비교 (피부관리실)

```python
print("\n" + "="*70)
print("Step 2-1: 유사 업종 비교 분석 (피부관리실)")
print("="*70)

# 피부관리실과 일반의원 비교
skincare_sales = df_sales[df_sales['서비스_업종_코드'] == 'CS200030'].copy()
medical_sales_comp = df_sales[df_sales['서비스_업종_코드'] == 'CS200006'].copy()

# 타겟층 비중 계산
for df_temp in [skincare_sales, medical_sales_comp]:
    df_temp['여성_비중'] = df_temp['여성_매출_금액'] / df_temp['당월_매출_금액'] * 100
    df_temp['2040대_비중'] = (
        df_temp['연령대_20_매출_금액'] + 
        df_temp['연령대_30_매출_금액'] + 
        df_temp['연령대_40_매출_금액']
    ) / df_temp['당월_매출_금액'] * 100

# 상권별 비교
comparison = pd.DataFrame({
    '피부관리실_여성비중': skincare_sales.groupby('상권_코드_명')['여성_비중'].mean(),
    '일반의원_여성비중': medical_sales_comp.groupby('상권_코드_명')['여성_비중'].mean(),
    '피부관리실_2040대비중': skincare_sales.groupby('상권_코드_명')['2040대_비중'].mean(),
    '일반의원_2040대비중': medical_sales_comp.groupby('상권_코드_명')['2040대_비중'].mean()
}).round(2)

print("\n💄 피부관리실 vs 일반의원 타겟층 비교")
print("-" * 70)
print(comparison)

# CSV 저장
comparison.to_csv(output_base + '02_고객분석/유사업종_비교.csv', encoding='utf-8-sig')
print("\n✓ 저장 완료: 02_고객분석/유사업종_비교.csv")

# 시각화
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

comparison[['피부관리실_여성비중', '일반의원_여성비중']].plot(
    kind='bar', ax=axes[0], color=['#FF6B9D', '#4ECDC4']
)
axes[0].set_title('여성 고객 비중 비교', fontsize=12, fontweight='bold')
axes[0].set_ylabel('비중 (%)')
axes[0].set_xlabel('')
axes[0].legend(['피부관리실', '일반의원'])
axes[0].grid(True, alpha=0.3, axis='y')

comparison[['피부관리실_2040대비중', '일반의원_2040대비중']].plot(
    kind='bar', ax=axes[1], color=['#95E1D3', '#F38181']
)
axes[1].set_title('20~40대 고객 비중 비교', fontsize=12, fontweight='bold')
axes[1].set_ylabel('비중 (%)')
axes[1].set_xlabel('')
axes[1].legend(['피부관리실', '일반의원'])
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(output_base + '02_고객분석/유사업종_비교분석.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n💡 인사이트:")
print("  - 피부관리실은 일반의원 대비 여성 고객 비중이 높음")
print("  - 피부과는 피부관리실과 유사한 타겟층을 공유")
```

### Step 3: 인구 구조 분석

```python
print("\n" + "="*70)
print("Step 3: 인구 구조 분석")
print("="*70)

# 3-1. 상주인구 분석
latest_resident = df_resident[df_resident['기준_년분기_코드'] == latest_quarter].copy()

latest_resident['여성2040대_인구'] = (
    latest_resident['여성연령대_20_상주인구_수'] +
    latest_resident['여성연령대_30_상주인구_수'] +
    latest_resident['여성연령대_40_상주인구_수']
)

latest_resident['여성2040대_비중'] = (
    latest_resident['여성2040대_인구'] / latest_resident['총_상주인구_수'] * 100
).round(2)

# 3-2. 직장인구 분석
latest_worker = df_worker[df_worker['기준_년분기_코드'] == latest_quarter].copy()

latest_worker['여성2040대_직장인구'] = (
    latest_worker['여성연령대_20_직장_인구_수'] +
    latest_worker['여성연령대_30_직장_인구_수'] +
    latest_worker['여성연령대_40_직장_인구_수']
)

latest_worker['여성2040대_비중'] = (
    latest_worker['여성2040대_직장인구'] / latest_worker['총_직장_인구_수'] * 100
).round(2)

# 통합 데이터
population_summary = pd.DataFrame({
    '상주인구': latest_resident.set_index('상권_코드_명')['총_상주인구_수'],
    '직장인구': latest_worker.set_index('상권_코드_명')['총_직장_인구_수'],
    '상주_여성2040대': latest_resident.set_index('상권_코드_명')['여성2040대_인구'],
    '직장_여성2040대': latest_worker.set_index('상권_코드_명')['여성2040대_직장인구'],
    '상주_타겟비중(%)': latest_resident.set_index('상권_코드_명')['여성2040대_비중'],
    '직장_타겟비중(%)': latest_worker.set_index('상권_코드_명')['여성2040대_비중']
})

print("\n👨‍👩‍👧‍👦 상권별 인구 구조")
print("-" * 70)
print(population_summary)

# CSV 저장
population_summary.to_csv(output_base + '03_인구유동분석/인구구조_분석.csv', encoding='utf-8-sig')
print("\n✓ 저장 완료: 03_인구유동분석/인구구조_분석.csv")

# 시각화
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 상주인구 vs 직장인구
population_summary[['상주인구', '직장인구']].plot(kind='bar', ax=axes[0])
axes[0].set_title('상권별 상주인구 vs 직장인구', fontsize=12, fontweight='bold')
axes[0].set_ylabel('인구 수')
axes[0].set_xlabel('')
axes[0].legend()
axes[0].grid(True, alpha=0.3, axis='y')

# 여성 20~40대 비중 비교
population_summary[['상주_타겟비중(%)', '직장_타겟비중(%)']].plot(
    kind='bar', ax=axes[1], color=['#FF6B9D', '#4ECDC4']
)
axes[1].set_title('상권별 여성 20~40대 비중', fontsize=12, fontweight='bold')
axes[1].set_ylabel('비중 (%)')
axes[1].set_xlabel('')
axes[1].legend(['상주인구', '직장인구'])
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(output_base + '03_인구유동분석/인구구조_비교.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n💡 인사이트:")
print(f"  - 직장인구가 가장 많은 상권: {population_summary['직장인구'].idxmax()}")
print(f"  - 타겟층(여성 20~40대) 직장인구가 가장 많은 상권: {population_summary['직장_여성2040대'].idxmax()}")
```

### Step 4: 유동인구 분석

```python
print("\n" + "="*70)
print("Step 4: 유동인구 분석")
print("="*70)

# 유동인구 데이터 집계
latest_floating = df_floating[df_floating['기준_년분기_코드'] == latest_quarter].copy()

floating_summary = latest_floating.groupby('상권_코드_명').agg({
    '총_유동인구_수': 'sum',
    '연령대_20_유동인구_수': 'sum',
    '연령대_30_유동인구_수': 'sum',
    '연령대_40_유동인구_수': 'sum'
})

floating_summary['2040대_유동인구'] = (
    floating_summary['연령대_20_유동인구_수'] +
    floating_summary['연령대_30_유동인구_수'] +
    floating_summary['연령대_40_유동인구_수']
)

floating_summary['2040대_비중(%)'] = (
    floating_summary['2040대_유동인구'] / floating_summary['총_유동인구_수'] * 100
).round(2)

print("\n🚶 상권별 유동인구 분석")
print("-" * 70)
print(floating_summary[['총_유동인구_수', '2040대_유동인구', '2040대_비중(%)']])

# CSV 저장
floating_summary.to_csv(output_base + '03_인구유동분석/유동인구_분석.csv', encoding='utf-8-sig')
print("\n✓ 저장 완료: 03_인구유동분석/유동인구_분석.csv")

# 시각화
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 총 유동인구
floating_summary['총_유동인구_수'].plot(kind='bar', ax=axes[0], color='#1abc9c')
axes[0].set_title('상권별 총 유동인구', fontsize=12, fontweight='bold')
axes[0].set_ylabel('유동인구 수')
axes[0].set_xlabel('')
axes[0].grid(True, alpha=0.3, axis='y')

# 20~40대 유동인구 비중
floating_summary['2040대_비중(%)'].plot(kind='bar', ax=axes[1], color='#f39c12')
axes[1].set_title('상권별 20~40대 유동인구 비중', fontsize=12, fontweight='bold')
axes[1].set_ylabel('비중 (%)')
axes[1].set_xlabel('')
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(output_base + '03_인구유동분석/유동인구_분석.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n💡 인사이트:")
print(f"  - 유동인구가 가장 많은 상권: {floating_summary['총_유동인구_수'].idxmax()}")
print(f"  - 타겟층 유동인구 비중이 가장 높은 상권: {floating_summary['2040대_비중(%)'].idxmax()}")
```

---

### 📍 Act 3: 입지 조건 평가하기

### Step 5: 접근성 및 인프라 분석

```python
print("\n" + "="*70)
print("Step 5: 접근성 및 인프라 분석")
print("="*70)

# 집객시설 데이터
latest_facilities = df_facilities[df_facilities['기준_년분기_코드'] == latest_quarter].copy()

# 대중교통 접근성 점수
latest_facilities['대중교통_접근성'] = (
    latest_facilities['지하철_역_수'].fillna(0) * 2 + 
    latest_facilities['버스_정거장_수'].fillna(0)
)

# 의료 인프라 점수
latest_facilities['의료_인프라_점수'] = (
    latest_facilities['일반_병원_수'].fillna(0) * 3 +
    latest_facilities['약국_수'].fillna(0)
)

facilities_summary = latest_facilities[[
    '상권_코드_명', 
    '지하철_역_수', 
    '버스_정거장_수', 
    '대중교통_접근성',
    '일반_병원_수',
    '약국_수',
    '의료_인프라_점수'
]].set_index('상권_코드_명')

print("\n🚇 상권별 접근성 및 의료 인프라")
print("-" * 70)
print(facilities_summary)

# CSV 저장
facilities_summary.to_csv(output_base + '04_입지조건분석/접근성_인프라.csv', encoding='utf-8-sig')
print("\n✓ 저장 완료: 04_입지조건분석/접근성_인프라.csv")

# 시각화
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 지하철역 수
facilities_summary['지하철_역_수'].plot(kind='bar', ax=axes[0, 0], color='#3498db')
axes[0, 0].set_title('상권별 지하철역 수', fontsize=12, fontweight='bold')
axes[0, 0].set_ylabel('역 수')
axes[0, 0].set_xlabel('')
axes[0, 0].grid(True, alpha=0.3, axis='y')

# 버스 정거장 수
facilities_summary['버스_정거장_수'].plot(kind='bar', ax=axes[0, 1], color='#2ecc71')
axes[0, 1].set_title('상권별 버스 정거장 수', fontsize=12, fontweight='bold')
axes[0, 1].set_ylabel('정거장 수')
axes[0, 1].set_xlabel('')
axes[0, 1].grid(True, alpha=0.3, axis='y')

# 대중교통 접근성
facilities_summary['대중교통_접근성'].plot(kind='bar', ax=axes[1, 0], color='#9b59b6')
axes[1, 0].set_title('상권별 대중교통 접근성 종합', fontsize=12, fontweight='bold')
axes[1, 0].set_ylabel('접근성 점수')
axes[1, 0].set_xlabel('')
axes[1, 0].grid(True, alpha=0.3, axis='y')

# 의료 인프라
facilities_summary['의료_인프라_점수'].plot(kind='bar', ax=axes[1, 1], color='#e74c3c')
axes[1, 1].set_title('상권별 의료 인프라 점수', fontsize=12, fontweight='bold')
axes[1, 1].set_ylabel('인프라 점수')
axes[1, 1].set_xlabel('')
axes[1, 1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(output_base + '04_입지조건분석/접근성_인프라_분석.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n💡 인사이트:")
print(f"  - 대중교통 접근성이 가장 우수한 상권: {facilities_summary['대중교통_접근성'].idxmax()}")
print(f"  - 의료 인프라가 가장 집중된 상권: {facilities_summary['의료_인프라_점수'].idxmax()}")
```

### Step 6: 소득 및 소비력 분석

```python
print("\n" + "="*70)
print("Step 6: 소득 및 소비력 분석")
print("="*70)

# 소득 및 지출 분석
latest_income = df_income[df_income['기준_년분기_코드'] == latest_quarter].copy()

latest_income['의료비_지출_비중(%)'] = (
    latest_income['의료비_지출_총금액'] / latest_income['지출_총금액'] * 100
).round(2)

income_summary = latest_income[[
    '상권_코드_명', 
    '월_평균_소득_금액', 
    '의료비_지출_총금액', 
    '의료비_지출_비중(%)'
]].set_index('상권_코드_명')

print("\n💰 상권별 소득 및 의료비 지출")
print("-" * 70)
print(income_summary)

# CSV 저장
income_summary.to_csv(output_base + '04_입지조건분석/소득소비_분석.csv', encoding='utf-8-sig')
print("\n✓ 저장 완료: 04_입지조건분석/소득소비_분석.csv")

# 시각화
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 월평균 소득
income_summary['월_평균_소득_금액'].plot(kind='bar', ax=axes[0], color='#95E1D3')
axes[0].set_title('상권별 월평균 소득', fontsize=12, fontweight='bold')
axes[0].set_ylabel('소득 (원)')
axes[0].set_xlabel('')
axes[0].grid(True, alpha=0.3, axis='y')

# 의료비 지출 비중
income_summary['의료비_지출_비중(%)'].plot(kind='bar', ax=axes[1], color='#F38181')
axes[1].set_title('상권별 의료비 지출 비중', fontsize=12, fontweight='bold')
axes[1].set_ylabel('비중 (%)')
axes[1].set_xlabel('')
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(output_base + '04_입지조건분석/소득_의료비지출_분석.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n💡 인사이트:")
print(f"  - 소득 수준이 가장 높은 상권: {income_summary['월_평균_소득_금액'].idxmax()}")
print(f"  - 의료비 지출 비중이 가장 높은 상권: {income_summary['의료비_지출_비중(%)'].idxmax()}")
```

---

### 🎯 Act 4: 최종 의사결정

### Step 7: 종합 입지 평가

```python
print("\n" + "="*70)
print("Step 7: 종합 입지 평가")
print("="*70)

# 7-1. 평가 지표 통합
evaluation_df = pd.DataFrame()

# 경쟁 강도 (낮을수록 좋음)
competition_score = 1 / medical_latest.set_index('상권_코드_명')['점포_수']
evaluation_df['경쟁강도점수'] = (competition_score / competition_score.max() * 100)

# 타겟층 매출
evaluation_df['여성매출점수'] = (
    target_summary['여성_비중(%)'] / target_summary['여성_비중(%)'].max() * 100
)
evaluation_df['2040대매출점수'] = (
    target_summary['2040대_비중(%)'] / target_summary['2040대_비중(%)'].max() * 100
)

# 인구 구조
evaluation_df['직장인구점수'] = (
    population_summary['직장인구'] / population_summary['직장인구'].max() * 100
)
evaluation_df['타겟인구점수'] = (
    population_summary['직장_여성2040대'] / population_summary['직장_여성2040대'].max() * 100
)

# 소득
evaluation_df['소득점수'] = (
    income_summary['월_평균_소득_금액'] / income_summary['월_평균_소득_금액'].max() * 100
)

# 접근성
evaluation_df['접근성점수'] = (
    facilities_summary['대중교통_접근성'] / facilities_summary['대중교통_접근성'].max() * 100
)

# 의료 인프라
evaluation_df['의료인프라점수'] = (
    facilities_summary['의료_인프라_점수'] / facilities_summary['의료_인프라_점수'].max() * 100
)

# 유동인구
evaluation_df['유동인구점수'] = (
    floating_summary['총_유동인구_수'] / floating_summary['총_유동인구_수'].max() * 100
)

# 7-2. 가중치 적용
weights = {
    '경쟁강도점수': 0.15,
    '여성매출점수': 0.12,
    '2040대매출점수': 0.12,
    '직장인구점수': 0.12,
    '타겟인구점수': 0.08,
    '소득점수': 0.08,
    '접근성점수': 0.13,
    '의료인프라점수': 0.10,
    '유동인구점수': 0.10
}

# 가중치 검증
total_weight = sum(weights.values())
assert abs(total_weight - 1.0) < 0.001, f"가중치 합계 오류: {total_weight:.2f}"
print(f"\n✓ 가중치 합계 검증: {total_weight:.2f}")

# 종합 점수 계산
evaluation_df['종합점수'] = sum(
    evaluation_df[col] * weight 
    for col, weight in weights.items()
)

evaluation_df = evaluation_df.round(2).sort_values('종합점수', ascending=False)

print("\n🏆 피부과 입지 종합 평가 결과")
print("=" * 70)
print(evaluation_df)

# CSV 저장
evaluation_df.to_csv(output_base + '05_종합평가/종합평가.csv', encoding='utf-8-sig')
print("\n✓ 저장 완료: 05_종합평가/종합평가.csv")

# 7-3. 레이더 차트
categories = list(weights.keys())
N = len(categories)
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(projection='polar'))

colors = ['#FF6B9D', '#4ECDC4', '#95E1D3', '#F38181', '#3498db']
for idx, location in enumerate(evaluation_df.index):
    values = evaluation_df.loc[location, categories].values.tolist()
    values += values[:1]
    ax.plot(angles, values, 'o-', linewidth=2, label=location, color=colors[idx % len(colors)])
    ax.fill(angles, values, alpha=0.15, color=colors[idx % len(colors)])

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, size=10)
ax.set_ylim(0, 100)
ax.set_title('상권별 피부과 입지 평가 레이더 차트', size=16, fontweight='bold', pad=30)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=11)
ax.grid(True)

plt.tight_layout()
plt.savefig(output_base + '05_종합평가/종합평가_레이더차트.png', dpi=300, bbox_inches='tight')
plt.show()

# 7-4. 최종 추천
print("\n" + "="*70)
print("🎯 최종 입지 추천")
print("="*70)
for i in range(min(3, len(evaluation_df))):
    rank_emoji = ["🥇", "🥈", "🥉"][i]
    location = evaluation_df.index[i]
    score = evaluation_df.iloc[i]['종합점수']
    print(f"{rank_emoji} {i+1}순위: {location} (종합점수: {score:.2f}점)")
    
    # 강점 분석
    top_strengths = evaluation_df.loc[location, categories].nlargest(3)
    print(f"   강점: {', '.join([f'{k.replace('점수', '')}({v:.1f})' for k, v in top_strengths.items()])}")

print("\n" + "="*70)
print("✅ 분석 완료! 모든 결과가 REPORT 디렉토리에 저장되었습니다.")
print("="*70)
```

---

## 5. 추가 심화 분석

### 5.1 계절성 분석

```python
print("\n" + "="*70)
print("추가 분석: 계절성 패턴")
print("="*70)

# 분기별 매출 변동
seasonal_analysis = medical_sales.groupby(['상권_코드_명', '분기']).agg({
    '당월_매출_금액': 'mean'
}).reset_index()

seasonal_pivot = seasonal_analysis.pivot(
    index='분기', 
    columns='상권_코드_명', 
    values='당월_매출_금액'
)

print("\n📊 분기별 평균 매출")
print("-" * 70)
print(seasonal_pivot)

# 시각화
plt.figure(figsize=(10, 6))
for col in seasonal_pivot.columns:
    plt.plot(seasonal_pivot.index, seasonal_pivot[col], marker='o', linewidth=2, label=col)

plt.title('상권별 분기별 매출 추이', fontsize=14, fontweight='bold')
plt.xlabel('분기')
plt.ylabel('평균 매출 (원)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(output_base + '05_종합평가/계절성_분석.png', dpi=300, bbox_inches='tight')
plt.show()
```

---

## 6. 결과 리포트 작성

### 6.1 리포트 구성

분석 결과를 바탕으로 다음 구조의 최종 보고서를 작성합니다:

1. **Executive Summary** (1페이지)
   - 분석 목적 및 방법론
   - 주요 발견사항 3가지
   - 최종 추천 입지 Top 3

2. **시장 환경 분석** (2페이지)
   - 경쟁 강도 및 성장성
   - 시장 안정성 평가

3. **고객 분석** (2-3페이지)
   - 타겟층 매출 패턴
   - 유사 업종 비교
   - 인구 구조 및 유동인구

4. **입지 조건 평가** (2페이지)
   - 접근성 및 인프라
   - 소득 및 소비력

5. **종합 평가 및 추천** (2페이지)
   - 9개 지표 종합 평가
   - 레이더 차트
   - 최종 추천 및 실행 계획

### 6.2 산출물 체크리스트

#### 스크립트 파일 (Python)
- [ ] 01_데이터로딩.py
- [ ] 02_경쟁환경분석.py
- [ ] 03_고객분석.py
- [ ] 04_인구유동분석.py
- [ ] 05_입지조건분석.py
- [ ] 06_종합평가.py
- [ ] 99_전체실행.py

#### 01_경쟁환경분석/
- [x] 경쟁환경_분석.csv (개폐업률, 성장률)
- [x] 의원_점포수_추이.png
- [x] 성장률_분석.png

#### 02_고객분석/
- [x] 타겟층_매출분석.csv (여성/연령대별)
- [x] 주중주말_패턴.csv
- [x] 유사업종_비교.csv (피부관리실 vs 일반의원)
- [x] 타겟층_매출분석.png (4개 차트)
- [x] 유사업종_비교분석.png

#### 03_인구유동분석/
- [x] 인구구조_분석.csv (상주/직장 인구)
- [x] 유동인구_분석.csv
- [x] 인구구조_비교.png
- [x] 유동인구_분석.png

#### 04_입지조건분석/
- [x] 접근성_인프라.csv (대중교통, 의료 인프라)
- [x] 소득소비_분석.csv
- [x] 접근성_인프라_분석.png (4개 차트)
- [x] 소득_의료비지출_분석.png

#### 05_종합평가/
- [x] 종합평가.csv (9개 지표 통합)
- [x] 종합평가_레이더차트.png
- [x] 계절성_분석.png

#### 06_최종리포트/
- [ ] 피부과_입지분석_최종보고서.md

---

## 7. 참고 자료

### 7.1 업종 코드 매핑

| 코드 | 업종명 | 피부과 관련성 |
|------|--------|--------------|
| CS200006 | 일반의원 | ★★★★★ (피부과 포함) |
| CS200030 | 피부관리실 | ★★★★ (직접 경쟁업종) |

### 7.2 평가 지표 가중치

| 지표 | 가중치 | 설명 |
|------|--------|------|
| 경쟁강도점수 | 15% | 일반의원 수 (낮을수록 유리) |
| 여성매출점수 | 12% | 여성 고객 매출 비중 |
| 2040대매출점수 | 12% | 20~40대 매출 비중 |
| 직장인구점수 | 12% | 직장인구 규모 |
| 타겟인구점수 | 8% | 여성 20~40대 직장인구 |
| 소득점수 | 8% | 월평균 소득 수준 |
| 접근성점수 | 13% | 대중교통 접근성 |
| 의료인프라점수 | 10% | 병원/약국 집중도 |
| 유동인구점수 | 10% | 유동인구 규모 |

### 7.3 데이터 출처

- **서울시 상권분석서비스**: 서울 열린데이터광장
- **수집 기간**: 2022년 1분기 ~ 2024년 4분기
- **업데이트 주기**: 분기별

### 7.4 변경 이력

| 버전 | 날짜 | 주요 변경 사항 |
|------|------|---------------|
| 1.0 | 2026-02-03 | 초기 버전 |
| 2.0 | 2026-02-03 | 유동인구/의료인프라 추가, 유사업종 수정 |
| 3.0 | 2026-02-03 | **CSV 저장 방식 변경, 산출물 디렉토리 구조화, 스토리텔링 순서 개선** |

---

**문서 버전**: 3.00  
**최종 수정일**: 2026-02-03  
**작성자**: EDA 분석팀
