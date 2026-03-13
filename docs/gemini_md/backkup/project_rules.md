# 프로젝트별 규칙: 강남구 병원 경쟁 및 리뷰 분석

> **프로젝트 코드명**: `gangnam_hospital_analysis`

이 문서는 **강남구 병원 데이터 분석** 프로젝트에 특화된 규칙을 정의합니다. `gemini.md`의 글로벌 표준을 따르되, 본 문서의 내용이 우선합니다.

## 1. 프로젝트 개요
- **프로젝트명**: 강남구 병원 경쟁 및 리뷰 분석 (Gangnam Hospital Analysis)
- **프로젝트 코드**: `gangnam_hospital_analysis`
- **목적**: 강남구 소재 병원/의원의 현황을 파악하고, 리뷰 데이터를 통해 환자 경험 및 경쟁 우위를 분석합니다.

## 2. 파일 및 디렉토리 구조
`crawling/gangnam` 디렉토리를 메인으로 사용합니다.

### 2.1 파일명 규칙 (Naming Convention)

#### 타임스탬프 포맷 (필수)
모든 생성 파일은 **파일명 끝에 생성 시간**을 포함해야 합니다.
- **포맷**: `{파일명}_{YYYYMMDD_HHMMSS}.{확장자}`
- **예시**: 
  - `gangnam_hospitals_20260110_174500.csv`
  - `report_analysis_20260110_174500.md`
  - `eda_result_20260110_174500.png`

#### 파일 유형별 규칙
- **원본 데이터 (Raw)**: `gangnam_hospitals_YYYYMMDD_HHMMSS.csv`
- **가공 데이터 (Processed)**:
    - 최종 통합본: `gangnam_hospitals_final_YYYYMMDD_HHMMSS.csv`
    - 필터링본: `{설명}_filtered_YYYYMMDD_HHMMSS.csv`
    - 리뷰 데이터: `reviews_year/` 폴더 내 연도별 저장
- **리포트 파일**: `report_{분석명}_YYYYMMDD_HHMMSS.md`
- **시각화 파일**: `{차트명}_YYYYMMDD_HHMMSS.png`

#### 주의사항
- 타임스탬프는 24시간 형식 사용 (HH: 00-23)
- 파일명에 공백 사용 금지 (언더스코어 `_` 사용)
- 한글 파일명 가능하나 영문 권장

### 2.2 디렉토리 역할
- `scripts/`: 데이터 수집(Crawling) 및 전처리(ETL) 파이썬 스크립트
- `reports/`: 분석 결과 리포트
  - `reports/errors/`: 에러 관련 리포트 전용 (크롤링 에러, 데이터 품질 이슈 등)
  - `reports/analysis/`: 분석 결과 리포트
- `docs/`: 프로젝트 가이드라인 및 매뉴얼
- `data/`: `raw`, `processed`, `archive`로 구분 관리

## 3. 기술 스택 및 도구 (Tech Stack)
- **수집**: `selenium`, `beautifulsoup4` 사용. 동적 페이지 처리가 많음.
- **데이터 처리**: `pandas` (주요), `polars` (대용량 데이터 처리 시 검토 가능)
- **텍스트 분석**: `konlpy` (Mecab 권장), `wordcloud` 등 한국어 자연어 처리
- **시각화**: `matplotlib`, `seaborn` (Windows 환경 한글 폰트 설정 필수)

## 4. 도메인 로직 및 주의사항
- **병원 vs 의원**: 데이터 분석 시 '병원'급과 '의원'급을 명확히 구분해야 합니다.
- **개인정보**: 리뷰 데이터 내의 사용자 이름이나 개인 식별 정보는 반드시 마스킹 처리합니다.
- **지역 제한**: 분석 대상은 주로 '서울시 강남구'로 한정되나, 비교군으로 타 지역이 포함될 수 있음을 유의합니다.
