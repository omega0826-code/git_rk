# 📋 변경 이력 (Changelog)

## v4 — 2026-02-24 (현재)
- 흰 배경 테마 적용 (White Clean)
- 검정/진회색 라벨 전환
- 장식 바(accent bar) 제거
- 빈도 시리즈 중복 라벨 오류 해결
- 파일명 타임스탬프 `_YYMMDD_HHMM` 추가
- 무결성 자동 검증 추가

## v3 — 2026-02-24
- python-pptx 표준 API only (XML 직접 조작 완전 제거)
- 축 숨김: 투명 처리 (delete 대신)
- text_frame.clear() 제거 → add_run() only

## v2 — 2026-02-24
- ❌ lxml XML 직접 조작 시도 → 데이터 손실 (폐기)

## v1 — 2026-02-24
- 초기 구현: python-pptx + 일부 비호환 속성
- ⚠️ PowerPoint 복구 경고 발생
  - `val_axis.visible`, `val_axis.delete + 속성 충돌`, `chart.chart_style`

## v0 — 2026-02-24
- Matplotlib PNG 그래프 18개 → 이미지 삽입 방식 (편집 불가)
