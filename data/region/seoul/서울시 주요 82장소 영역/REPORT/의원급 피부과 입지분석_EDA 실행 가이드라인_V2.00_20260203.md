# 의원급 피부과 입지 분석을 위한 EDA 실행 가이드라인

**작성일**: 2026-02-03  
**버전**: 2.00 (전면 개정)  
**데이터 기준**: 강남구 주요 82장소 상권 데이터 (2022년 1분기 ~ 2024년 4분기)  
**분석 목적**: 의원급 피부과 최적 입지 선정을 위한 탐색적 데이터 분석

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

## 2. 피부과 입지 분석 핵심 변수

### 2.1 경쟁 환경 분석 (점포-상권 데이터)

> [!IMPORTANT]
> 피부과는 `서비스_업종_코드` **CS200006 (일반의원)** 카테고리에 포함됨

#### 주요 분석 변수
- **점포_수**: 현재 일반의원 수 (경쟁 강도)
- **개업_율 / 개업_점포_수**: 신규 진입 추세
- **폐업_률 / 폐업_점포_수**: 시장 안정성 지표
- **프랜차이즈_점포_수**: 대형 체인 의원 현황

#### 분석 방법
```python
# 1. 상권별 일반의원 경쟁 강도 비교
competition_analysis = df_stores[
    df_stores['서비스_업종_코드'] == 'CS200006'
].groupby('상권_코드_명').agg({
    '점포_수': 'mean',
    '개업_율': 'mean',
    '폐업_률': 'mean'
})

# 2. 시계열 트렌드 분석 (2022Q1 ~ 2024Q4)
trend_analysis = df_stores[
    df_stores['서비스_업종_코드'] == 'CS200006'
].pivot_table(
    index='기준_년분기_코드',
    columns='상권_코드_명',
    values='점포_수'
)
```

### 2.2 타겟 고객층 분석 (추정매출 데이터)

#### 피부과 주요 타겟층
1. **여성 고객** (피부 관리 수요 높음)
2. **20~40대** (미용 관심도 높은 연령층)
3. **평일 낮 시간대** (직장인 점심시간, 주부 오후 시간)
4. **주중 방문 선호** (평일 진료 수요)

#### 주요 분석 변수
- **여성_매출_금액 / 여성_매출_건수**: 여성 고객 비중
- **연령대_20_매출_금액 ~ 연령대_40_매출_금액**: 주요 타겟 연령대 소비력
- **시간대_11~14_매출_금액**: 점심시간 유동 인구
- **주중_매출_금액 vs 주말_매출_금액**: 평일/주말 패턴

#### 분석 방법
```python
# 1. 상권별 타겟층 매출 비중 계산
target_customer_analysis = df_sales[
    df_sales['서비스_업종_코드'] == 'CS200006'
].copy()

target_customer_analysis['여성_비중'] = (
    target_customer_analysis['여성_매출_금액'] / 
    target_customer_analysis['당월_매출_금액'] * 100
)

target_customer_analysis['2040대_비중'] = (
    (target_customer_analysis['연령대_20_매출_금액'] + 
     target_customer_analysis['연령대_30_매출_금액'] + 
     target_customer_analysis['연령대_40_매출_금액']) / 
    target_customer_analysis['당월_매출_금액'] * 100
)

target_customer_analysis['주중_비중'] = (
    target_customer_analysis['주중_매출_금액'] / 
    target_customer_analysis['당월_매출_금액'] * 100
)

# 2. 상권별 집계
target_summary = target_customer_analysis.groupby('상권_코드_명').agg({
    '여성_비중': 'mean',
    '2040대_비중': 'mean',
    '주중_비중': 'mean',
    '당월_매출_금액': 'mean'
})
```

### 2.3 인구 구조 분석

#### 상주인구 (거주민)
```python
# 여성 20~40대 거주 인구 비중
resident_analysis = df_resident.copy()
resident_analysis['여성2040대_인구'] = (
    resident_analysis['여성연령대_20_상주인구_수'] +
    resident_analysis['여성연령대_30_상주인구_수'] +
    resident_analysis['여성연령대_40_상주인구_수']
)
resident_analysis['여성2040대_비중'] = (
    resident_analysis['여성2040대_인구'] / 
    resident_analysis['총_상주인구_수'] * 100
)
```

