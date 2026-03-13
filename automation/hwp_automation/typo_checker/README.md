# HWPX 관련 도구 모음

기존 프로젝트에서 작업한 HWPX 관련 코드 및 문서를 정리한 폴더입니다.

---

## 📁 01_hwpx_parser — HWPX 파서

> 출처: `project/25_121_ulsan/HWPX/`

HWPX 파일(ZIP 기반 XML 패키지)에서 텍스트, 표, 이미지, 제목을 추출하는 파서입니다.

| 파일                               | 설명                                                                                                   |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `hwpx_parser.py`                   | HWPX 파서 본체 (872줄) — HwpxReader, TextExtractor, HeadingDetector, TableExtractor, ImageExtractor 등 |
| `hwpx_guideline.md`                | HWPX 구조 분석 및 파싱 가이드라인                                                                      |
| `hwpx_parser_dev_guide_v1.0.md`    | 개발자용 가이드                                                                                        |
| `hwpx_parser_usage_guide_v1.0.md`  | 사용법 가이드                                                                                          |
| `hwpx_parser_error_report_v1.0.md` | 에러/트러블슈팅 리포트                                                                                 |
| `hwpx_structure_log.txt`           | HWPX 내부 구조 로그                                                                                    |

---

## 📁 02_typo_checker — HWPX 오타 검사기 (v1 · 프로젝트 전용)

> 출처: `project/25_n33_MunKyung/hwpx/`

문경 프로젝트 전용 오타 검사기. HWPX 문서를 파싱한 후 규칙 기반 오타 검사 및 표 데이터 검증을 수행합니다.

| 파일                     | 설명                                                             |
| ------------------------ | ---------------------------------------------------------------- |
| `typo_checker.py`        | 오타 검사 본체 (491줄) — TextChecker, TableChecker, ReportWriter |
| `run_parse.py`           | HWPX 파싱 실행 스크립트                                          |
| `page_mapper.py`         | 페이지 매핑 유틸리티 (XML pageBreak 방식)                        |
| `page_mapping.json`      | 페이지 매핑 데이터                                               |
| `hwpx_parsing_report.md` | 파싱 결과 리포트                                                 |
| `typo_check_report.md`   | 오타 검사 결과 리포트                                            |

---

## 📁 03_md_to_hwpx — 마크다운 → HWPX 변환기

> 출처: `project/25_044_Traditional ingredien/`

마크다운 문서를 pyhwpx(COM 자동화)를 통해 HWPX 파일로 변환합니다.

| 파일                   | 설명                                             |
| ---------------------- | ------------------------------------------------ |
| `md_to_hwpx.py`        | 변환기 본체 (455줄) — MarkdownParser, HwpxWriter |
| `md_to_hwpx_리포트.md` | 변환 프로세스 리포트                             |

---

## 📁 04_proofreading — HWPX 범용 교정 도구 (v2 · 신규)

> 출처: `Hwp Automation/Proofreading/`  
> 추가일: 2026-02-24

`01_hwpx_parser`와 `02_typo_checker`를 통합하여 **임의의 HWPX 파일**을 자동 파싱 → 오타 검사 → 리포트 생성하는 범용 도구입니다. pyhwpx COM 자동화 기반 **페이지 번호 매핑** 및 **CSV 출력** 기능을 포함합니다.

| 파일                            | 설명                                                                                            |
| ------------------------------- | ----------------------------------------------------------------------------------------------- |
| `run_typo_check.py`             | 범용 오타 검사 스크립트 (770줄) — PageMapper, TextChecker, TableChecker, ReportWriter, CSV 출력 |
| `검사결과_종합리포트_sample.md` | 검사 결과 요약 리포트 샘플                                                                      |
| `스크립트_개발리포트.md`        | 스크립트 개발 과정, 오류 수정, 기능 업그레이드 리포트                                           |

### 사용법

```bash
python run_typo_check.py <hwpx_파일> [--output-dir DIR] [--no-page-map]
```

### 02_typo_checker와의 차이

| 항목        | 02 (v1)                | 04 (v2)                         |
| ----------- | ---------------------- | ------------------------------- |
| 대상        | 문경 프로젝트 전용     | **범용** (임의 HWPX)            |
| 페이지 매핑 | XML pageBreak (부정확) | **pyhwpx goto_page()** (정확)   |
| 출력 형식   | Markdown만             | **Markdown + CSV**              |
| 페이지 표시 | 없음                   | **페이지 번호 컬럼**            |
| 실행 방식   | 파싱/검사 분리         | **통합 파이프라인**             |
| CLI 옵션    | 없음                   | `--output-dir`, `--no-page-map` |

---

## 📁 99_spell_checker_plan — 맞춤법 사전 연동 기획 (미구현)

> 상태: 📋 계획 단계

향후 추가 예정인 **맞춤법 사전 연동 + 형태소 분석** 기능의 개발 기획 문서입니다.

| 파일                            | 설명                                                            |
| ------------------------------- | --------------------------------------------------------------- |
| `개선안3_맞춤법_형태소_분석.md` | 구현 방안 (py-hanspell, hunspell, kiwi), 코드 예시, 단계별 전략 |

### 계획 요약

| 단계  | 도구                 | 목적                            |
| ----- | -------------------- | ------------------------------- |
| 1단계 | **kiwi** (kiwipiepy) | 띄어쓰기 교정                   |
| 2단계 | **py-hanspell**      | 맞춤법 검사 (온라인/네이버 API) |
| 3단계 | **hunspell**         | 맞춤법 검사 (오프라인 사전)     |

---

## 변경 이력

변경 이력은 `CHANGELOG.md`를 참조하세요.
