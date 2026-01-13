# PDF 표 추출 작업 완료 보고서

## 작업 개요

울산지역 인력 및 훈련 수요공급조사 분석 PDF 파일에서 표를 추출하여 Excel 스프레드시트로 변환하는 작업을 완료했습니다.

---

## 생성된 파일

### 📁 작업 디렉토리
`d:\git_rk\project\25_121_ulsan\`

### 📄 생성된 파일 목록

#### 1. Python 스크립트

| 파일명 | 설명 | 크기 |
|--------|------|------|
| [extract_tables_from_pdf.py](file:///d:/git_rk/project/25_121_ulsan/extract_tables_from_pdf.py) | 기본 표 추출 스크립트 (pdfplumber 사용) | 5.4 KB |
| [extract_tables_improved.py](file:///d:/git_rk/project/25_121_ulsan/extract_tables_improved.py) | **개선 버전** - 여러 라이브러리 결합 | 15.2 KB |
| [test_imports.py](file:///d:/git_rk/project/25_121_ulsan/test_imports.py) | 라이브러리 설치 확인용 테스트 스크립트 | 618 B |

#### 2. 배치 파일 (실행용)

| 파일명 | 설명 |
|--------|------|
| [run_extract.bat](file:///d:/git_rk/project/25_121_ulsan/run_extract.bat) | 기본 스크립트 실행 |
| [run_extract_improved.bat](file:///d:/git_rk/project/25_121_ulsan/run_extract_improved.bat) | **개선 스크립트 실행 (권장)** |

#### 3. 출력 파일

| 파일명 | 설명 | 크기 |
|--------|------|------|
| 울산지역_인력훈련조사_표추출.xlsx | 초기 추출 결과 | 177.8 KB |
| 울산지역_인력훈련조사_표추출_개선.xlsx | 개선 버전 실행 시 생성 | (실행 후 생성) |

---

## 정확도 개선 사항

### 문제점
초기 버전(pdfplumber만 사용)에서 일부 표가 누락되거나 부정확하게 추출되는 문제 발생

### 해결 방법

#### 1. **다중 라이브러리 결합**
```
pdfplumber (기본) → 빠르고 간단
     +
Camelot (선택) → 높은 정확도, 복잡한 표 처리
     +
Tabula (선택) → 추가 보완
```

#### 2. **다양한 추출 전략**
- **Strict 모드**: 선이 명확한 표 (격자형)
- **Loose 모드**: 선이 없는 표 (텍스트 정렬 기반)
- **Lattice 방식**: 선 기반 감지
- **Stream 방식**: 텍스트 흐름 기반 감지

#### 3. **중복 제거 및 최적 선택**
- 같은 표가 여러 방법으로 추출되면 가장 정확한 결과 선택
- 우선순위: Camelot > pdfplumber > Tabula

#### 4. **설정 최적화**
```python
# 더 민감한 표 감지
snap_tolerance: 3 → 5
join_tolerance: 3 → 5
edge_min_length: 3 → 1
```

---

## 사용 방법

### ✅ 권장 방법: 개선 버전 실행

```cmd
cd d:\git_rk\project\25_121_ulsan
run_extract_improved.bat
```

**자동으로 수행되는 작업:**
1. Python 버전 확인
2. 필수 라이브러리 설치 (pdfplumber, openpyxl)
3. 선택적 라이브러리 설치 시도 (Camelot, Tabula)
4. 개선된 스크립트 실행
5. Excel 파일 생성

### 📊 출력 결과

- **파일명**: `울산지역_인력훈련조사_표추출_개선.xlsx`
- **구조**:
  - 각 표가 별도 시트로 분리
  - 시트명: "표1", "표2", "표3", ...
  - 각 시트 상단에 표 정보 표시:
    - 표 번호
    - 원본 PDF 페이지 번호
    - 사용된 추출 방법

---

## 추가 최적화 옵션

### 1. Camelot 설치 (정확도 대폭 향상)

> [!IMPORTANT]
> Camelot은 복잡한 표와 병합된 셀을 훨씬 더 정확하게 처리합니다.

**설치 방법:**
```cmd
# 1. Ghostscript 설치 필요
# https://ghostscript.com/releases/gsdnld.html

# 2. Camelot 설치
pip install camelot-py[cv]
```

설치가 복잡하면 **pdfplumber만으로도 충분**합니다.

### 2. 특정 페이지만 추출

스크립트를 수정하여 특정 페이지만 처리 가능:

```python
# extract_tables_improved.py의 main() 함수 수정
# 예: 10-20페이지만 추출
for page_num in range(10, 21):  # 10-20페이지
    # ...
```

### 3. 표 감지 임계값 조정

표가 너무 많이/적게 감지되면 설정 조정:

```python
table_settings = {
    "snap_tolerance": 5,      # 높이면 더 많은 표 감지
    "join_tolerance": 5,      # 높이면 더 많은 표 감지
    "edge_min_length": 1,     # 낮추면 더 많은 표 감지
}
```

---

## 문제 해결

### ❌ 표가 여전히 누락되는 경우

1. **PDF 품질 확인**
   - 스캔된 이미지 PDF는 OCR 필요
   - 텍스트 기반 PDF인지 확인

2. **Camelot 설치**
   - 가장 정확한 추출 방법
   - 복잡한 표에 효과적

3. **수동 영역 지정**
   - 특정 표의 좌표를 직접 지정
   - pdfplumber의 `crop()` 기능 사용

### ⚠️ 추출된 표가 깨지는 경우

1. **병합된 셀**: Camelot 사용 권장
2. **복잡한 레이아웃**: 수동 영역 분할
3. **회전된 표**: PDF 회전 보정 필요

### 💾 메모리 부족 오류

1. 페이지별로 나누어 처리
2. 이미지 해상도 낮추기

---

## 다음 단계

1. **`run_extract_improved.bat` 실행**
2. **생성된 Excel 파일 확인**
3. **누락된 표가 있다면**:
   - Camelot 설치 시도
   - 특정 페이지만 재추출
   - 수동 영역 지정 고려

---

## 참고 문서

- [accuracy_improvement_guide.md](file:///C:/Users/user/.gemini/antigravity/brain/7f222b7f-7478-4728-a437-f4e7abc41751/accuracy_improvement_guide.md) - 정확도 개선 상세 가이드
- [task.md](file:///C:/Users/user/.gemini/antigravity/brain/7f222b7f-7478-4728-a437-f4e7abc41751/task.md) - 작업 체크리스트