#### 직장인구 (유동 고객)
```python
# 여성 20~40대 직장 인구 비중
worker_analysis = df_worker.copy()
worker_analysis['여성2040대_직장인구'] = (
    worker_analysis['여성연령대_20_직장_인구_수'] +
    worker_analysis['여성연령대_30_직장_인구_수'] +
    worker_analysis['여성연령대_40_직장_인구_수']
)
worker_analysis['여성2040대_비중'] = (
    worker_analysis['여성2040대_직장인구'] / 
    worker_analysis['총_직장_인구_수'] * 100
)
```

### 2.4 접근성 분석 (집객시설 데이터)

> [!IMPORTANT]
> 대중교통 접근성은 피부과 방문 편의성과 직결되는 핵심 지표

#### 주요 분석 변수
- **지하철_역_수**: 상권 내 지하철역 개수 (환승역 포함)
- **버스_정거장_수**: 상권 내 버스 정류장 개수
- **약국_수**: 의료 관련 편의시설 (처방전 수령 편의성)
- **일반_병원_수**: 의료 인프라 집중도

#### 접근성 점수 계산
```python
# 대중교통 접근성 = 지하철역 × 2 + 버스 정거장
facilities['대중교통_접근성'] = (
    facilities['지하철_역_수'].fillna(0) * 2 + 
    facilities['버스_정거장_수'].fillna(0)
)

# 의료 인프라 점수 = 일반병원 × 3 + 약국
facilities['의료_인프라_점수'] = (
    facilities['일반_병원_수'].fillna(0) * 3 +
    facilities['약국_수'].fillna(0)
)
```

### 2.5 유동인구 분석 (길단위인구 데이터)

> [!TIP]
> 유동인구는 상권 활성화와 잠재 고객 규모를 나타내는 핵심 지표

#### 주요 분석 변수
- **총_유동인구_수**: 상권 내 전체 유동인구
- **연령대_20~40_유동인구**: 타겟층 유동인구
- **시간대별_유동인구**: 시간대별 유동 패턴
- **요일별_유동인구**: 평일/주말 유동 패턴

#### 분석 방법
```python
# 상권별 유동인구 집계
floating_summary = df_floating.groupby('상권_코드_명').agg({
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

floating_summary['2040대_비중'] = (
    floating_summary['2040대_유동인구'] / 
    floating_summary['총_유동인구_수'] * 100
)
```

### 2.6 소득 및 소비력 분석

#### 주요 분석 변수
- **월_평균_소득_금액**: 상권 소득 수준
- **의료비_지출_총금액**: 의료 서비스 지출 규모
- **생활용품_지출_총금액**: 미용/건강 관련 소비 성향

```python
# 상권별 소득 및 의료비 지출 분석
income_analysis = df_income.groupby('상권_코드_명').agg({
    '월_평균_소득_금액': 'mean',
    '의료비_지출_총금액': 'mean',
    '지출_총금액': 'mean'
})

income_analysis['의료비_지출_비중'] = (
    income_analysis['의료비_지출_총금액'] / 
    income_analysis['지출_총금액'] * 100
)
```

---

## 3. 단계별 EDA 실행 프로세스

### 3.1 데이터 로딩 및 전처리

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager, rc
from math import pi

# 한글 폰트 설정
import koreanize_matplotlib

# 데이터 로딩
data_path = 'd:/git_rk/data/서울시 주요 82장소 영역/Gangnam_CSV_20260203_094620/'

df_area = pd.read_csv(data_path + 'gangnam_서울시 상권분석서비스(영역-상권).csv', encoding='utf-8')
df_stores = pd.read_csv(data_path + 'gangnam_서울시 상권분석서비스(점포-상권)_2022년 1분기~2024년 4분기.csv', encoding='utf-8')
df_sales = pd.read_csv(data_path + 'gangnam_서울시 상권분석서비스(추정매출-상권)__2022년 1분기~2024년 4분기.csv', encoding='utf-8')
df_resident = pd.read_csv(data_path + 'gangnam_서울시 상권분석서비스(상주인구-상권).csv', encoding='utf-8')
df_worker = pd.read_csv(data_path + 'gangnam_서울시 상권분석서비스(직장인구-상권).csv', encoding='utf-8')
df_income = pd.read_csv(data_path + 'gangnam_서울시 상권분석서비스(소득소비-상권).csv', encoding='utf-8')
df_facilities = pd.read_csv(data_path + 'gangnam_서울시 상권분석서비스(집객시설-상권).csv', encoding='utf-8')
df_floating = pd.read_csv(data_path + 'gangnam_서울시 상권분석서비스(길단위인구-상권).csv', encoding='utf-8')

