# 🔧 차트 생성 스크립트 — 개발 매뉴얼

> **대상**: `create_chart_pptx.py` (v4) | **python-pptx 0.6+**

---

## 1. 아키텍처 개요

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Excel 데이터  │ →  │   데이터 추출   │ →  │  차트 빌더     │ → PPTX
│   (openpyxl)   │    │  get_bar_data │    │  Builder 클래스  │
│                │    │  get_pie1     │    │  add_hbar()    │
│                │    │  get_radar    │    │  add_pie()     │
│                │    │  get_stacked  │    │  add_radar()   │
└──────────────┘    └──────────────┘    │  add_stacked() │
                                         └──────────────┘
```

---

## 2. 모듈 구성

### 2.1 설정 클래스

```python
@dataclass
class Cfg:
    idx: int          # 표 번호
    title: str        # 슬라이드 제목
    total_row: int    # 합계 행 번호
    name_row: int     # 항목명 행 번호
    data_col: int     # 데이터 시작 열 (기본: 4)
    n_col: int        # 응답자 수(n) 열 (기본: 3)
    chart: str        # "hbar" | "pie" | "donut" | "radar" | "stacked"
    end_row: int      # stacked 전용 — 데이터 마지막 행
```

### 2.2 데이터 추출 함수

| 함수                    | 반환값                      | 용도                 |
| ----------------------- | --------------------------- | -------------------- |
| `get_bar_data(ws, cfg)` | `(labels, pcts, freqs, n)`  | 수평막대/파이/도넛   |
| `get_pie1(ws)`          | `(labels, pcts, vals, n)`   | 표1 전용 (구조 상이) |
| `get_radar(ws, cfg)`    | `(labels, values)`          | 레이더 (평균 점수)   |
| `get_stacked(ws, cfg)`  | `(items, data_dict, univs)` | 누적막대 (대학별)    |

### 2.3 Builder 클래스 메서드

| 메서드          | 인자                                          | 설명           |
| --------------- | --------------------------------------------- | -------------- |
| `add_hbar()`    | labels, pcts, freqs, n, title, pg, tot        | 수평 막대 차트 |
| `add_pie()`     | labels, pcts, freqs, n, title, pg, tot, donut | 파이/도넛      |
| `add_radar()`   | labels, values, title, pg, tot                | 레이더         |
| `add_stacked()` | items, data, univs, title, pg, tot            | 누적 막대      |

---

## 3. 새 차트 유형 추가 방법

### Step 1: `TABLES`에 설정 추가
```python
Cfg(19, "신규 표 제목", total_row=400, name_row=398, chart="new_type")
```

### Step 2: 데이터 추출 함수 작성
```python
def get_new_data(ws, c):
    # ... Excel에서 데이터 추출
    return labels, values, n
```

### Step 3: Builder에 메서드 추가
```python
def add_new_type(self, ...):
    slide = self._slide()
    self._title(slide, title, sub)
    self._unit(slide, "단위")
    # ... 차트 생성
    self._pgnum(slide, pg, tot)
```

### Step 4: 메인 루프에 분기 추가
```python
elif c.chart == "new_type":
    data = get_new_data(ws, c)
    b.add_new_type(data, c.title, pg, total)
```

---

## 4. python-pptx 주의사항 (필독)

### ✅ 안전한 API 사용법
```python
# 데이터 라벨 — 표준 방식
plot.has_data_labels = True
dl = plot.data_labels
dl.number_format = '0.0"%"'

# 커스텀 라벨 — add_run만 사용 (clear 금지)
tf = ser.points[i].data_label.text_frame
p = tf.paragraphs[0]
run = p.add_run()
run.text = "50.5% (505)"
```

### ❌ 사용 금지 패턴
| 패턴                       | 이유                            |
| -------------------------- | ------------------------------- |
| `val_axis.delete = True`   | PowerPoint 복구 경고            |
| `val_axis.visible = False` | 존재하지 않는 속성              |
| `text_frame.clear()`       | 필수 XML 요소 삭제              |
| `chart.chart_style = N`    | 일부 값 비호환                  |
| `major_tick_mark = 정수`   | enum 대신 정수 직접 할당 비호환 |
| lxml `etree.SubElement()`  | 네임스페이스 불일치             |

### ✅ 축 숨김 — 안전한 방법
```python
va = chart.value_axis
va.has_major_gridlines = False
va.has_title = False
va.tick_labels.font.size = Pt(2)
va.tick_labels.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)  # 배경색
va.format.line.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
```

---

## 5. 의존성

| 패키지        | 버전 | 용도       |
| ------------- | ---- | ---------- |
| `python-pptx` | 0.6+ | PPTX 생성  |
| `openpyxl`    | 3.0+ | Excel 읽기 |

```bash
pip install python-pptx openpyxl
```
