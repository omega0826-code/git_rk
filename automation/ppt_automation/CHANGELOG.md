# Changelog

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