# 기준년분기 데이터 타입 변환
for df in [df_stores, df_sales, df_resident, df_worker, df_income, df_facilities, df_floating]:
    df['기준_년분기_코드'] = df['기준_년분기_코드'].astype(str)
    df['년도'] = df['기준_년분기_코드'].str[:4].astype(int)
    df['분기'] = df['기준_년분기_코드'].str[4:].astype(int)

# 최신 분기 자동 선택
latest_quarter = df_stores['기준_년분기_코드'].max()
print(f"데이터 로딩 완료 - 분석 기준 분기: {latest_quarter}")
print(f"상권 수: {df_area.shape[0]}")
print(f"점포 데이터: {df_stores.shape[0]:,} rows")
print(f"매출 데이터: {df_sales.shape[0]:,} rows")
```

### 3.2 Step 1: 경쟁 환경 분석

```python
# 1-1. 일반의원(피부과 포함) 경쟁 현황
medical_stores = df_stores[df_stores['서비스_업종_코드'] == 'CS200006'].copy()

# 최신 분기 데이터
medical_latest = medical_stores[medical_stores['기준_년분기_코드'] == latest_quarter]

print("=" * 60)
print(f"상권별 일반의원 경쟁 현황 ({latest_quarter})")
print("=" * 60)
print(medical_latest[['상권_코드_명', '점포_수', '개업_율', '폐업_률', '프랜차이즈_점포_수']])

# 1-2. 시계열 트렌드 시각화
plt.figure(figsize=(12, 6))
for location in medical_stores['상권_코드_명'].unique():
    location_data = medical_stores[medical_stores['상권_코드_명'] == location]
    plt.plot(location_data['기준_년분기_코드'], 
             location_data['점포_수'], 
             marker='o', 
             label=location)

plt.title('상권별 일반의원 점포 수 추이 (2022Q1 ~ 2024Q4)', fontsize=14, fontweight='bold')
plt.xlabel('기준 년분기')
plt.ylabel('점포 수')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(data_path + '../REPORT/의원_점포수_추이.png', dpi=300, bbox_inches='tight')
plt.show()

# 1-3. 개폐업률 분석
churn_analysis = medical_stores.groupby('상권_코드_명').agg({
    '개업_율': 'mean',
    '폐업_률': 'mean',
    '점포_수': 'mean'
}).round(2)

print("\n상권별 평균 개폐업률")
print(churn_analysis)
```

### 3.3 Step 2: 타겟 고객층 매출 분석

```python
# 2-1. 일반의원 매출 데이터 추출
medical_sales = df_sales[df_sales['서비스_업종_코드'] == 'CS200006'].copy()

# 2-2. 타겟층 비중 계산
medical_sales['여성_매출_비중'] = (
    medical_sales['여성_매출_금액'] / medical_sales['당월_매출_금액'] * 100
)

medical_sales['20대_매출_비중'] = (
    medical_sales['연령대_20_매출_금액'] / medical_sales['당월_매출_금액'] * 100
)

medical_sales['30대_매출_비중'] = (
    medical_sales['연령대_30_매출_금액'] / medical_sales['당월_매출_금액'] * 100
)

medical_sales['40대_매출_비중'] = (
    medical_sales['연령대_40_매출_금액'] / medical_sales['당월_매출_금액'] * 100
)

medical_sales['2040대_매출_비중'] = (
    medical_sales['20대_매출_비중'] + 
    medical_sales['30대_매출_비중'] + 
    medical_sales['40대_매출_비중']
)

# 2-3. 상권별 타겟층 분석
target_summary = medical_sales.groupby('상권_코드_명').agg({
    '당월_매출_금액': 'mean',
    '여성_매출_비중': 'mean',
    '2040대_매출_비중': 'mean',
    '20대_매출_비중': 'mean',
    '30대_매출_비중': 'mean',
    '40대_매출_비중': 'mean'
}).round(2)

print("\n" + "=" * 60)
print("상권별 일반의원 타겟 고객층 매출 분석")
print("=" * 60)
print(target_summary)

# 2-4. 주중/주말 매출 패턴 분석
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

print("\n상권별 주중/주말 매출 분석")
print(weekday_analysis)

# 2-5. 시각화: 타겟층 및 주중/주말 비교
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 여성 매출 비중
target_summary['여성_매출_비중'].plot(kind='bar', ax=axes[0, 0], color='#FF6B9D')
axes[0, 0].set_title('상권별 여성 매출 비중', fontsize=12, fontweight='bold')
axes[0, 0].set_ylabel('비중 (%)')
axes[0, 0].set_xlabel('')
axes[0, 0].grid(True, alpha=0.3, axis='y')
axes[0, 0].axhline(y=50, color='red', linestyle='--', alpha=0.5, label='50% 기준선')
axes[0, 0].legend()

