# 차트 규칙 추가 가이드

## 규칙 파일 구조

각 `rule_*.py` 파일은 두 가지를 정의합니다:

### 1. RULE 딕셔너리
```python
RULE = {
    "chart_type": "pie",           # 차트 유형명
    "priority": 10,                # 우선순위 (낮을수록 먼저 판별)
    "builder_method": "add_pie",   # Builder의 메서드명
}
```

### 2. match() 함수
```python
def match(title, labels, pcts, freqs, n, **kwargs):
    """이 데이터에 해당 차트가 적합한지 True/False 반환"""
    return len(labels) <= 6
```

## 우선순위 가이드

| priority | 용도 |
|---|---|
| 1-10 | 확실한 매칭 (파이: 항목수 6개 이하 + 합 100%) |
| 11-30 | 키워드 기반 매칭 (레이더, 누적) |
| 100 | 폴백 (수평막대 — 마지막 기본값) |

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

## 테스트 방법
```python
from chart_rules.rule_donut import match
assert match("영향 분석", ["긍정", "부정"], [60, 40], [30, 20], 50)
```
