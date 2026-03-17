# Changelog

## [1.2.0] - 2026-03-16

### Added
- `dhu_cobalt.json`: 대구한의대 코발트 테마 신규 추가 (148×78mm, 돋움 8pt)
- `rule_satisfaction.py`: 제목에 '만족도' 포함 시 세로막대 우선 적용 (우선순위 3)
- `chart_builder.py`: `_remove_extra_series()` XML 시리즈 제거 헬퍼 추가
- `chart_builder.py`: `_lightness_variants()` 파이차트 명도 변형 색상 생성

### Changed
- 차트 유형 판별 규칙 변경:
  - **파이**: 항목 ≤2개 (우선순위 5) ← 기존: ≤3개
  - **가로막대**: 항목 ≥6개 (우선순위 20) ← 기존: ≥7개
  - **만족도 키워드**: 제목에 '만족도' 포함 시 vbar 우선 (우선순위 3) [신규]
- 데이터 라벨 형식 변경:
  - **세로막대**: `비율%\n(빈도)` (줄바꿈)
  - **가로막대**: `비율% (빈도)` (한 줄)
  - **파이차트**: `카테고리 비율% (빈도)` (바깥쪽)
- 빈도 시리즈 처리: `format.fill.background()` → `_remove_extra_series()` XML 완전 제거
- CategoryChartData에 비율+빈도 2시리즈 추가 (편집용 데이터 보존)
- 모든 차트의 시리즈 이름을 `' '`로 통일 (자동 제목 표시 방지)

---

## [1.1.0] - 2026-03-16

### Added
- `rule_vbar.py`: 세로막대(vbar) 차트 규칙 신규 추가 (기본 폴백, 항목 ≤6개)
- `chart_builder.py`: `add_vbar()` 세로막대 차트 빌더 메서드 추가
- 테마 JSON 2종(`white_clean`, `dark_premium`)에 `vbar` 레이아웃 설정 추가
- `theme_viewer.html`에 세로막대 프리뷰 탭 추가

### Changed
- 차트 유형 판별 규칙 전면 재설정:
  - **파이**: 항목 ≤3개 (우선순위 5) ← 기존: 항목 ≤6 + 합계 ~100% 또는 키워드
  - **레이더**: 제목에 '레이더' 포함 (우선순위 10) ← 기존: 인식 수준, 평균 점수 등 키워드
  - **누적(스택)**: 제목에 '누적' 포함 (우선순위 15) ← 기존: 대학교별, 학교별 등 키워드
  - **가로막대**: 항목 ≥7개 (우선순위 20) ← 기존: 기본 폴백
  - **세로막대**: 기본 폴백 (우선순위 100) [신규]
- `run_chart.py`: vbar에도 정렬(sort) 파라미터 전달하도록 수정
- `theme_viewer.html`: 기본 차트 유형을 세로막대(vbar)로 변경

---

## [1.0.0] - 2026-03-11

### Added
- `parser/` 모듈: XLS/XLSX 파서 (`parser_xls`), 마크다운 파서 (`parser_md`)
- `chart/` 모듈: Builder + 테마 JSON + chart_rules 플러그인
- 테마 2종: `white_clean`, `dark_premium`
- chart_rules 4종: `rule_pie`, `rule_radar`, `rule_stacked`, `rule_hbar`
- `run_chart.py`: 개별 파이프라인 (CLI, 로그)
- `run_ppt.py`: 통합 파이프라인 (모듈 조합)
- `docs/`: 가이드 5종
- `logs/`: 실행 로그 자동 기록

### Changed
- `scripts/` 폴더 제거 → `chart/` 모듈로 통합

### 버전 규칙
- **MAJOR**: 파이프라인 구조 변경 (호환 안됨)
- **마이너**: 새 모듈/차트 추가 (하위호환)
- **patch**: 버그수정, 테마 추가