# 20~40대 매출 비중
target_summary['2040대_매출_비중'].plot(kind='bar', ax=axes[0, 1], color='#4ECDC4')
axes[0, 1].set_title('상권별 20~40대 매출 비중', fontsize=12, fontweight='bold')
axes[0, 1].set_ylabel('비중 (%)')
axes[0, 1].set_xlabel('')
axes[0, 1].grid(True, alpha=0.3, axis='y')

# 주중/주말 매출 비교
weekday_analysis[['주중_매출_금액', '주말_매출_금액']].plot(
    kind='bar', ax=axes[1, 0], color=['#3498db', '#e74c3c']
)
axes[1, 0].set_title('상권별 주중/주말 매출 비교', fontsize=12, fontweight='bold')
axes[1, 0].set_ylabel('매출 금액 (원)')
axes[1, 0].set_xlabel('')
axes[1, 0].legend(['주중', '주말'])
axes[1, 0].grid(True, alpha=0.3, axis='y')

# 주중 매출 비중
weekday_analysis['주중_비중'].plot(kind='bar', ax=axes[1, 1], color='#9b59b6')
axes[1, 1].set_title('상권별 주중 매출 비중', fontsize=12, fontweight='bold')
axes[1, 1].set_ylabel('비중 (%)')
axes[1, 1].set_xlabel('')
axes[1, 1].grid(True, alpha=0.3, axis='y')
axes[1, 1].axhline(y=70, color='green', linestyle='--', alpha=0.5, label='70% 기준선')
axes[1, 1].legend()

plt.tight_layout()
plt.savefig(data_path + '../REPORT/타겟층_매출분석.png', dpi=300, bbox_inches='tight')
plt.show()
```

### 3.4 Step 3: 인구 구조 분석

```python
# 3-1. 상주인구 분석
latest_resident = df_resident[df_resident['기준_년분기_코드'] == latest_quarter].copy()

latest_resident['여성2040대_인구'] = (
    latest_resident['여성연령대_20_상주인구_수'] +
    latest_resident['여성연령대_30_상주인구_수'] +
    latest_resident['여성연령대_40_상주인구_수']
)

latest_resident['여성2040대_비중'] = (
    latest_resident['여성2040대_인구'] / latest_resident['총_상주인구_수'] * 100
)

print("\n" + "=" * 60)
print("상권별 상주인구 분석")
print("=" * 60)
print(latest_resident[['상권_코드_명', '총_상주인구_수', '여성2040대_인구', '여성2040대_비중']])

# 3-2. 직장인구 분석
latest_worker = df_worker[df_worker['기준_년분기_코드'] == latest_quarter].copy()

latest_worker['여성2040대_직장인구'] = (
    latest_worker['여성연령대_20_직장_인구_수'] +
    latest_worker['여성연령대_30_직장_인구_수'] +
    latest_worker['여성연령대_40_직장_인구_수']
)

latest_worker['여성2040대_비중'] = (
    latest_worker['여성2040대_직장인구'] / latest_worker['총_직장_인구_수'] * 100
)

print("\n상권별 직장인구 분석")
print(latest_worker[['상권_코드_명', '총_직장_인구_수', '여성2040대_직장인구', '여성2040대_비중']])

# 3-3. 시각화: 인구 구조 비교
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 상주인구 vs 직장인구
population_comparison = pd.DataFrame({
    '상주인구': latest_resident.set_index('상권_코드_명')['총_상주인구_수'],
    '직장인구': latest_worker.set_index('상권_코드_명')['총_직장_인구_수']
})

population_comparison.plot(kind='bar', ax=axes[0])
axes[0].set_title('상권별 상주인구 vs 직장인구', fontsize=12, fontweight='bold')
axes[0].set_ylabel('인구 수')
axes[0].set_xlabel('')
axes[0].legend()
axes[0].grid(True, alpha=0.3, axis='y')

# 여성 20~40대 비중 비교
target_pop_comparison = pd.DataFrame({
    '상주인구': latest_resident.set_index('상권_코드_명')['여성2040대_비중'],
    '직장인구': latest_worker.set_index('상권_코드_명')['여성2040대_비중']
})

