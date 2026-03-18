# MD→HWPX 변환 트러블슈팅 리포트

> 작성일: 2026-03-18

## 문제 요약

첫 번째 변환 결과물을 한컴오피스에서 열었을 때, 원하는 출력 형식과 3가지 차이점이 발견됨.

---

## Issue 1: 템플릿 원본 텍스트 잔존

### 증상

출력 문서 최상단에 "1. 고용 전망" (bix_test.hwpx의 원본 첫 문단 텍스트)이 표시됨.
새 워딩 보고서 본문 위에 불필요한 텍스트가 출력.

### 원인

`build_section_xml()`에서 템플릿의 첫 문단(`<hp:p>`)을 **통째로 복사**하여 secPr을 가져왔기 때문.
첫 문단에는 secPr(페이지 설정) 뿐 아니라 원본의 텍스트 run도 포함되어 있었음.

```python
# 수정 전 (문제 코드)
first_p = child          # 문단 전체를 복사 → 텍스트 포함
secpr_xml = first_p
sec.append(secpr_xml)    # 원본 텍스트까지 함께 삽입됨
```

### 해결

첫 문단에서 `<hp:secPr>`과 `<hp:ctrl>` (colPr 포함) 요소만 별도로 추출하고,
새로 생성한 빈 문단에 해당 요소만 삽입하는 방식으로 변경.

```python
# 수정 후
for run in child.findall(f'{{{HP}}}run', NS):
    sp = run.find(f'{{{HP}}}secPr', NS)  # secPr만 추출
    ct = run.find(f'{{{HP}}}ctrl', NS)   # colPr만 추출

# 새 빈 문단에 삽입
first_run.append(secpr_elem)
first_run.append(ctrl_elem)
empty_t = etree.SubElement(first_run, f'{{{HP}}}t')  # 빈 텍스트
```

---

## Issue 2: 불릿 기호 불일치

### 증상

출력에서 불릿 항목이 `  · 텍스트` 형태로 표시됨.
원하는 형식은 `○ 텍스트` (원형 마커).

### 원인

`build_section_xml()`에서 불릿 텍스트 앞에 `'  · '`를 하드코딩으로 추가했음.

### 해결

불릿 기호를 `'○ '`로 변경.

```diff
- text = '  · ' + text
+ text = '○ ' + text
```

---

## Issue 3: blockquote에서 마크다운 서식 잔존

### 증상

인용문 `> **생성일시**: 260317_2201` 이 HWPX에서 `**생성일시**: 260317_2201`로 표시됨.
`**` 마크다운 굵기 기호가 그대로 출력.

### 원인

불릿(`MdBullet`)에서는 `**bold**` 서식을 제거했지만, 인용문(`MdBlockquote`) 파서에는 서식 제거 로직이 빠져있었음.

### 해결

인용문 파싱 시에도 동일한 마크다운 서식 제거 로직 추가.

```python
bq_text = re.sub(r'\*\*(.+?)\*\*', r'\1', bq_text)
bq_text = re.sub(r'\*(.+?)\*', r'\1', bq_text)
```

---

## 수정 파일

| 파일 | 변경 내용 |
|------|-----------|
| `md_to_styled_hwpx.py` L196~238 | secPr 추출 로직 전면 개선 |
| `md_to_styled_hwpx.py` L250 | 불릿 기호 `·` → `○` |
| `md_to_styled_hwpx.py` L103~104 | blockquote 마크다운 서식 제거 추가 |

## 추가 참고: CMD 한글 파일명 문제

Windows CMD(CP949)에서 한글 파일명을 argparse로 전달하면 인코딩이 깨져 `OSError: [Errno 22] Invalid argument` 발생.
**해결**: Python wrapper 스크립트에서 `subprocess.run()`으로 호출하여 Unicode 경로를 정상 전달.

---

## 2차 수정 (v3)

> 작성일: 2026-03-18

v2 결과물 확인 후 추가 문제 4건 발견.

### Issue 4: 불릿 기호 글꼴 불일치

**증상**: `○` (U+25CB)가 한컴오피스에서 빈 원으로만 렌더링, 원하는 기호와 다름.
**해결**: 유니코드 `U+F06D` (특수문자표 기준)로 변경.

