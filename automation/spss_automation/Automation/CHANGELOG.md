# CHANGELOG

모든 주요 변경사항은 이 파일에 기록됩니다.
형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/) 기반이며,
[Semantic Versioning](https://semver.org/lang/ko/) 을 따릅니다.

---

## [1.1.0] - 2026-02-26

### Added
- `generate_syntax.py` v1.0.0: JSON 설정 기반 범용 분석 syntax 자동 생성기
  - 6종 item type: `freq`, `freq_each`, `mean`, `multi`, `scale`, `recode`
  - 라벨 SPS 자동 파싱 및 변수 라벨 추출
  - 배너 설정 기반 매크로 블록 자동 생성
  - CP949 인코딩 자동 대체
- `docs/syntax_generator_guide.md`: 개발 가이드라인 (버전관리, 회귀 테스트)
- `docs/troubleshooting.md`: 트러블슈팅 DB (5건 축적)
- `md_to_sps.py`: CP949 특수문자 자동 대체 (`CP949_REPLACE_MAP`)
- `md_to_sps.py`: `--strip-define-blanks` 옵션 (DEFINE 내 빈줄 제거)

### Fixed
- CP949 인코딩 시 `UnicodeEncodeError` (═, ·, – 등 유니코드 문자)
- DEFINE 블록 내 빈 줄로 인한 SPSS 매크로 파싱 오류

### Tested
- 대구한의대 기업체조사 / 재학생조사 2개 케이스 검증 통과

---

## [1.0.0] - 2026-02-26

### Added
- 최초 릴리즈: `guideline_to_sps.py`
- CSV → SPSS 25.0 syntax (.sps) 변환 기능
  - `VARIABLE LABELS` + `VALUE LABELS` 자동 생성
  - `TO` 범위 구문 지원
- CP949 / UTF-8 인코딩 선택 지원
- 간략 라벨 JSON 매핑을 통한 통계표용 라벨 생성
- CLI 인터페이스 (argparse)
- HTML entity 디코딩, 스마트 따옴표 변환, CP949 비호환 문자 치환
- 예시 파일: `examples/short_labels_sample.json`
