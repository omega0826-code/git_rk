# HWPX 파싱 가이드라인

> 대상 파일: `TEST_MISS_1.hwpx` (3.5MB, 「2025년도 경북RSC 기초조사 보고서」)

---

## 목차

1. [HWPX 파일 구조 개요](#1-hwpx-파일-구조-개요)
2. [핵심 XML 네임스페이스](#2-핵심-xml-네임스페이스)
3. [section0.xml 핵심 요소 분석](#3-section0xml-핵심-요소-분석)
   - 3.1 문단 (`hp:p`)
   - 3.2 표 (`hp:tbl`)
   - 3.3 이미지 (`hp:pic`)
   - 3.4 제목/헤딩 표시 (`hp:titleMark`)
   - 3.5 그룹 객체 (`hp:container`)
   - 3.6 머리말/꼬리말 (`hp:header`)
   - 3.7 페이지 속성 (`hp:secPr`, `hp:pagePr`)
4. [파싱 계획 (Python)](#4-파싱-계획-python)
   - 4.1 아키텍처
   - 4.2 핵심 파싱 로직
   - 4.3 출력 디렉토리 구조 및 파일명 규칙
   - 4.4 출력 형식 옵션
   - 4.5 주의사항 및 엣지 케이스
5. [검증 계획](#5-검증-계획)
6. [파서 실행 결과](#6-파서-실행-결과)
7. [산출물 보고서](#7-산출물-보고서)
   - 7.1 보고서 목록
   - 7.2 보고서 버전 규칙
   - 7.3 보고서 공통 구조
   - 7.4 각 보고서 상세 목차
   - 7.5 보고서 저장 위치
8. [표별 출처 추출 결과](#8-표별-출처-추출-결과)
9. [추후 개발 계획](#9-추후-개발-계획)
10. [업데이트 내역](#10-업데이트-내역)

---

## 1. HWPX 파일 구조 개요

HWPX는 **ZIP 기반 XML 패키지** 포맷이다. 압축 해제하면 다음 구조가 나타난다:

```
sample.hwpx (ZIP)
├── mimetype                     # 파일 타입 선언
├── version.xml                  # HWPX 버전 정보
├── settings.xml                 # 문서 설정
├── Contents/
│   ├── header.xml               # 문서 헤더 (글꼴, 스타일, 테두리 등 정의)
│   ├── section0.xml             # ★ 본문 (문단·표·이미지 등 실제 콘텐츠)
│   ├── content.hpf              # 콘텐츠 매니페스트
│   ├── masterpage0.xml          # 마스터페이지 (짝수 페이지)
│   └── masterpage1.xml          # 마스터페이지 (홀수 페이지)
├── BinData/
│   ├── image1.bmp ~ image34.wmf # 임베디드 이미지 (bmp/png/jpg/wmf)
│   └── ole35.ole                # OLE 객체
├── Preview/
│   ├── PrvText.txt              # 미리보기 텍스트
│   └── PrvImage.png             # 미리보기 이미지
└── META-INF/
    ├── container.xml            # OPF 컨테이너
    ├── container.rdf            # 메타데이터
    └── manifest.xml             # 전체 파일 목록
```

---

## 2. 핵심 XML 네임스페이스

| 접두사 | URI                                            | 용도                     |
| ------ | ---------------------------------------------- | ------------------------ |
| `hp`   | `http://www.hancom.co.kr/hwpml/2011/paragraph` | 문단, 텍스트, 표, 이미지 |
| `hs`   | `http://www.hancom.co.kr/hwpml/2011/section`   | 섹션 루트                |
| `hc`   | `http://www.hancom.co.kr/hwpml/2011/core`      | 이미지(img), 행렬        |
| `hh`   | `http://www.hancom.co.kr/hwpml/2011/head`      | 헤더 메타정보            |
| `ha`   | `http://www.hancom.co.kr/hwpml/2011/app`       | 앱 정보                  |

---

## 3. section0.xml 핵심 요소 분석

### 3.1 문단 (`hp:p`)
```xml
<hp:p id="..." paraPrIDRef="..." styleIDRef="..." pageBreak="0|1">
  <hp:run charPrIDRef="...">
    <hp:t>텍스트 내용</hp:t>
  </hp:run>
</hp:p>
```
- `hp:p` = 하나의 문단
- `hp:run` = 문단 내 텍스트 런 (서식 단위)
- `hp:t` = 실제 텍스트 콘텐츠
- `pageBreak="1"` = 페이지 나눔
- `paraPrIDRef` = 문단 스타일 ID 참조 (header.xml에 정의)
- `charPrIDRef` = 문자 스타일 ID 참조

### 3.2 표 (`hp:tbl`)
```xml
<hp:tbl id="..." rowCnt="9" colCnt="9" cellSpacing="0" borderFillIDRef="28">
  <hp:sz width="42330" height="18764"/>
  <hp:tr>                              <!-- 행 (table row) -->
    <hp:tc borderFillIDRef="23">       <!-- 셀 (table cell) -->
      <hp:subList vertAlign="CENTER">
        <hp:p>
          <hp:run><hp:t>구분</hp:t></hp:run>
        </hp:p>
      </hp:subList>
      <hp:cellAddr colAddr="0" rowAddr="0"/>
      <hp:cellSpan colSpan="1" rowSpan="2"/>  <!-- 셀 병합 -->
      <hp:cellSz width="7223" height="2930"/>
    </hp:tc>
  </hp:tr>
</hp:tbl>
```
- `rowCnt`, `colCnt` = 행·열 개수
- `hp:cellSpan` = 셀 병합 정보 (`colSpan`, `rowSpan`)
- `hp:cellAddr` = 셀의 논리적 위치 (`colAddr`, `rowAddr`)
- `hp:cellSz` = 셀 크기
- 텍스트는 `hp:tc > hp:subList > hp:p > hp:run > hp:t` 경로

### 3.3 이미지 (`hp:pic`)
```xml
<hp:pic id="..." numberingType="PICTURE" textWrap="TOP_AND_BOTTOM">
  <hp:orgSz width="19140" height="2280"/>
  <hp:curSz width="25748" height="3066"/>
  <hc:img binaryItemIDRef="image3"/>  <!-- BinData/ 참조 -->
  <hp:shapeComment>그림입니다. ...</hp:shapeComment>
</hp:pic>
```
- `hc:img binaryItemIDRef` = `BinData/` 폴더 내 파일명 참조
- `hp:orgSz` / `hp:curSz` = 원본·현재 크기
- `hp:shapeComment` = 이미지 설명 (선택적)

### 3.4 제목/헤딩 표시 (`hp:titleMark`)
```xml
<hp:t>1. 경북지역 산업 현황 분석<hp:titleMark ignore="1"/></hp:t>
```
- `hp:titleMark` = 목차·개요에서 사용되는 제목 마커
- `styleIDRef`로 헤딩 레벨 구분 (1=개요1, 2=개요2, 7=캡션 등)

### 3.5 그룹 객체 (`hp:container`)
```xml
<hp:container id="..." textWrap="BEHIND_TEXT">
  <hp:pic>...</hp:pic>     <!-- 배경 이미지 -->
  <hp:rect>...</hp:rect>   <!-- 텍스트 상자 -->
  <hp:shapeComment>묶음 개체입니다.</hp:shapeComment>
</hp:container>
```
- 이미지 + 텍스트 상자 등을 묶은 그룹 객체

### 3.6 머리말/꼬리말 (`hp:header`)
```xml
<hp:header id="7" applyPageType="ODD">
  <hp:subList>
    <hp:p><hp:run><hp:t>1장 경북지역 산업 및 고용 현황</hp:t></hp:run></hp:p>
  </hp:subList>
</hp:header>
```
- `applyPageType` = `ODD`(홀수 페이지), `EVEN`(짝수 페이지)

### 3.7 페이지 속성 (`hp:secPr`, `hp:pagePr`)
```xml
<hp:pagePr landscape="WIDELY" width="59528" height="84188">
  <hp:margin header="4251" footer="4251" left="8503" right="8503" top="5669" bottom="4251"/>
</hp:pagePr>
```
- 페이지 크기, 여백, 방향 등

---

## 4. 파싱 계획 (Python)

### 4.1 아키텍처

> v1.4 반영: 실제 구현 기준 (당초 계획 대비 변경점은 아래 표 참조)

```
hwpx_parser.py (872줄)
├── HwpxReader          # ZIP 해제 + XML 로드
├── TextExtractor       # 텍스트 추출 (표/머리말 필터링)
├── HeadingDetector     # 제목 감지 (titleMark + styleIDRef)
├── TableExtractor      # 표 추출 (셀 병합 처리)
├── ImageExtractor      # 이미지 참조 추출 + 파일 저장
├── OutputWriter        # Markdown/TXT/CSV/Excel/JSON 저장
├── parse_hwpx()        # 원스톱 파싱 함수
└── main()              # CLI 진입점
```

#### 당초 계획 대비 변경점

| 구분        | 당초 계획                      | 실제 구현                           | 사유                  |
| ----------- | ------------------------------ | ----------------------------------- | --------------------- |
| 문단/제목   | `SectionParser` (통합 클래스)  | `TextExtractor` + `HeadingDetector` | 역할 분리, 재사용성   |
| 이미지      | `SectionParser._parse_image`   | `ImageExtractor` (독립 클래스)      | 추출+저장 로직 분리   |
| 결과 저장   | (미계획)                       | `OutputWriter` (신규)               | 다양한 출력 형식 관리 |
| 원스톱 함수 | `convert()`                    | `parse_hwpx()`                      | 함수명 변경           |
| 병합 처리   | `_resolve_spans()` 별도 메서드 | `extract_all()` 내부 로직           | 인라인 처리로 간결화  |

### 4.2 핵심 파싱 로직

#### Step 1: ZIP 해제 + XML 로드
```python
import zipfile
from lxml import etree

NS = {
    'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
    'hs': 'http://www.hancom.co.kr/hwpml/2011/section',
    'hc': 'http://www.hancom.co.kr/hwpml/2011/core',
    'hh': 'http://www.hancom.co.kr/hwpml/2011/head',
}

with zipfile.ZipFile("sample.hwpx", "r") as z:
    section_xml = z.read("Contents/section0.xml")
    root = etree.fromstring(section_xml)
```

#### Step 2: 텍스트 추출
```python
def extract_text(root):
    """모든 hp:p 요소에서 텍스트를 추출한다."""
    paragraphs = []
    for p in root.iter(f'{{{NS["hp"]}}}p'):
        texts = []
        for t in p.iter(f'{{{NS["hp"]}}}t'):
            if t.text:
                texts.append(t.text)
        if texts:
            paragraphs.append(''.join(texts))
    return paragraphs
```

#### Step 3: 표 추출 (셀 병합 처리 포함)
```python
def extract_tables(root):
    """모든 hp:tbl에서 표 데이터를 추출한다."""
    tables = []
    for tbl in root.iter(f'{{{NS["hp"]}}}tbl'):
        row_cnt = int(tbl.get('rowCnt', 0))
        col_cnt = int(tbl.get('colCnt', 0))
        
        # 2D 배열 초기화
        grid = [['' for _ in range(col_cnt)] for _ in range(row_cnt)]
        occupied = [[False]*col_cnt for _ in range(row_cnt)]
        
        for tc in tbl.iter(f'{{{NS["hp"]}}}tc'):
            addr = tc.find(f'{{{NS["hp"]}}}cellAddr')
            span = tc.find(f'{{{NS["hp"]}}}cellSpan')
            col = int(addr.get('colAddr', 0))
            row = int(addr.get('rowAddr', 0))
            cs = int(span.get('colSpan', 1))
            rs = int(span.get('rowSpan', 1))
            
            # 셀 텍스트 추출
            cell_texts = []
            for t in tc.iter(f'{{{NS["hp"]}}}t'):
                if t.text:
                    cell_texts.append(t.text)
            cell_value = ' '.join(cell_texts)
            
            # 병합 영역에 값 배치
            for r in range(row, min(row+rs, row_cnt)):
                for c in range(col, min(col+cs, col_cnt)):
                    if not occupied[r][c]:
                        grid[r][c] = cell_value if (r==row and c==col) else ''
                        occupied[r][c] = True
        
        tables.append(grid)
    return tables
```

#### Step 4: 제목(헤딩) 감지
```python
def detect_headings(root):
    """titleMark가 있는 문단을 제목으로 식별한다."""
    headings = []
    for p in root.iter(f'{{{NS["hp"]}}}p'):
        has_title = p.find(f'.//{{{NS["hp"]}}}titleMark') is not None
        if has_title:
            style_id = p.get('styleIDRef', '0')
            texts = [t.text for t in p.iter(f'{{{NS["hp"]}}}t') if t.text]
            headings.append({
                'level': style_id,  # header.xml의 스타일 참조
                'text': ''.join(texts)
            })
    return headings
```

### 4.3 출력 디렉토리 구조 및 파일명 규칙

#### 디렉토리 구조
```
{입력파일_디렉토리}/
└── hwpx_parsed/                          # 파싱 결과 루트 폴더
    └── {원본파일명}_{YYYYMMDD_HHmm}/     # 실행 시점 타임스탬프 폴더
        ├── full_text.md                  # 전체 텍스트 (Markdown)
        ├── full_text.txt                 # 전체 텍스트 (Plain Text)
        ├── headings.json                 # 제목 구조 목록
        ├── tables/                       # 표 추출 폴더
        │   ├── table_01_{표제목}.csv     # 개별 표 CSV (UTF-8-BOM)
        │   ├── table_02_{표제목}.csv
        │   ├── ...
        │   └── all_tables.xlsx           # 전체 표 통합 Excel (시트별)
        ├── images/                       # 이미지 추출 폴더
        │   ├── image_01.png              # 개별 이미지 (원본 포맷)
        │   ├── image_02.bmp
        │   └── ...
        └── parse_log.txt                 # 파싱 로그 (요소 수, 오류 등)
```

#### 파일명 규칙

| 항목          | 규칙                               | 예시                                              |
| ------------- | ---------------------------------- | ------------------------------------------------- |
| **루트 폴더** | `hwpx_parsed/`                     | 입력파일과 같은 디렉토리에 생성                   |
| **실행 폴더** | `{원본명}_{YYYYMMDD_HHmm}/`        | `TEST_MISS_1_20260219_1108/`                      |
| **텍스트**    | `full_text.md`, `full_text.txt`    | 고정 파일명                                       |
| **제목 구조** | `headings.json`                    | 고정 파일명                                       |
| **표 CSV**    | `table_{NN}_{표제목_sanitize}.csv` | `table_01_전국_및_경북_GRDP.csv`                  |
| **표 Excel**  | `all_tables.xlsx`                  | 고정 파일명, 시트명 = `표1_GRDP`, `표2_시군별` 등 |
| **이미지**    | `image_{NN}.{원본확장자}`          | `image_01.png`, `image_02.bmp`                    |
| **파싱 로그** | `parse_log.txt`                    | 고정 파일명                                       |

> **파일명 sanitize 규칙**: 표 제목에서 특수문자(`/\:*?"<>|`)를 `_`로 치환, 최대 50자 제한, 공백→`_`

#### CSV 저장 규칙
- 인코딩: **UTF-8 with BOM** (`utf-8-sig`) — Excel 한글 깨짐 방지
- 구분자: `,` (쉼표)
- 병합 셀은 첫 번째 셀에만 값 입력, 나머지는 빈 문자열

### 4.4 출력 형식 옵션

| 출력 형식      | 용도                | 구현 방법                      |
| -------------- | ------------------- | ------------------------------ |
| **Markdown**   | 보고서 재구성       | 제목 + 본문 + 표(마크다운 표)  |
| **CSV**        | 표 데이터 개별 추출 | 표별 CSV 파일 저장 (UTF-8-BOM) |
| **DataFrame**  | 분석·시각화         | pandas DataFrame 변환          |
| **Plain Text** | 전문 검색·요약      | 표 제외 순수 텍스트            |

### 4.5 주의사항 및 엣지 케이스

1. **셀 병합**: `colSpan`/`rowSpan`이 복잡 → 2D 점유(occupied) 배열 필수
2. **중첩 표**: 머리말/꼬리말 내부에도 `hp:tbl`이 존재 → 본문 표만 필터링 필요
3. **대용량 XML**: section0.xml이 17MB → `lxml.etree`의 iterparse 고려
4. **이미지 참조**: `hc:img binaryItemIDRef`로 `BinData/` 파일 매핑
5. **인코딩**: XML은 UTF-8이나, 한글 Windows에서 콘솔 출력 시 `chcp 65001` 필요
6. **페이지 구분**: `pageBreak="1"`로 페이지 경계 감지 가능
7. **스타일 해석**: `charPrIDRef`, `paraPrIDRef` → `header.xml`의 스타일 정의 참조 필요

---

## 5. 검증 계획

### 자동 검증
```bash
# 1. 파서 실행 후 표 개수 확인
python hwpx_parser.py TEST_MISS_1.hwpx --count-tables

# 2. 첫 번째 표 CSV 추출 후 데이터 확인
python hwpx_parser.py TEST_MISS_1.hwpx --extract-table 0 --output table0.csv

# 3. 전체 텍스트 추출 후 키워드 검색
python hwpx_parser.py TEST_MISS_1.hwpx --text-only | findstr "GRDP"
```

### 수동 검증
- 추출된 표의 셀 병합이 올바른지 원본 한글 문서와 비교
- 추출된 텍스트에서 누락된 문단이 없는지 확인

---

## 6. 파서 실행 결과

> 실행일: 2026-02-19 11:41 | 소요시간: **2.2초** | 파서 버전: v1.0

### 6.1 실행 요약

| 항목   | 수량  |
| ------ | ----- |
| 섹션   | 1개   |
| 문단   | 968개 |
| 제목   | 56개  |
| 표     | 125개 |
| 이미지 | 36개  |

### 6.2 출력 디렉토리

```
hwpx_parsed/TEST_MISS_1_20260219_1141/
├── full_text.md       (283KB)   # Markdown 텍스트
├── full_text.txt      (281KB)   # Plain Text
├── headings.json      (5.6KB)   # 제목 구조 (56개)
├── parse_log.txt      (6.5KB)   # 파싱 로그
├── tables/                      # 125개 CSV + 1 Excel
│   ├── table_01.csv ~ table_125.csv
│   └── all_tables.xlsx (245KB)
└── images/                      # 36개 이미지
    ├── image_01.jpg ~ image_36.bmp
    └── (bmp/png/jpg/wmf 형식 혼재)
```

### 6.3 제목 구조 분석

제목은 3단계 (`styleIDRef` 0, 1, 2, 3)로 추출됨:
- **Level 1** (개요1): `1. 경북지역 산업 현황 분석`, `2. 경북지역 고용 현황 분석`, `3. 소결` 등
- **Level 2** (개요2): `(1) 경제 현황 및 산업구조`, `(2) 경북지역 주력산업 현황` 등
- **Level 0/3** (하위): `① 지역내총생산`, `② 산업구조` 등 (원문자 번호)

### 6.4 특이사항

1. **표 제목 미추출**: 표 위 문단에서 제목을 추측하는 로직이 일부 표에서 빈 문자열 반환 → CSV 파일명이 `table_NN.csv` (제목 없음)
2. **이미지 포맷 혼재**: bmp(대용량, 최대 25MB), wmf, jpg, png 등 다양한 포맷
3. **styleIDRef=0 제목**: 원문자(①②③) 번호가 있는 소제목의 styleIDRef가 0으로, 본문과 구분이 어려울 수 있음
4. **오류 없음**: 파싱 중 오류 0건 발생

### 6.5 실행 사례 2: 문경 영순 타당성 보고서

> 실행일: 2026-02-19 19:08 | 소요시간: **0.4초** | 파서 버전: v1.0

#### 대상 파일

| 항목      | 내용                                               |
| --------- | -------------------------------------------------- |
| 파일명    | `문경 영순_타당성 보고서(송부용)_20260217_v4.hwpx` |
| 파일 크기 | 약 200KB                                           |
| 문서 유형 | 산업단지 조성사업 타당성 검토 보고서               |

#### 추출 요약

| 항목   | 수량  |
| ------ | ----- |
| 섹션   | 1개   |
| 문단   | 266개 |
| 제목   | 7개   |
| 표     | 52개  |
| 이미지 | 2개   |

#### 출력 디렉토리

```
hwpx_parsed/문경 영순_타당성 보고서(송부용)_20260217_v4_20260219_1908/
├── full_text.md       (45.6KB)  # Markdown 텍스트
├── full_text.txt      (45.0KB)  # Plain Text
├── headings.json      (0.7KB)   # 제목 구조 (7개)
├── parse_log.txt      (2.0KB)   # 파싱 로그
├── tables/                      # 52개 CSV + 1 Excel
│   ├── table_01.csv ~ table_52.csv
│   └── all_tables.xlsx (55KB)
└── images/                      # 2개 이미지
    ├── image_01.bmp
    └── image_02.bmp
```

#### 제목 구조

| 레벨 | styleIDRef | 제목 텍스트                           |
| ---- | ---------- | ------------------------------------- |
| 5    | 5          | 1.2. 전제조건의 설정                  |
| 4    | 4          | 2. 비용 추정                          |
| 5    | 5          | 2.1. 분석 관점에 따른 비용추정의 개요 |
| 5    | 5          | 2.2. 경제성 분석용 사업비 설정        |
| 5    | 5          | 2.3. 상부건축물 건축비 추정           |
| 6    | 6          | 3) 운영경비 추정                      |
| 6    | 6          | 4) 연차별 사업비 추정 결과            |

#### 특이사항

1. **문서 구조**: 타당성 분석 보고서로 경제성/재무성 분석 데이터가 대부분을 차지
2. **표 52개 중 대형 표 다수**: 최대 40행×10열 (연차별 사업비 분석표)
3. **표 제목 미추출**: 표 위 문단이 `< 표제목 >` 형식이나 파서의 제목 추측 로직이 빈 문자열 반환
4. **오류 없음**: 파싱 중 오류 0건

---

## 10. 업데이트 내역

| 버전 | 날짜       | 변경 내용                                                                              |
| ---- | ---------- | -------------------------------------------------------------------------------------- |
| v1.0 | 2026-02-19 | 초기 버전 — HWPX 구조 분석, 파싱 계획, 검증 계획 작성                                  |
| v1.1 | 2026-02-19 | 출력 디렉토리 구조 및 파일명 규칙 추가                                                 |
| v1.2 | 2026-02-19 | 산출물 보고서 3종 구조, 버전 규칙, 업데이트 내역 섹션 추가                             |
| v1.3 | 2026-02-19 | 목차 추가, 섹션 번호 중복(4.4) 수정 → 4.5로 변경                                       |
| v1.4 | 2026-02-19 | 파서 구현 완료, 실행 결과 반영, 파일명 `TEST_MISS._1` → `TEST_MISS_1` 변경             |
| v1.5 | 2026-02-19 | 산출물 보고서 3종 작성, 아키텍처를 실제 구현 기준으로 갱신, 계획 대비 변경점 표 추가   |
| v1.6 | 2026-02-19 | 표별 출처 추출(방법 B) 실행 결과 추가, 추후 개발 계획(방법 A: XML 파서 확장) 섹션 추가 |
| v1.7 | 2026-02-19 | 문경 영순 타당성 보고서 파싱 사례(6.5) 추가                                            |


파서 제작 완료 후 아래 3종의 보고서를 작성한다.

### 7.1 보고서 목록

| #   | 보고서명                      | 파일명 형식                          | 내용                                                 |
| --- | ----------------------------- | ------------------------------------ | ---------------------------------------------------- |
| 1   | **HWPX 파서 제작 가이드라인** | `hwpx_parser_dev_guide_v{X.Y}.md`    | 개발 환경, 아키텍처, 모듈 설계, 핵심 로직, 빌드 방법 |
| 2   | **HWPX 파서 활용 가이드라인** | `hwpx_parser_usage_guide_v{X.Y}.md`  | 설치, CLI 사용법, Python API, 입출력 예시, FAQ       |
| 3   | **에러 및 오류 해결 리포트**  | `hwpx_parser_error_report_v{X.Y}.md` | 개발 중 발생한 오류, 원인 분석, 해결 방법, 회피 전략 |

### 7.2 보고서 버전 규칙

| 항목            | 규칙                               | 예시                        |
| --------------- | ---------------------------------- | --------------------------- |
| **버전 형식**   | `v{Major}.{Minor}` (시맨틱 버전)   | `v1.0`, `v1.1`, `v2.0`      |
| **Major 변경**  | 파서 구조 대폭 변경, 호환성 깨짐   | `v1.0` → `v2.0`             |
| **Minor 변경**  | 기능 추가, 버그 수정, 문서 보완    | `v1.0` → `v1.1`             |
| **파일명 예시** | `hwpx_parser_dev_guide_v1.0.md`    | 첫 릴리즈                   |
| **업데이트 시** | 새 버전 파일 생성 (이전 버전 유지) | `v1.0` → `v1.1` (v1.0 보존) |

### 7.3 보고서 공통 구조

각 보고서는 아래 공통 구조를 따른다:

```markdown
# {보고서 제목}

> 버전: v{X.Y} | 작성일: YYYY-MM-DD | 최종 수정: YYYY-MM-DD

---

## 목차
(자동 생성 또는 수동 작성)

---

## 1. 개요
(보고서 목적, 대상 독자)

## 2. 본문
(보고서별 상세 내용)

...

## N. 업데이트 내역

| 버전 | 날짜       | 작성자 | 변경 내용                    |
| ---- | ---------- | ------ | ---------------------------- |
| v1.0 | 2026-02-19 | -      | 초기 버전 작성               |
| v1.1 | 2026-XX-XX | -      | OOO 기능 추가, XXX 버그 수정 |
```

### 7.4 각 보고서 상세 목차

#### 보고서 1: HWPX 파서 제작 가이드라인 (`hwpx_parser_dev_guide_v{X.Y}.md`)
1. 개요
2. 개발 환경 (Python 버전, 의존 패키지, OS 요구사항)
3. HWPX 파일 구조 분석 (본 가이드라인 요약)
4. 모듈 아키텍처 (클래스 다이어그램, 모듈 관계)
5. 핵심 파싱 로직 (XML 파싱, 셀 병합, 제목 감지 등)
6. 출력 디렉토리 및 파일명 규칙
7. 테스트 방법
8. 알려진 제한사항
9. 업데이트 내역

#### 보고서 2: HWPX 파서 활용 가이드라인 (`hwpx_parser_usage_guide_v{X.Y}.md`)
1. 개요
2. 설치 방법 (`pip install`, 의존성)
3. 빠른 시작 (Quick Start)
4. CLI 사용법 (명령어 옵션, 실행 예시)
5. Python API 사용법 (import, 함수 호출 예시)
6. 입출력 예시 (입력 파일 → 출력 결과 스크린샷)
7. 자주 묻는 질문 (FAQ)
8. 업데이트 내역

#### 보고서 3: 에러 및 오류 해결 리포트 (`hwpx_parser_error_report_v{X.Y}.md`)
1. 개요
2. 오류 목록 요약표

| #   | 오류 유형 | 발생 시점 | 심각도 | 해결 여부 |
| --- | --------- | --------- | ------ | --------- |
| 1   | ...       | ...       | ...    | ✅/❌       |

3. 개별 오류 상세
   - 오류 설명
   - 재현 조건
   - 에러 메시지 / 스택 트레이스
   - 원인 분석
   - 해결 방법
   - 회피 전략 (미해결 시)
4. 업데이트 내역

### 7.5 보고서 저장 위치

```
{프로젝트_디렉토리}/HWPX/
├── hwpx_guideline.md                          # 본 가이드라인 (현재 문서)
├── hwpx_parser.py                             # 파서 소스코드
├── hwpx_parser_dev_guide_v1.0.md              # 제작 가이드라인 보고서
├── hwpx_parser_usage_guide_v1.0.md            # 활용 가이드라인 보고서
├── hwpx_parser_error_report_v1.0.md           # 에러 리포트
└── hwpx_parsed/                               # 파싱 결과 출력 폴더
```

---

## 8. 표별 출처 추출 결과

> 실행일: 2026-02-19 12:15 | 방법: B (full_text.md 텍스트 분석) | 스크립트: `extract_table_sources.py`

### 8.1 추출 요약

| 항목              | 수량     |
| ----------------- | -------- |
| 전체 표 수        | 125개    |
| 출처 발견 표 수   | **58개** |
| 출처 미발견 표 수 | 67개     |

> 출처 미발견 표는 주로 설문조사 결과, 분석 산출 데이터, 요약표 등 자체 작성 데이터임

### 8.2 주요 출처 기관

| 출처 기관        | 횟수 | 주요 통계/조사명                                               |
| ---------------- | ---- | -------------------------------------------------------------- |
| 통계청           | 15+  | 지역소득, GRDP, 경제활동인구, 국내인구이동통계, 사업체조사 등  |
| 고용노동부       | 5+   | 사업체노동력조사, 직종별 사업체 노동력조사, 워크넷 구인구직 DB |
| 한국교육개발원   | 4+   | 직업계고 취업통계조사, 고등교육기관 졸업자 취업통계조사        |
| 경상북도         | 4+   | 지역산업진흥계획, 사업체조사, 공항경제권 신산업 육성 방안      |
| 각 기관 홈페이지 | 4    | 공공기관/대학/여성새로일하기센터 교육 프로그램                 |
| 행정안전부       | 2    | 지방자치단체 외국인 주민현황                                   |
| 중소벤처기업부   | 3    | 지역특화산업육성+사업 후속사업 기획보고서                      |

### 8.3 출력 파일

```
hwpx_parsed/TEST_MISS_1_20260219_1141/
├── table_sources.json   # 58개 표의 상세 출처 매핑 (JSON)
└── table_sources.csv    # 동일 데이터 CSV (UTF-8-BOM)
```

각 항목에 포함되는 필드:
- `table_no`: 표 순서 번호
- `section`: 소속 제목(heading)
- `title`: 표 제목
- `unit`: 단위 정보
- `content_preview`: 표 내용 미리보기 (최대 150자)
- `source`: 출처 (자료 출처 + 주석)
- `line_no`: full_text.md 내 라인 번호

---

## 9. 추후 개발 계획

### 9.1 방법 A: XML 직접 파싱으로 표 출처 자동 추출 (파서 내장)

현재 `extract_table_sources.py`는 `full_text.md` 텍스트를 분석하는 방식(방법 B)이다. 향후 `hwpx_parser.py`의 `TableExtractor` 클래스에 출처 추출 기능을 직접 통합하여 더 정확한 XML 기반 추출을 구현할 수 있다.

#### 구현 대상

##### (1) `_guess_table_source()` 메서드 추가
- 표를 포함하는 `hp:p` 요소의 **다음 형제(sibling)** 문단들을 탐색
- `자료`, `출처`, `※`, `주.`, `주1.` 등의 키워드로 시작하는 문단을 출처로 인식
- 연속된 출처/주석 문단을 모두 수집하여 반환

```python
@staticmethod
def _guess_table_source(tbl_elem, text_extractor: TextExtractor) -> dict:
    """표 바로 아래 문단에서 출처(자료)를 추측한다."""
    parent_p = tbl_elem.getparent()
    if parent_p is None or parent_p.tag != _tag('hp', 'p'):
        return {'source': '', 'notes': []}
    
    sources = []
    notes = []
    next_sibling = parent_p.getnext()
    while next_sibling is not None and next_sibling.tag == _tag('hp', 'p'):
        text = text_extractor.extract_paragraph_text(next_sibling)
        if not text:
            next_sibling = next_sibling.getnext()
            continue
        if re.match(r'^(자료\s*[:：]|※\s*자료)', text):
            sources.append(text)
        elif re.match(r'^(주\d*[\.:：]|\d+\)\s)', text):
            notes.append(text)
        elif text.startswith('※'):
            notes.append(text)
        else:
            break
        next_sibling = next_sibling.getnext()
    
    return {'source': ' | '.join(sources), 'notes': notes}
```

##### (2) `extract_all()` 수정
- 각 표 딕셔너리에 `source` 및 `notes` 필드 추가

```python
# extract_all() 내부에 추가
source_info = self._guess_table_source(tbl, text_ext)
tables.append({
    'index': table_idx,
    'title': title,
    'rows': row_cnt,
    'cols': col_cnt,
    'grid': grid,
    'source': source_info['source'],      # 신규
    'notes': source_info['notes'],         # 신규
})
```

##### (3) `OutputWriter` 수정
- CSV 저장 시 출처 정보를 메타데이터 행으로 포함
- `table_sources.json` 파일 자동 생성

#### 기대 효과
- 파서 실행 시 출처 정보가 자동으로 추출되어 별도 스크립트 불필요
- XML 기반이므로 텍스트 분석 대비 매핑 정확도 향상
- 표 CSV에 출처가 메타데이터로 포함되어 데이터 추적성 확보