```diff
- text = '○ ' + text
+ text = '\uF06D ' + text
```

### Issue 5: 소제목(h2/h3)에 글머리표 표시

**증상**: "A1. RISE사업 인지 여부" 등 소제목 앞에도 ○ 글머리표가 표시됨.
**원인**: h2/h3가 본문과 동일한 `paraPrIDRef=56` (JUSTIFY 160%)을 사용하여, 글머리표 스타일이 적용됨.
**해결**: h2/h3의 `paraPrIDRef`를 `62` (LEFT 160%)로 변경하여 본문 스타일과 분리.

### Issue 6: 소제목 텍스트에 불필요한 번호/괄호 포함

**증상**: `A1. RISE사업 인지 여부 (N=140, 단수 응답)` 전체가 출력됨.
**원하는 출력**: `RISE사업 인지 여부`
**해결**: h2 텍스트 변환 시 정규식으로 접두사/접미사 제거.

```python
text = re.sub(r'^[A-Z]\d+(?:-\d+)?(?:\(\d+\))?\.\s*', '', text)  # A1. 제거
text = re.sub(r'\s*\(N=\d+[^)]*\)\s*$', '', text)                 # (N=xxx) 제거
```

### Issue 7: 불필요한 h1 타이틀 및 메타데이터 출력

**증상**: "통계 분석 결과 워딩 보고서", "생성일시: 260317_2201" 가 문서 상단에 출력됨.
**해결**: `build_section_xml()`에서 h1 heading과 `생성일시` blockquote를 필터링.

```python
if isinstance(elem, MdHeading) and elem.level == 1:
    continue
if isinstance(elem, MdBlockquote) and '생성일시' in elem.text:
    continue
```

### 수정 파일 (2차)

| 파일 | 변경 내용 |
|------|-----------|
| `md_to_styled_hwpx.py` L249~253 | h1/blockquote 불필요 요소 필터링 |
| `md_to_styled_hwpx.py` L268~270 | h2 텍스트 번호/괄호 정규식 제거 |
| `md_to_styled_hwpx.py` L273 | 불릿 기호 `○` → `\uF06D` |
| `profiles/bix/style_guide.json` | h2/h3 `paraPrIDRef` 56 → 62 |

---

## 3차 수정 (v4)

> 작성일: 2026-03-18

v3 결과물 확인 후 추가 문제 2건 발견 + 디자인 변경 1건.

### Issue 8: 본문 글머리표 이중 표시

**증상**: 불릿 항목에 `○ ○ 텍스트` 형태로 글머리표가 2개 표시됨.
**원인**: paraPr=56 스타일 자체에 글머리표가 설정되어 있는데, 코드(`'\uF06D ' + text`)로 텍스트에도 기호를 추가하여 이중 표시.
**해결**: 텍스트 삽입 코드(`'\uF06D ' + text`) 삭제. paraPr 스타일의 글머리표만 사용.

### Issue 9: h2 문항 번호 누락

**증상**: 소제목이 "제목"만 표시, "A1. 제목" 형태의 문항 번호가 누락됨.
**원인**: v3에서 `re.sub(r'^[A-Z]\d+...')` 정규식으로 접두사를 제거했기 때문.
**해결**: 접두사 제거 코드 삭제. `(N=xxx)` 접미사 제거만 유지.

### 디자인 변경: h2 소제목 14pt

**변경**: 소제목 폰트 크기를 12pt → 14pt로 변경.
**방법**: `style_guide.json`의 `role_mapping.h2.charPrIDRef`를 `53` (12pt HY중고딕 Bold) → `39` (14pt 한양견고딕)으로 변경.

### 수정 파일 (3차)

| 파일 | 변경 내용 |
|------|-----------|
| `md_to_styled_hwpx.py` L269~273 | h2 접두사 제거 코드 삭제, 접미사 제거만 유지 |
| `md_to_styled_hwpx.py` L276~278 | 불릿 텍스트 `\uF06D` 삽입 코드 삭제 |
| `profiles/bix/style_guide.json` | h2 `charPrIDRef` 53 → 39 (14pt) |
