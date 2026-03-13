# ⚠️ 차트 생성 오류 리포트

> **기간**: 2026-02-24 | **버전**: v1 → v4

---

## 오류 이력 요약

| 버전 | 주요 변경                               | 결과          |
| ---- | --------------------------------------- | ------------- |
| v1   | python-pptx 표준 API + 일부 비호환 속성 | ⚠️ 복구 경고   |
| v2   | lxml XML 직접 조작으로 전환             | ❌ 데이터 손실 |
| v3   | 표준 API만 사용, 축 투명 처리           | ✅ 정상        |
| v4   | 흰 배경 + 검정 라벨, 빈도 시리즈 제거   | ✅ 정상        |

---

## 상세 오류 기록

### 오류 #1: PowerPoint 복구 경고 (v1)

**증상**: 파일 열 때마다 "복구가 시도될 수 있습니다" 대화상자 표시

**원인** (3가지):
| #   | 코드                                           | 문제                                                 |
| --- | ---------------------------------------------- | ---------------------------------------------------- |
| 1   | `val_axis.visible = False`                     | python-pptx에 존재하지 않는 속성 → 잘못된 XML 생성   |
| 2   | `val_axis.delete = True` + 다른 속성 동시 설정 | 삭제 축에 `has_title`, `has_major_gridlines` 등 충돌 |
| 3   | `major_tick_mark = 2`                          | enum 대신 정수 직접 할당 → 버전 비호환               |

**해결**: 해당 속성 모두 제거, 축 투명 처리로 전환

---

### 오류 #2: 데이터 손실 (v2)

**증상**: PowerPoint에서 복구 후 차트 데이터가 사라지거나 왜곡

**원인**:
```python
# 잘못된 패턴 — etree.SubElement(dummy, ...) 사용
tx = etree.SubElement(etree.Element('dummy'), _qn(C_NS, 'tx'))
dLbl = etree.SubElement(etree.Element('dummy'), _qn(C_NS, 'dLbl'))
```
- `dummy` 부모 참조 충돌: lxml에서 child를 다른 parent에 재삽입 시 원본 트리 손상
- 네임스페이스 불일치: `etree.Element`로 생성 시 OOXML 네임스페이스 누락
- `<c:dLbls>` 없이 개별 `<c:dLbl>`만 삽입: PowerPoint 복구 시 데이터를 버림

**교훈**: python-pptx 내부 XML 직접 조작은 금지. 표준 API만 사용할 것.

---

### 오류 #3: 빈도 시리즈 중복 라벨 (v3 → v4 과도기)

**증상**: 막대 차트에 빈도 시리즈가 별도 바+라벨로 표시 (717.0%, 400.0%)

**원인**:
```python
cd.add_series('비율(%)', s_p)
cd.add_series('빈도', s_f)    # ← 2번째 시리즈 bar 생성
# series.has_data_labels = False  ← 효과 없음 (python-pptx 미지원)
```
- `plot.has_data_labels = True`는 **모든 시리즈**에 적용
- 개별 시리즈에서 `has_data_labels` 속성 미지원
- `format.fill.background()`로 투명 처리해도 라벨은 남음

**해결**: 빈도 시리즈 자체를 제거. 데이터 라벨에 빈도 정보만 포함.

---

### 오류 #4: 차트 제목 "비율(%)" 표시 (v1~v3)

**증상**: 파이/레이더 차트 상단에 검정색 "비율(%)" 또는 "평균 점수" 텍스트

**원인**: 시리즈명이 차트 제목으로 자동 표시
```python
cd.add_series('비율(%)', pcts)  # ← '비율(%)'가 차트 제목으로 렌더링
```

**해결**: 시리즈명을 공백으로 변경
```python
cd.add_series(' ', pcts)  # ← 차트 제목 안 보임
```

---

### 오류 #5: `text_frame.clear()` 관련 (v1 초기)

**증상**: 커스텀 데이터 라벨 설정 시 XML 구조 손상

**원인**:
```python
tf = pt_dl.text_frame
tf.clear()           # ← <a:bodyPr>, <a:lstStyle> 등 필수 요소까지 삭제
p = tf.paragraphs[0] # ← 빈 컬렉션에서 인덱싱 → 비정상 XML
```

**해결**: `clear()` 호출 금지, `add_run()`만 사용
```python
tf = pt_dl.text_frame
p = tf.paragraphs[0]  # 기존 단락 활용
run = p.add_run()
run.text = "50.5% (505)"
```

---

## 핵심 교훈 요약

| #   | 교훈                                | 규칙                               |
| --- | ----------------------------------- | ---------------------------------- |
| 1   | python-pptx 내부 XML 직접 조작 금지 | **표준 API만 사용**                |
| 2   | 축 삭제 대신 투명 처리              | 배경색 동일 폰트 + 최소 크기       |
| 3   | `text_frame.clear()` 금지           | `add_run()`만 사용                 |
| 4   | 시리즈명은 공백 사용                | 차트 제목 표시 방지                |
| 5   | 2번째 시리즈로 데이터 포함 시       | 라벨 개별 제어 불가 주의           |
| 6   | 생성 후 검증 필수                   | `Presentation(파일)` 재로드 테스트 |
