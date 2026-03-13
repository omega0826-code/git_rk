# 테마 커스터마이징 가이드

## JSON 구조 개요

| 섹션 | 설명 |
|---|---|
| `slide` | 슬라이드 크기, 배경색 |
| `font` | 폰트명, 각 요소별 크기 (8종) |
| `colors` | 제목/라벨/축선/팔레트 색상 |
| `hbar/pie/radar/stacked` | 차트별 위치, 크기, 옵션 |

## 색상 팔레트 교체

`chart_palette`는 10색 배열, RGB 형식:
```json
"chart_palette": [
  [59, 130, 246],     // accent1: 파란색
  [16, 185, 129],     // accent2: 초록색
  ...
]
```

## 차트 사이즈 조절

각 차트 유형별 4개 값 (인치 단위):
- `chart_left`: 왼쪽 여백
- `chart_top`: 위쪽 여백
- `chart_width`: 가로 길이
- `chart_height`: 세로 길이

## 폰트 변경

```json
"font": {
  "name": "맑은 고딕",      // 다른 폰트명으로 교체
  "title_size": 22,          // 제목
  "subtitle_size": 12,       // 부제 (n=xxx)
  "label_size": 10,          // 축 라벨
  "data_label_size": 10,     // 데이터 라벨
  "legend_size": 11,         // 범례
  "page_num_size": 10,       // 페이지 번호
  "stacked_label_size": 8    // 누적막대 라벨
}
```

## 새 테마 만들기
1. `themes/white_clean.json` 복사
2. 원하는 값 수정
3. `themes/my_theme.json` 으로 저장
4. `--theme my_theme` 으로 실행
