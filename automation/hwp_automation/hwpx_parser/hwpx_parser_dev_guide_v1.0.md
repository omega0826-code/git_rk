# HWPX 파서 제작 가이드라인

> 버전: v1.0 | 작성일: 2026-02-19 | 최종 수정: 2026-02-19

---

## 1. 개요

본 문서는 HWPX 파일에서 텍스트, 표, 이미지, 제목을 자동 추출하는 Python 기반 파서 `hwpx_parser.py`의 개발 과정을 기술한다.

**대상 독자**: 파서를 유지보수하거나 확장하려는 개발자

---

## 2. 개발 환경

| 항목        | 내용                                 |
| ----------- | ------------------------------------ |
| Python      | 3.x (테스트: Python 3.11)            |
| OS          | Windows 10/11 (한글 환경)            |
| 필수 패키지 | `lxml`                               |
| 선택 패키지 | `pandas`, `openpyxl` (Excel 출력 시) |

```bash
pip install lxml pandas openpyxl
```

---

## 3. HWPX 파일 구조

HWPX는 ZIP 기반 XML 패키지이다. 핵심 파일:
- `Contents/section0.xml` — 본문 (문단, 표, 이미지)
- `Contents/header.xml` — 스타일 정의 (글꼴, 크기 등)
- `BinData/` — 임베디드 이미지

> 상세 구조는 `hwpx_guideline.md`의 1~3장 참조

---

## 4. 모듈 아키텍처

### 4.1 당초 계획 vs 실제 구현

| 구분         | 당초 계획 (가이드라인 4.1)       | 실제 구현                       | 변경 사유                    |
| ------------ | -------------------------------- | ------------------------------- | ---------------------------- |
| ZIP/XML 로드 | `HwpxReader`                     | `HwpxReader` ✅                  | 계획대로                     |
| 문단 파싱    | `SectionParser._parse_paragraph` | `TextExtractor` (독립 클래스)   | 역할 분리로 재사용성 향상    |
| 표 파싱      | `SectionParser._parse_table`     | `TableExtractor` ✅              | 계획대로                     |
| 이미지 파싱  | `SectionParser._parse_image`     | `ImageExtractor` (신규 클래스)  | 이미지 추출+저장 로직 분리   |
| 제목 감지    | `SectionParser._detect_headings` | `HeadingDetector` (신규 클래스) | 독립 유틸리티로 활용도 증가  |
| 결과 저장    | (미계획)                         | `OutputWriter` (신규 클래스)    | 다양한 출력 형식 관리 필요   |
| 원스톱 함수  | `convert()`                      | `parse_hwpx()`                  | 함수명 변경, 기능 동일       |
| 병합 처리    | `TableExtractor._resolve_spans`  | `extract_all()` 내부 로직       | 별도 메서드 대신 인라인 처리 |

### 4.2 최종 클래스 다이어그램

```
hwpx_parser.py (872줄)
│
├── HwpxReader          # ZIP 해제 + XML 로드
│   ├── __init__()      # 파일 검증 + ZIP 열기
│   ├── read_xml()      # 내부 XML 파싱
│   ├── read_binary()   # 바이너리 파일 읽기
│   ├── get_section_roots()  # 모든 section XML
│   ├── get_header()    # header.xml
│   └── get_bin_data_list()  # BinData/ 목록
│
├── TextExtractor       # 텍스트 추출
│   ├── extract_paragraph_text()  # 단일 문단
│   ├── is_in_table()   # 표 내부 여부 확인
│   ├── is_in_header_footer()  # 머리말/꼬리말 여부
│   ├── extract_all()   # 전체 텍스트
│   └── extract_by_heading()  # 제목별 분리
│
├── HeadingDetector      # 제목 감지
│   ├── STYLE_LEVEL_MAP  # styleIDRef → 레벨 매핑
│   └── detect()         # titleMark 기반 감지
│
├── TableExtractor       # 표 추출 (셀 병합 처리)
│   ├── _is_body_table()       # 본문 표 필터링
│   ├── _get_cell_text()       # 셀 텍스트 추출
│   ├── _guess_table_title()   # 표 제목 추측
│   ├── extract_all()          # 전체 표 추출
│   └── to_dataframe()         # DataFrame 변환
│
├── ImageExtractor       # 이미지 추출
│   ├── extract_image_refs()   # 이미지 참조 목록
│   └── extract_images()       # 실제 파일 저장
│
├── OutputWriter         # 결과물 저장
│   ├── write_full_text_md()   # Markdown
│   ├── write_full_text_txt()  # Plain Text
│   ├── write_headings_json()  # JSON
│   ├── write_table_csv()      # 개별 CSV
│   ├── write_all_tables_csv() # 전체 CSV
│   ├── write_all_tables_excel() # Excel
│   └── write_parse_log()      # 파싱 로그
│
├── parse_hwpx()         # 원스톱 파싱 함수
└── main()               # CLI 진입점
```

---

## 5. 핵심 파싱 로직

### 5.1 네임스페이스
```python
NS = {
    'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
    'hs': 'http://www.hancom.co.kr/hwpml/2011/section',
    'hc': 'http://www.hancom.co.kr/hwpml/2011/core',
    'hh': 'http://www.hancom.co.kr/hwpml/2011/head',
    'ha': 'http://www.hancom.co.kr/hwpml/2011/app',
}
```

### 5.2 텍스트 추출
- `hp:p` → `hp:run` → `hp:t`의 `.text` 수집
- 표/머리말/꼬리말 내부 문단은 `getparent()` 순회로 필터링

### 5.3 표 추출 (셀 병합)
- `hp:tbl`의 `rowCnt`, `colCnt`로 2D 그리드 초기화
- `hp:tc > hp:cellAddr`로 위치, `hp:cellSpan`으로 병합 범위 파악
- `occupied` 배열로 중복 방지

### 5.4 제목 감지
- `hp:titleMark` 존재 여부로 제목 판별
- `styleIDRef`로 헤딩 레벨 매핑 (1=개요1, 2=개요2 등)

### 5.5 이미지 추출
- `hp:pic > hc:img`의 `binaryItemIDRef`로 `BinData/` 파일 매핑
- 원본 포맷(bmp/png/jpg/wmf) 그대로 저장

---

## 6. 출력 디렉토리 및 파일명 규칙

> `hwpx_guideline.md` 4.3절 참조

---

## 7. 테스트 방법

```bash
# 표 개수 확인
python hwpx_parser.py <파일>.hwpx --count-tables

# 텍스트만 출력
python hwpx_parser.py <파일>.hwpx --text-only

# 특정 표 CSV 추출
python hwpx_parser.py <파일>.hwpx --extract-table 1 --output table1.csv

# 전체 추출
python hwpx_parser.py <파일>.hwpx
```

---

## 8. 알려진 제한사항

1. 표 제목 추측 로직이 일부 표에서 실패 (표 위 문단이 없는 경우)
2. `styleIDRef=0`인 소제목이 본문과 구분 어려움
3. BMP 이미지 대용량 (최대 25MB) — 자동 변환 미지원
4. 다중 섹션(`section1.xml` 등) 테스트 미완

---

## 9. 업데이트 내역

| 버전 | 날짜       | 작성자 | 변경 내용      |
| ---- | ---------- | ------ | -------------- |
| v1.0 | 2026-02-19 | -      | 초기 버전 작성 |
