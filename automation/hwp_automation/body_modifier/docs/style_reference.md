# HWPX charPr / paraPr 속성 레퍼런스

## charPr (글자 속성)

`header.xml`의 `<hh:charProperties>` 안에 위치. 각 `<hh:charPr>`이 하나의 글자 스타일.

| 속성 | 설명 | 예시값 |
|------|------|--------|
| `id` | 고유 식별자 | `"22"` |
| `height` | 글자 크기 (1/100pt, 1000 = 10pt) | `"1000"`, `"2000"` |
| `textColor` | 글자 색상 (hex) | `"#000000"`, `"#FF0000"` |
| `bold` | 진하게 | `"0"` 또는 `"1"` |
| `italic` | 기울임 | `"0"` 또는 `"1"` |
| `spacing` | 자간 (1/100pt) | `"-2"` |
| `ratio` | 장평 (%) | `"98"` |

### fontRef (폰트 참조)

`<hh:fontRef>` 하위에 언어별 폰트 지정:
- `hangul` — 한글 폰트 id
- `latin` — 영문 폰트 id

## paraPr (문단 속성)

`header.xml`의 `<hh:paraProperties>` 안에 위치.

| 속성 | 설명 | 예시값 |
|------|------|--------|
| `id` | 고유 식별자 | `"2"` |
| `align.horizontal` | 정렬 | `"justify"`, `"center"`, `"left"` |
| `margin.left` | 왼쪽 여백 | `"0"`, `"800"` |
| `margin.indent` | 들여쓰기 | `"0"`, `"300"` |
| `lineSpacing.value` | 줄 간격 | `"160"` |

## 계층 판단 기준 (예시)

| 계층 | height | bold | align | 비고 |
|------|--------|------|-------|------|
| 대제목 | 2000+ | 1 | center | 가운데 정렬 + 큰 글자 |
| 소제목 | 1200~1800 | 1 | left/justify | 진하게 + 중간 크기 |
| 본문 | 1000 | 0 | justify | 양쪽 정렬 + 일반 크기 |
| 표 텍스트 | 800~1000 | 0 | center | 가운데 정렬 + 작은 글자 |
