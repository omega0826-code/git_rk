# Changelog

## [1.1.0] - 2026-03-17 20:05

### 변경
- **교차표 통합 테이블**: 교차표 보고서(`_cross.md`)에서 요약표+상세표 2개 → 전체행 포함 **통합 1개 테이블** 형식으로 변경. 전체 행은 볼드체 강조
- **출력 파일명 자동 생성**: `output_prefix` 고정값 제거, 원본 파일명에서 자동 추출 (예: `(output)기업체_대구한의대...xls` → `report_기업체_대구한의대_rise_260310_송부_YYMMDD_HHMM.md`)
- **XLS 비율 백분율 변환**: xlrd `formatting_info=True`로 셀 서식 감지, 소수(0.4545...) → 원본 소수점 자리수 백분율(45.5%) 변환

### 추가
- `_is_pct_format()`, `_get_pct_decimals()` 헬퍼 함수
- `_format_unified_table()` 통합 테이블 포맷 함수

### 제거
- `_format_subgroup_section()` (→ `_format_unified_table()`로 대체)
- `config.py`의 `output_prefix` 항목 (자동 생성으로 불필요)

---

## [1.0.0] - 2026-03-17 18:10

### 추가
- `spss_excel_to_md.py` 메인 변환 스크립트 초기 릴리즈
- XLS/CSV 자동 판별 로드
- 블록 유형 레지스트리 패턴 (빈도표/교차표/평균표)
- 요약 + 교차표 2파일 동시 생성
- 실행 기록(CSV), 에러 리포트(MD) 자동 로깅