target_pop_comparison.plot(kind='bar', ax=axes[1], color=['#FF6B9D', '#4ECDC4'])
axes[1].set_title('상권별 여성 20~40대 비중', fontsize=12, fontweight='bold')
axes[1].set_ylabel('비중 (%)')
axes[1].set_xlabel('')
axes[1].legend()
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(data_path + '../REPORT/인구구조_비교.png', dpi=300, bbox_inches='tight')
plt.show()
```

### 3.5 Step 4: 접근성 및 인프라 분석

```python
# 4-1. 집객시설 데이터 추출
latest_facilities = df_facilities[df_facilities['기준_년분기_코드'] == latest_quarter].copy()

# 4-2. 대중교통 접근성 점수 계산
latest_facilities['대중교통_접근성'] = (
    latest_facilities['지하철_역_수'].fillna(0) * 2 +  # 지하철 가중치 2배
    latest_facilities['버스_정거장_수'].fillna(0)
)

# 4-3. 의료 인프라 점수 계산
latest_facilities['의료_인프라_점수'] = (
    latest_facilities['일반_병원_수'].fillna(0) * 3 +
    latest_facilities['약국_수'].fillna(0)
)

print("\n" + "=" * 60)
print("상권별 접근성 및 의료 인프라 분석")
print("=" * 60)
print(latest_facilities[[
    '상권_코드_명', 
    '지하철_역_수', 
    '버스_정거장_수', 
    '대중교통_접근성',
    '일반_병원_수',
    '약국_수',
    '의료_인프라_점수'
]])

# 4-4. 시각화
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 지하철역 수
latest_facilities.set_index('상권_코드_명')['지하철_역_수'].plot(
    kind='bar', ax=axes[0, 0], color='#3498db'
)
axes[0, 0].set_title('상권별 지하철역 수', fontsize=12, fontweight='bold')
axes[0, 0].set_ylabel('역 수')
axes[0, 0].set_xlabel('')
axes[0, 0].grid(True, alpha=0.3, axis='y')

# 버스 정거장 수
latest_facilities.set_index('상권_코드_명')['버스_정거장_수'].plot(
    kind='bar', ax=axes[0, 1], color='#2ecc71'
)
axes[0, 1].set_title('상권별 버스 정거장 수', fontsize=12, fontweight='bold')
axes[0, 1].set_ylabel('정거장 수')
axes[0, 1].set_xlabel('')
axes[0, 1].grid(True, alpha=0.3, axis='y')

# 대중교통 접근성 종합
latest_facilities.set_index('상권_코드_명')['대중교통_접근성'].plot(
    kind='bar', ax=axes[1, 0], color='#9b59b6'
)
axes[1, 0].set_title('상권별 대중교통 접근성 종합 점수', fontsize=12, fontweight='bold')
axes[1, 0].set_ylabel('접근성 점수')
axes[1, 0].set_xlabel('')
axes[1, 0].grid(True, alpha=0.3, axis='y')

