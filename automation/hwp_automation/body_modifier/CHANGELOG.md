# CHANGELOG

## [1.0.0] - 2026-03-13

### 신규
- 프로젝트 초기 구조 생성
- `parser.py`: HWPX 구조 분석 (charPr/paraPr 매핑, 본문/표 파싱)
- `modifier.py`: 규칙 기반 본문 수정 엔진 (insert_after/replace_text/change_style/delete_para)
- `builder.py`: HWPX 빌드 (charPr 동적 추가, mimetype ZIP_STORED 보장)
- `run_body_mod.py`: 통합 파이프라인 CLI
- `config/sample_spec.json`: 수정 사양 예시
- `docs/process_overview.md`: 4단계 프로세스 설계 문서

### 검증 완료
- 울산 정성분석 보고서 기업 발언 36건 빨간색 삽입 → validate.py VALID 통과
