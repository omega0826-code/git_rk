# 향후 분석 전략 제언 (Next Step Analysis Strategy)

본 문서는 `gangnam_reviews.parquet` 데이터에 대한 EDA 결과를 바탕으로, 향후 더 심도 깊은 인사이트 도출과 서비스 적용을 위한 기술적 실행 전략을 제시합니다.

---

## 1. 데이터 정제 고도화 (Refinement)

### 현상 및 문제점
- **평점 스케일 불일치**: 초기 가이드라인은 1~5점 척도를 권장했으나, 실제 데이터에는 0~10점까지 분포함.
- **데이터 상한선 의심**: 상위 병원들의 리뷰 수가 정확히 10,000건으로 집계되는 현상이 발견됨 (데이터 수집 상의 Cap 또는 인위적 분포 가능성).

### 실행 전략
1. **Rating Normalization**: 10점 만점 데이터를 5점 척도로 변환하거나, 분석 목적에 맞춰 구간화(Binning) 필요.
    - 예: `0~4` → `1 (부정)`, `5~7` → `3 (보통)`, `8~10` → `5 (긍정)`
2. **이상치 제거**: 리뷰 길이가 비정상적으로 짧거나(초성만 존재), 중복된 내용 제거.

---

## 2. 심층 NLP 분석 (Advanced NLP)

### 목표
단순 키워드 빈도 분석을 넘어, "왜" 만족/불만족했는지 구체적인 원인을 파악.

### 실행 전략
1. **형태소 분석기 도입 (Mecab/KoNLPy)**:
    - 단순 띄어쓰기 기준(`split`)이 아닌, 한국어 특성에 맞는 형태소 분석 적용.
    - 명사(Noun), 형용사(Adjective), 동사(Verb) 위주로 추출하여 의미 분석 강화.
2. **Topic Modeling (BERTopic)**:
    - **부정 리뷰(Low Rating)** 내에서 주요 토픽 추출 (예: "대기시간", "불친절", "부작용", "비용").
    - **긍정 리뷰(High Rating)** 내 주요 소구점 파악 (예: "시설", "원장님 실력", "접근성").
3. **Aspect-Based Sentiment Analysis (ABSA)**:
    - 문장 내에서 속성(Aspect)과 감성(Sentiment)을 연결.
    - 예: "시설은 좋은데 가격이 비싸요" → `{시설: 긍정, 가격: 부정}`

---

## 3. 어뷰징 및 가짜 리뷰 탐지 (Anomaly Detection)

### 목표
신뢰도 높은 병원 추천을 위해 광고성/조작 의심 리뷰 필터링.

### 실행 전략
1. **시간적 이상 패턴 감지**:
    - 특정 병원에 단기간(예: 1일)에 리뷰가 폭증한 구간 탐지.
2. **텍스트 유사도 분석**:
    - `TF-IDF` 또는 `Embedding`을 활용하여 내용이 90% 이상 유사한 "복붙" 리뷰 군집 탐지.
3. **헤비 업로더 분석**:
    - 특정 닉네임이 비정상적으로 많은 병원에 리뷰를 남겼는지 확인.

---

## 4. 병원 추천 시스템 프로토타입 (Recommendation)

### 목표
사용자 맞춤형 병원/시술 추천.

### 실행 전략
1. **컨텐츠 기반 필터링 (Content-based)**:
    - 사용자가 관심 있는 "시술명(예: 라식)"과 "선호 요소(예: 친절함, 저렴함)"를 입력하면, 해당 키워드의 긍정 리뷰 비율이 높은 병원 추천.
2. **태그 클라우드 생성**:
    - 병원별 대표 키워드(태그)를 자동 생성하여 사용자에게 직관적인 정보 제공. (예: `#대기시간짧음`, `#꼼꼼한상담`)

---

## 5. 제안 아키텍처 (Proposed Architecture)

```
[Data Source] (Parquet)
      ↓
[Preprocessing Module] (Python/Pandas/KoNLPy)
  - Rating Scaling
  - Morphological Analysis
      ↓
[Analysis Module]
  - Topic Modeling (BERTopic)
  - Anomaly Detection (Scikit-learn)
      ↓
[Dashboard/Serving] (Streamlit or FastAPI)
  - Hospital Search & Compare
  - Review Summary Dashboard
```