# 의료 인프라 점수
latest_facilities.set_index('상권_코드_명')['의료_인프라_점수'].plot(
    kind='bar', ax=axes[1, 1], color='#e74c3c'
)
axes[1, 1].set_title('상권별 의료 인프라 점수', fontsize=12, fontweight='bold')
axes[1, 1].set_ylabel('인프라 점수')
axes[1, 1].set_xlabel('')
axes[1, 1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(data_path + '../REPORT/접근성_인프라_분석.png', dpi=300, bbox_inches='tight')
plt.show()
```

### 3.6 Step 5: 유동인구 분석

```python
# 5-1. 유동인구 데이터 집계
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

floating_summary['2040대_비중'] = (
    floating_summary['2040대_유동인구'] / floating_summary['총_유동인구_수'] * 100
)

print("\n" + "=" * 60)
print("상권별 유동인구 분석")
print("=" * 60)
print(floating_summary.round(2))

# 5-2. 시각화
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 총 유동인구
floating_summary['총_유동인구_수'].plot(kind='bar', ax=axes[0], color='#1abc9c')
axes[0].set_title('상권별 총 유동인구', fontsize=12, fontweight='bold')
axes[0].set_ylabel('유동인구 수')
axes[0].set_xlabel('')
axes[0].grid(True, alpha=0.3, axis='y')

# 20~40대 유동인구 비중
floating_summary['2040대_비중'].plot(kind='bar', ax=axes[1], color='#f39c12')
axes[1].set_title('상권별 20~40대 유동인구 비중', fontsize=12, fontweight='bold')
axes[1].set_ylabel('비중 (%)')
axes[1].set_xlabel('')
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(data_path + '../REPORT/유동인구_분석.png', dpi=300, bbox_inches='tight')
plt.show()
```

### 3.7 Step 6: 소득 및 소비력 분석

```python
# 6-1. 소득 및 지출 분석
latest_income = df_income[df_income['기준_년분기_코드'] == latest_quarter].copy()

latest_income['의료비_지출_비중'] = (
    latest_income['의료비_지출_총금액'] / latest_income['지출_총금액'] * 100
)

print("\n" + "=" * 60)
print("상권별 소득 및 의료비 지출 분석")
print("=" * 60)
print(latest_income[['상권_코드_명', '월_평균_소득_금액', '의료비_지출_총금액', '의료비_지출_비중']])

# 6-2. 시각화
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 월평균 소득
latest_income.set_index('상권_코드_명')['월_평균_소득_금액'].plot(
    kind='bar', ax=axes[0], color='#95E1D3'
)
axes[0].set_title('상권별 월평균 소득', fontsize=12, fontweight='bold')
axes[0].set_ylabel('소득 (원)')
axes[0].set_xlabel('')
axes[0].grid(True, alpha=0.3, axis='y')

# 의료비 지출 비중
latest_income.set_index('상권_코드_명')['의료비_지출_비중'].plot(
    kind='bar', ax=axes[1], color='#F38181'
)
axes[1].set_title('상권별 의료비 지출 비중', fontsize=12, fontweight='bold')
axes[1].set_ylabel('비중 (%)')
axes[1].set_xlabel('')
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(data_path + '../REPORT/소득_의료비지출_분석.png', dpi=300, bbox_inches='tight')
plt.show()
```

### 3.8 Step 7: 종합 입지 평가 스코어링

```python
# 7-1. 평가 지표 통합
evaluation_df = pd.DataFrame()

# 경쟁 강도 (낮을수록 좋음 - 역수 사용)
competition_score = 1 / medical_latest.set_index('상권_코드_명')['점포_수']
evaluation_df['경쟁강도점수'] = (competition_score / competition_score.max() * 100)

# 타겟층 매출 비중 (높을수록 좋음)
evaluation_df['여성매출점수'] = (
    target_summary['여성_매출_비중'] / target_summary['여성_매출_비중'].max() * 100
)
evaluation_df['2040대매출점수'] = (
    target_summary['2040대_매출_비중'] / target_summary['2040대_매출_비중'].max() * 100
)

# 인구 구조 (높을수록 좋음)
evaluation_df['직장인구점수'] = (
    latest_worker.set_index('상권_코드_명')['총_직장_인구_수'] / 
    latest_worker['총_직장_인구_수'].max() * 100
)

evaluation_df['타겟인구점수'] = (
    latest_worker.set_index('상권_코드_명')['여성2040대_직장인구'] / 
    latest_worker['여성2040대_직장인구'].max() * 100
)

# 소득 수준 (높을수록 좋음)
evaluation_df['소득점수'] = (
    latest_income.set_index('상권_코드_명')['월_평균_소득_금액'] / 
    latest_income['월_평균_소득_금액'].max() * 100
)

# 접근성 점수 (높을수록 좋음)
evaluation_df['접근성점수'] = (
    latest_facilities.set_index('상권_코드_명')['대중교통_접근성'] / 
    latest_facilities['대중교통_접근성'].max() * 100
)

# 의료 인프라 점수 (높을수록 좋음)
evaluation_df['의료인프라점수'] = (
    latest_facilities.set_index('상권_코드_명')['의료_인프라_점수'] / 
    latest_facilities['의료_인프라_점수'].max() * 100
)

# 유동인구 점수 (높을수록 좋음)
evaluation_df['유동인구점수'] = (
    floating_summary['총_유동인구_수'] / 
    floating_summary['총_유동인구_수'].max() * 100
)

# 7-2. 종합 점수 계산 (가중치 적용)
weights = {
    '경쟁강도점수': 0.15,      # 경쟁 강도
    '여성매출점수': 0.12,      # 여성 타겟층
    '2040대매출점수': 0.12,    # 연령 타겟층
    '직장인구점수': 0.12,      # 직장인구 규모
    '타겟인구점수': 0.08,      # 타겟 직장인구
    '소득점수': 0.08,          # 소득 수준
    '접근성점수': 0.13,        # 대중교통 접근성
    '의료인프라점수': 0.10,    # 의료 인프라
    '유동인구점수': 0.10       # 유동인구 규모
}

# 가중치 합계 검증
total_weight = sum(weights.values())
assert abs(total_weight - 1.0) < 0.001, f"가중치 합계가 {total_weight:.2f}입니다. 1.0이어야 합니다!"
print(f"\n가중치 합계 검증: {total_weight:.2f} ✓")

evaluation_df['종합점수'] = sum(
    evaluation_df[col] * weight 
    for col, weight in weights.items()
)

evaluation_df = evaluation_df.round(2).sort_values('종합점수', ascending=False)

print("\n" + "=" * 60)
print("피부과 입지 종합 평가 결과")
print("=" * 60)
print(evaluation_df)

# 7-3. 시각화: 레이더 차트
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
plt.savefig(data_path + '../REPORT/종합평가_레이더차트.png', dpi=300, bbox_inches='tight')
plt.show()

# 7-4. 최종 추천
print("\n" + "=" * 60)
print("최종 입지 추천")
print("=" * 60)
for i in range(min(3, len(evaluation_df))):
    print(f"{i+1}순위 추천: {evaluation_df.index[i]} (종합점수: {evaluation_df.iloc[i]['종합점수']:.2f})")
```

---

## 4. 추가 심화 분석 (선택사항)

### 4.1 유사 업종 벤치마킹

피부과와 직접 경쟁 관계에 있는 **피부관리실(CS200030)**과 비교 분석:

```python
# 피부관리실(CS200030)과 일반의원(CS200006) 비교 분석
skincare_sales = df_sales[df_sales['서비스_업종_코드'] == 'CS200030'].copy()
medical_sales_comp = df_sales[df_sales['서비스_업종_코드'] == 'CS200006'].copy()

# 타겟층 비중 계산
for df_temp, name in [(skincare_sales, '피부관리실'), (medical_sales_comp, '일반의원')]:
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
})

