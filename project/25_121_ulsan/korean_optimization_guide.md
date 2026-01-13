# 한글 인식 정확도 개선 가이드

## 문제점
PDF에서 표를 추출할 때 한글 텍스트가 부정확하게 인식되는 문제가 발생했습니다.

### 주요 원인
1. **문자 간격 인식**: 한글은 영문보다 문자 간격이 넓어 기본 설정으로는 별도 셀로 분리될 수 있음
2. **텍스트 정렬**: 한글 폰트의 특성상 수평/수직 정렬 감지가 어려움
3. **선 감지**: 한글 문서에서 표 경계선이 얇거나 불명확한 경우 많음

---

## 개선 방법

### 1. 다중 추출 전략 적용

기존에는 2가지 전략만 사용했지만, 이제 **4가지 전략**을 모두 시도합니다:

| 전략 | 설명 | 한글 적합도 |
|------|------|------------|
| **lines** | 선 기반 감지 (기본) | ⭐⭐⭐⭐ |
| **lines_strict** | 선 엄격 모드 | ⭐⭐⭐ |
| **text** | 텍스트 정렬 기반 | ⭐⭐⭐⭐⭐ (한글 최적) |
| **explicit** | 명시적 선 감지 | ⭐⭐⭐ |

### 2. 한글 최적화 설정값

#### Text 전략 (한글에 가장 효과적)
```python
{
    "vertical_strategy": "text",
    "horizontal_strategy": "text",
    "snap_tolerance": 6,        # 기본 3 → 6 (한글 문자 간격 고려)
    "join_tolerance": 6,        # 기본 3 → 6
    "text_tolerance": 3,        # 텍스트 정렬 허용 오차
    "text_x_tolerance": 3,      # 수평 정렬 허용 오차
    "text_y_tolerance": 3,      # 수직 정렬 허용 오차
}
```

**주요 변경 사항:**
- `snap_tolerance`, `join_tolerance`: 3 → 6으로 증가
  - 한글 문자 간 간격이 넓어도 같은 셀로 인식
- `text_tolerance` 추가: 텍스트 정렬 감지 정확도 향상

#### Lines 전략
```python
{
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "snap_tolerance": 3,
    "join_tolerance": 3,
    "edge_min_length": 3,
    "intersection_tolerance": 3,
}
```

### 3. 데이터 정제 개선

#### 제어 문자 제거
```python
# 기존: 단순 None 체크
cleaned_row = [cell if cell is not None else "" for cell in row]

# 개선: 제어 문자 제거 + 공백 정리
cleaned_cell = ''.join(char for char in cell_str 
                       if ord(char) >= 32 or char in '\t\n\r')
cleaned_cell = ' '.join(cleaned_cell.split())  # 연속 공백 제거
```

### 4. 한글 가중치 열 너비 계산

```python
# 한글 문자 수 계산 (유니코드 범위: 0xAC00-0xD7A3)
korean_count = sum(1 for char in cell_value 
                   if ord(char) >= 0xAC00 and ord(char) <= 0xD7A3)
english_count = len(cell_value) - korean_count

# 한글은 1.5배 가중치 적용
effective_length = korean_count * 1.5 + english_count
```

**효과:**
- 한글이 포함된 열의 너비가 적절하게 조정됨
- 텍스트 잘림 현상 방지

---

## 사용 방법

### 실행 명령
```cmd
cd d:\git_rk\project\25_121_ulsan
python extract_korean_optimized.py
```

### 출력 파일
- **파일명**: `울산지역_인력훈련조사_표추출_한글최적화.xlsx`
- **특징**:
  - 각 시트에 사용된 추출 방법 표시
  - 한글 텍스트 인식 정확도 향상
  - 열 너비 자동 조정 (한글 가중치 적용)

---

## 추가 최적화 팁

### 1. 특정 전략만 사용하기

특정 전략이 가장 잘 작동한다면 해당 전략만 사용하도록 수정:

```python
# extract_korean_optimized.py에서
# 다른 전략들을 주석 처리하고 원하는 전략만 남김
strategies = [
    {
        'name': 'text',  # 한글에 가장 효과적
        'settings': {
            "vertical_strategy": "text",
            "horizontal_strategy": "text",
            # ...
        }
    }
]
```

### 2. 허용 오차 값 조정

표가 여전히 부정확하게 추출되면 허용 오차 값을 조정:

```python
# 더 느슨하게 (더 많은 텍스트를 같은 셀로 인식)
"snap_tolerance": 8,  # 6 → 8
"join_tolerance": 8,

# 더 엄격하게 (텍스트를 더 세밀하게 분리)
"snap_tolerance": 4,  # 6 → 4
"join_tolerance": 4,
```

### 3. 특정 페이지만 처리

문제가 있는 페이지만 재추출:

```python
# extract_korean_optimized.py 수정
for page_num, page in enumerate(pdf.pages, start=1):
    if page_num not in [5, 10, 15]:  # 5, 10, 15 페이지만 처리
        continue
    # ...
```

---

## 비교: 기존 vs 개선

| 항목 | 기존 | 개선 |
|------|------|------|
| 추출 전략 | 2개 (strict, loose) | 4개 (lines, lines_strict, text, explicit) |
| 한글 간격 허용 | 3-5 | 6 (text 전략) |
| 텍스트 정렬 감지 | 없음 | 3가지 tolerance 추가 |
| 열 너비 계산 | 단순 문자 수 | 한글 1.5배 가중치 |
| 공백 처리 | 없음 | 연속 공백 제거 |
| 제어 문자 처리 | 기본 | 향상된 필터링 |

---

## 예상 개선 효과

✅ **한글 텍스트 인식률 향상**
- 문자 간격이 넓은 한글도 정확히 인식
- 텍스트 정렬 기반 감지로 선이 없는 표도 추출

✅ **데이터 품질 향상**
- 연속 공백 제거로 깔끔한 데이터
- 제어 문자 완전 제거

✅ **가독성 향상**
- 한글 가중치 적용으로 적절한 열 너비
- 각 시트에 추출 방법 표시로 품질 확인 가능
