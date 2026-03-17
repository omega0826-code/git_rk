# 차트 규칙 추가 가이드

## 규칙 파일 구조

각 `rule_*.py` 파일은 두 가지를 정의합니다:

### 1. RULE 딕셔너리
```python
RULE = {
    "chart_type": "pie",           # 차트 유형명
    "priority": 5,                 # 우선순위 (낮을수록 먼저 판별)
    "builder_method": "add_pie",   # Builder의 메서드명
}
```

### 2. match() 함수
```python
def match(title, labels, pcts, freqs, n, **kwargs):
    """이 데이터에 해당 차트가 적합한지 True/False 반환"""
    return len(labels) <= 2
```

## 현재 등록된 규칙

| 파일 | 차트 유형 | 우선순위 | 판별 기준 |
|---|---|---|---|
| `rule_satisfaction.py` | vbar (세로막대) | 3 | 제목에 '만족도' 포함 |
| `rule_pie.py` | pie (파이) | 5 | 항목 ≤2개 |
| `rule_radar.py` | radar (레이더) | 10 | 제목에 '레이더' 포함 |
| `rule_stacked.py` | stacked (누적) | 15 | 제목에 '누적' 포함 |
| `rule_hbar.py` | hbar (가로막대) | 20 | 항목 ≥6개 |
| `rule_vbar.py` | vbar (세로막대) | 100 | 기본 폴백 |

> **우선순위 흐름**: 만족도 키워드(3) → 파이(5) → 레이더(10) → 누적(15) → 가로(20) → 세로 폴백(100)

## 우선순위 가이드

| priority | 용도 |
|---|---|
| 1-5 | 키워드 우선 매칭 (만족도 → vbar) |
| 5-10 | 항목 수 기반 매칭 (파이: ≤2개) |
| 11-20 | 키워드 + 항목 수 조합 (레이더, 누적, 가로) |
| 100 | 폴백 (세로막대 — 마지막 기본값) |

## 새 차트 추가 예제

### 예: 도넛 차트
```python
# chart_rules/rule_donut.py
RULE = {"chart_type": "donut", "priority": 8, "builder_method": "add_pie"}
def match(title, labels, pcts, freqs, n, **kwargs):
    return '영향' in title and len(labels) == 2
```

### 예: 꺾은선 차트
```python
# chart_rules/rule_line.py
RULE = {"chart_type": "line", "priority": 25, "builder_method": "add_line"}
def match(title, labels, pcts, freqs, n, **kwargs):
    return '추이' in title or '변화' in title
```

> `add_line` 메서드는 `chart_builder.py`에도 추가해야 합니다.

## 데이터 라벨 규칙

차트 빌더는 비율(%)과 빈도(명) 두 시리즈의 데이터를 포함합니다.

| 차트 유형 | 라벨 형식 | 구분자 |
|---|---|---|
| vbar | `비율%\n(빈도)` | 줄바꿈 |
| hbar | `비율% (빈도)` | 공백 |
| pie | `카테고리 비율% (빈도)` | 공백 |

> 빈도 시리즈는 `_remove_extra_series()`로 차트 XML에서 제거되어 막대/파이에 표시되지 않지만,
> **차트 우클릭 → 데이터 편집**에서 워크시트 데이터로 확인/수정 가능합니다.

## 테스트 방법
```python
from chart_rules.rule_satisfaction import match
assert match("RISE사업 전반 만족도", ["만족", "보통", "불만족"], [60, 30, 10], [30, 15, 5], 50)
```