print("\n피부관리실 vs 일반의원 타겟층 비교")
print(comparison.round(2))

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
plt.savefig(data_path + '../REPORT/유사업종_비교분석.png', dpi=300, bbox_inches='tight')
plt.show()
```

### 4.2 계절성 분석

```python
# 분기별 매출 변동 패턴
seasonal_analysis = medical_sales.groupby(['상권_코드_명', '분기']).agg({
    '당월_매출_금액': 'mean'
}).reset_index()

seasonal_pivot = seasonal_analysis.pivot(
    index='분기', 
    columns='상권_코드_명', 
    values='당월_매출_금액'
)

print("\n분기별 평균 매출 (계절성 분석)")
print(seasonal_pivot)

# 시각화
plt.figure(figsize=(10, 6))
for col in seasonal_pivot.columns:
    plt.plot(seasonal_pivot.index, seasonal_pivot[col], marker='o', label=col)

plt.title('상권별 분기별 매출 추이', fontsize=14, fontweight='bold')
plt.xlabel('분기')
plt.ylabel('평균 매출 (원)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(data_path + '../REPORT/계절성_분석.png', dpi=300, bbox_inches='tight')
plt.show()
```

### 4.3 상권 성장성 분석

```python
# 2022년 vs 2024년 비교
growth_analysis = medical_stores.groupby(['상권_코드_명', '년도'])['점포_수'].mean().unstack()
growth_analysis['성장률(%)'] = (
    (growth_analysis[2024] - growth_analysis[2022]) / growth_analysis[2022] * 100
)

print("\n상권별 성장률 분석")
print(growth_analysis.round(2))

# 시각화
fig, ax = plt.subplots(figsize=(10, 6))
growth_analysis['성장률(%)'].plot(kind='bar', ax=ax, color='#2ecc71')
ax.set_title('상권별 일반의원 성장률 (2022 vs 2024)', fontsize=14, fontweight='bold')
ax.set_ylabel('성장률 (%)')
ax.set_xlabel('')
ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(data_path + '../REPORT/성장률_분석.png', dpi=300, bbox_inches='tight')
plt.show()
```

---

## 5. 결과 리포트 작성 가이드

### 5.1 리포트 구성

1. **Executive Summary** (1페이지)
   - 분석 목적 및 방법론
   - 주요 발견사항 3가지
   - 최종 추천 입지 Top 3

2. **경쟁 환경 분석** (2-3페이지)
   - 상권별 의원 수 및 트렌드
   - 개폐업률 분석
   - 시장 포화도 평가

3. **타겟 고객 분석** (2-3페이지)
   - 여성/연령대별 매출 분석
   - 주중/주말 패턴 분석
   - 인구 구조 분석

4. **접근성 및 인프라** (1-2페이지)
   - 대중교통 접근성
   - 의료 인프라 현황
   - 유동인구 분석

5. **종합 평가 및 추천** (2페이지)
   - 평가 지표별 점수
   - 레이더 차트
   - 최종 추천 및 근거

### 5.2 시각화 체크리스트

- [x] 상권별 의원 점포 수 추이 그래프
- [x] 타겟층 매출 비중 비교 차트 (4개 차트)
- [x] 주중/주말 매출 비교 차트
- [x] 인구 구조 비교 차트
- [x] 접근성 및 의료 인프라 차트 (4개 차트)
- [x] 유동인구 분석 차트
- [x] 소득 및 의료비 지출 분석 차트
- [x] 종합 평가 레이더 차트
- [x] 유사 업종 비교 차트
- [x] 계절성 분석 차트
- [x] 성장률 분석 차트

### 5.3 결과물 저장

```python
# 분석 결과를 Excel로 저장
with pd.ExcelWriter(data_path + '../REPORT/피부과_입지분석_결과_V2_20260203.xlsx', 
                    engine='openpyxl') as writer:
    # 종합 평가
    evaluation_df.to_excel(writer, sheet_name='종합평가')
    
    # 타겟층 분석
    target_summary.to_excel(writer, sheet_name='타겟층분석')
    
    # 경쟁 환경
    churn_analysis.to_excel(writer, sheet_name='경쟁환경')
    
    # 주중/주말 패턴
    weekday_analysis.to_excel(writer, sheet_name='주중주말패턴')
    
    # 인구 구조
    latest_worker[['상권_코드_명', '총_직장_인구_수', '여성2040대_직장인구']].to_excel(
        writer, sheet_name='인구구조', index=False
    )
    
    # 소득 소비
    latest_income[['상권_코드_명', '월_평균_소득_금액', '의료비_지출_비중']].to_excel(
        writer, sheet_name='소득소비', index=False
    )
    
    # 접근성
    latest_facilities[['상권_코드_명', '지하철_역_수', '버스_정거장_수', '대중교통_접근성', '의료_인프라_점수']].to_excel(
        writer, sheet_name='접근성', index=False
    )
    
    # 유동인구
    floating_summary.to_excel(writer, sheet_name='유동인구')
    
    # 유사 업종 비교
    comparison.to_excel(writer, sheet_name='유사업종비교')

print("\n분석 결과가 Excel 파일로 저장되었습니다.")
```

---

## 6. 주의사항 및 제한사항

> [!WARNING]
> **데이터 해석 시 주의사항**

1. **일반의원 데이터의 한계**
   - 현재 데이터는 피부과만 분리되지 않고 "일반의원" 전체 카테고리로 집계됨
   - 실제 피부과 비중은 별도 조사 필요

2. **시계열 데이터 기간**
   - 2022년 1분기 ~ 2024년 4분기 데이터만 포함
   - 코로나19 영향이 일부 포함되어 있을 수 있음

3. **상권 범위**
   - 분석 대상이 강남구 5개 주요 상권으로 제한됨
   - 인근 상권과의 경쟁 관계는 고려되지 않음

4. **가중치 조정**
   - 종합 평가의 가중치는 예시이며, 실제 사업 전략에 맞게 조정 필요
   - 현재 설정: 경쟁강도(15%), 여성매출(12%), 2040대매출(12%), 직장인구(12%), 타겟인구(8%), 소득(8%), 접근성(13%), 의료인프라(10%), 유동인구(10%)

---

## 7. 참고 자료

### 7.1 업종 코드 매핑

| 코드 | 업종명 | 피부과 관련성 |
|------|--------|--------------|
| CS200006 | 일반의원 | ★★★★★ (피부과 포함) |
| CS200030 | 피부관리실 | ★★★★ (직접 경쟁업종) |

### 7.2 데이터 출처

- **서울시 상권분석서비스**: 서울 열린데이터광장
- **수집 기간**: 2022년 1분기 ~ 2024년 4분기
- **업데이트 주기**: 분기별

### 7.3 변경 이력

| 버전 | 날짜 | 주요 변경 사항 |
|------|------|---------------|
| 1.0 | 2026-02-03 | 초기 버전 작성 |
| 2.0 | 2026-02-03 | 유동인구 분석 추가, 의료 인프라 점수 종합 평가 반영, 주중/주말 패턴 분석 추가, 유사 업종을 피부관리실만으로 제한, 가중치 검증 로직 추가 |

---

**문서 버전**: 2.00  
**최종 수정일**: 2026-02-03  
**작성자**: EDA 분석팀
