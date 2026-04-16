# Excel 스타일 복사 트러블슈팅 리포트

> **작성일**: 2026-03-20  
> **케이스**: `contact_list_target_5000_260320` 스타일 적용 작업

---

## 문제 1: Excel "내용에 문제가 있습니다" 오류 (1차)

### 증상
- openpyxl로 생성한 xlsx 파일을 Excel에서 열 때 복구 대화상자 표시
- "이 통합 문서의 내용을 최대한 복구하시겠습니까?"

### 원인
`Color(theme=N, tint=T)` API 사용 시 openpyxl이 생성하는 XML이 Excel과 호환되지 않음

```python
# 문제 코드
header_fill = PatternFill(fill_type='solid', fgColor=Color(theme=3, tint=-0.499984740745262))
header_font = Font(color=Color(theme=0))
spacer_fill = PatternFill(fill_type='solid', fgColor=Color(theme=1))
```

### 해결
theme 인덱스를 실제 RGB 값으로 변환하여 사용

```python
# 해결 코드
header_fill = PatternFill(fill_type='solid', fgColor='938953')
header_font = Font(color='FFFFFF')
spacer_fill = PatternFill(fill_type='solid', fgColor='FFFFFF')
```

### RGB 변환 방법

```python
import zipfile, colorsys
from openpyxl.xml.functions import fromstring

zf = zipfile.ZipFile('reference.xlsx')
theme_xml = zf.read('xl/theme/theme1.xml')
# ... clrScheme에서 base RGB 추출 후 tint 적용
```

---

## 문제 2: Excel "내용에 문제가 있습니다" 오류 (2차)

### 증상
- RGB 색상으로 수정 후에도 동일한 오류 지속

### 원인
`load_workbook()` → `insert_rows()` → `ws.auto_filter.ref` / `ws.print_area` 조합이
xlsx 내부 XML 참조를 손상시킴

```python
# 문제 코드
wb = load_workbook(SRC_FILE)        # 기존 파일 로드
ws.insert_rows(2)                    # 행 삽입 -> 내부 참조 깨짐
ws.auto_filter.ref = f'A1:Y{max_row}' # 손상된 참조에 필터 설정
ws.print_area = f'M1:Y{max_row}'     # print_area도 오류 유발
```

### 해결
기존 파일 수정이 아닌, **새 워크북(`Workbook()`)으로 처음부터 생성**

```python
# 해결 코드
wb = Workbook()               # 새 워크북 생성
ws = wb.active
# 데이터를 cell by cell로 직접 기록
# auto_filter, print_area는 제거
```

### 핵심 교훈

> [!CAUTION]
> `load_workbook()` + `insert_rows()` 조합은 xlsx 내부의 행 참조, 
> 자동필터 범위, 인쇄영역 등을 손상시킬 수 있음.
> 스타일 복사 시에는 반드시 `Workbook()`으로 새로 생성할 것.

---

## 요약: 안전한 스타일 적용 체크리스트

| # | 항목 | 상태 |
|---|---|---|
| 1 | `Color(theme=...)` 대신 RGB 헥스 사용 | 필수 |
| 2 | `Workbook()`으로 새 파일 생성 | 필수 |
| 3 | `insert_rows()` / `delete_rows()` 사용 금지 | 필수 |
| 4 | `auto_filter` 설정 시 독립 테스트 | 권장 |
| 5 | `print_area` 설정 시 시트명 prefix 제거 | 권장 |
| 6 | 생성 후 Excel에서 오류 없이 열리는지 확인 | 필수 |
