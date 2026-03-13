# HWPX 파서 활용 가이드라인

> 버전: v1.0 | 작성일: 2026-02-19 | 최종 수정: 2026-02-19

---

## 1. 개요

`hwpx_parser.py`는 한컴 HWPX 파일에서 텍스트, 표, 이미지, 제목 구조를 자동 추출하는 Python 도구이다.

**대상 독자**: 파서를 사용하여 HWPX 파일을 분석하려는 사용자

---

## 2. 설치 방법

### 2.1 필수 패키지
```bash
pip install lxml
```

### 2.2 선택 패키지 (Excel 출력 시)
```bash
pip install pandas openpyxl
```

> ⚠️ pandas/openpyxl이 없어도 파서는 동작하며, Excel 출력만 비활성화됩니다.

---

## 3. 빠른 시작 (Quick Start)

```bash
# HWPX 파일 전체 추출 (텍스트 + 표 + 이미지)
python hwpx_parser.py 보고서.hwpx
```

실행 후 같은 디렉토리에 `hwpx_parsed/보고서_YYYYMMDD_HHmm/` 폴더가 생성됩니다.

---

## 4. CLI 사용법

### 4.1 기본 문법
```
python hwpx_parser.py <hwpx_파일> [옵션]
```

### 4.2 옵션 상세

| 옵션                | 설명                    | 예시                                                  |
| ------------------- | ----------------------- | ----------------------------------------------------- |
| (없음)              | 전체 추출 (기본)        | `python hwpx_parser.py sample.hwpx`                   |
| `--count-tables`    | 표 개수만 출력          | `python hwpx_parser.py sample.hwpx --count-tables`    |
| `--text-only`       | 텍스트만 콘솔에 출력    | `python hwpx_parser.py sample.hwpx --text-only`       |
| `--extract-table N` | N번째 표만 추출 (1부터) | `python hwpx_parser.py sample.hwpx --extract-table 3` |
| `--output FILE`     | 출력 파일 지정 (CSV)    | `--extract-table 1 --output t1.csv`                   |
| `--output-dir DIR`  | 출력 디렉토리 변경      | `--output-dir D:\output`                              |

### 4.3 사용 예시

```bash
# 1. 표 개수 빠르게 확인
python hwpx_parser.py TEST_MISS_1.hwpx --count-tables
# 출력: 표 개수: 125

# 2. 전체 추출
python hwpx_parser.py TEST_MISS_1.hwpx
# 출력: hwpx_parsed/TEST_MISS_1_20260219_1141/ 폴더 생성

# 3. 1번 표를 CSV로 저장
python hwpx_parser.py TEST_MISS_1.hwpx --extract-table 1 --output table1.csv

# 4. 텍스트에서 키워드 검색
python hwpx_parser.py TEST_MISS_1.hwpx --text-only | findstr "GRDP"

# 5. 출력 디렉토리 변경
python hwpx_parser.py TEST_MISS_1.hwpx --output-dir D:\results
```

---

## 5. Python API 사용법

```python
from hwpx_parser import parse_hwpx, HwpxReader, TableExtractor, TextExtractor

# 방법 1: 원스톱 추출
result = parse_hwpx("sample.hwpx")
print(f"문단 수: {len(result['paragraphs'])}")
print(f"표 수: {len(result['tables'])}")
print(f"출력 위치: {result['output_dir']}")

# 방법 2: 개별 추출기 사용
with HwpxReader("sample.hwpx") as reader:
    sections = reader.get_section_roots()
    
    # 텍스트 추출
    text_ext = TextExtractor()
    for root in sections:
        paragraphs = text_ext.extract_all(root)
        for p in paragraphs:
            print(p)

    # 표 추출
    table_ext = TableExtractor()
    for root in sections:
        tables = table_ext.extract_all(root)
        for t in tables:
            print(f"표 {t['index']}: {t['rows']}행 × {t['cols']}열")
            # DataFrame으로 변환
            df = table_ext.to_dataframe(t)
            print(df.head())
```

---

## 6. 입출력 예시

### 6.1 입력
- `TEST_MISS_1.hwpx` (3.5MB, 2025년도 경북RSC 기초조사 보고서)

### 6.2 실행 결과
```
소요: 2.2초
문단: 968개 / 제목: 56개 / 표: 125개 / 이미지: 36개
```

### 6.3 출력 디렉토리
```
hwpx_parsed/TEST_MISS_1_20260219_1141/
├── full_text.md       (283KB)
├── full_text.txt      (281KB)
├── headings.json      (5.6KB)
├── parse_log.txt      (6.5KB)
├── tables/
│   ├── table_01.csv ~ table_125.csv
│   └── all_tables.xlsx (245KB)
└── images/
    └── image_01.jpg ~ image_36.bmp
```

---

## 7. 자주 묻는 질문 (FAQ)

### Q1. 한글 프로그램을 실행한 상태에서 파서를 돌려도 되나요?
**A**: 네, 괜찮습니다. 이 파서는 한글 COM 자동화를 사용하지 않고 ZIP/XML을 직접 파싱합니다. 단, **파싱 대상 파일을 한글에서 열어둔 상태라면** 파일 잠금 오류가 발생할 수 있습니다.

### Q2. pandas가 없으면 어떻게 되나요?
**A**: Excel(`all_tables.xlsx`) 출력만 비활성화됩니다. CSV, Markdown, Plain Text, JSON은 정상 출력됩니다.

### Q3. 표 제목이 빈칸인 CSV가 있습니다.
**A**: 일부 표는 바로 위 문단에 제목이 없어서 자동 추측이 실패합니다. CSV 파일명은 `table_NN.csv`로 표시됩니다. 내용 확인 후 수동으로 제목을 부여하시면 됩니다.

### Q4. BMP 이미지가 너무 큽니다.
**A**: 원본 포맷 그대로 추출됩니다. 별도 변환 도구(예: `Pillow`)로 PNG/JPG로 변환하세요:
```python
from PIL import Image
img = Image.open("image_02.bmp")
img.save("image_02.png")
```

### Q5. 여러 HWPX 파일을 일괄 처리할 수 있나요?
**A**: 현재 CLI는 단일 파일만 지원합니다. 배치 처리는 Python 스크립트를 작성하세요:
```python
from pathlib import Path
from hwpx_parser import parse_hwpx

for hwpx in Path(".").glob("*.hwpx"):
    result = parse_hwpx(str(hwpx))
    print(f"{hwpx.name}: 표 {len(result['tables'])}개")
```

---

## 8. 업데이트 내역

| 버전 | 날짜       | 작성자 | 변경 내용      |
| ---- | ---------- | ------ | -------------- |
| v1.0 | 2026-02-19 | -      | 초기 버전 작성 |
