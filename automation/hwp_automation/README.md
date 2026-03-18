# hwp_automation — HWPX 자동화 도구 모음

HWPX 파일(한컴 한글 ZIP 기반 패키지) 관련 자동화 도구를 모아 놓은 디렉토리입니다.

---

## 📁 모듈 구조

```
hwp_automation/
├── body_modifier/      ← HWPX 본문 수정 파이프라인
├── hwpx_parser/        ← HWPX 파일 파싱 (텍스트, 표, 이미지, 제목)
├── md_to_hwpx/         ← 마크다운 → HWPX 변환기
├── proofreading/       ← HWPX 범용 교정 도구 (파싱+오타검사+페이지매핑)
├── typo_checker/       ← 프로젝트 전용 오타 검사기 (문경)
├── plan/               ← 향후 기능 기획
├── README.md
└── CHANGELOG.md
```

---

## 📁 body_modifier — HWPX 본문 수정 자동화

HWPX 파일의 본문을 분석 → 규칙 기반 수정 → 새 HWPX 생성하는 3단계 파이프라인.

| 모듈 | 역할 |
|------|------|
| `parser.py` | HWPX 구조 분석 |
| `modifier.py` | 규칙 기반 수정 (삽입, 교체, 삭제, 스타일 변경) |
| `builder.py` | HWPX ZIP 패키징 |

```bash
python run_body_mod.py --input 원본.hwpx --spec config/sample_spec.json --output 결과.hwpx
```

---

## 📁 hwpx_parser — HWPX 파서

> 출처: `project/25_121_ulsan/HWPX/`

HWPX 파일(ZIP 기반 XML 패키지)에서 텍스트, 표, 이미지, 제목을 추출하는 파서.

| 파일 | 설명 |
|------|------|
| `hwpx_parser.py` | 파서 본체 (872줄) — HwpxReader, TextExtractor, HeadingDetector, TableExtractor, ImageExtractor |
| `hwpx_guideline.md` | HWPX 구조 분석 및 파싱 가이드라인 |
| `hwpx_parser_dev_guide_v1.0.md` | 개발자용 가이드 |
| `hwpx_parser_usage_guide_v1.0.md` | 사용법 가이드 |
| `hwpx_parser_error_report_v1.0.md` | 에러/트러블슈팅 리포트 |

```bash
python hwpx_parser.py <hwpx_파일> [--text-only] [--count-tables] [--extract-table N]
```

---

## 📁 md_to_hwpx — 마크다운 → HWPX 변환기

> 출처: `project/25_044_Traditional ingredien/`

마크다운 문서를 pyhwpx(COM 자동화)를 통해 HWPX 파일로 변환.

| 파일 | 설명 |
|------|------|
| `md_to_hwpx.py` | 변환기 본체 (455줄) — MarkdownParser, HwpxWriter |
| `md_to_hwpx_리포트.md` | 변환 프로세스 리포트 |

---

## 📁 proofreading — HWPX 범용 교정 도구 (v2)

`hwpx_parser`와 `typo_checker`를 통합하여 **임의의 HWPX 파일**에 대해 파싱 → 오타 검사 → 리포트 생성을 자동 수행.

| 파일/폴더 | 설명 |
|-----------|------|
| `run_typo_check.py` | 범용 오타 검사 스크립트 (770줄) — 5단계 파이프라인 |
| `docs/` | 스크립트 개발리포트, 검사결과 종합리포트 |
| `output/` | 실행 산출물 (파싱 결과, CSV, Markdown 리포트) |

```bash
python run_typo_check.py <hwpx_파일> [--output-dir DIR] [--no-page-map]
```

### typo_checker와의 차이

| 항목 | typo_checker (v1) | proofreading (v2) |
|------|--------------------|--------------------|
| 대상 | 문경 프로젝트 전용 | **범용** (임의 HWPX) |
| 페이지 매핑 | XML pageBreak (부정확) | **pyhwpx goto_page()** (정확) |
| 출력 형식 | Markdown만 | **Markdown + CSV** |

---

## 📁 typo_checker — 프로젝트 전용 오타 검사기 (v1)

> 출처: `project/25_n33_MunKyung/hwpx/`

문경 프로젝트 전용. HWPX 문서를 파싱한 후 규칙 기반 오타 검사 및 표 데이터 검증.

| 파일 | 설명 |
|------|------|
| `typo_checker.py` | 오타 검사 본체 (491줄) |
| `run_parse.py` | HWPX 파싱 실행 스크립트 |
| `page_mapper.py` | 페이지 매핑 유틸리티 |

---

## 📁 plan — 향후 기능 기획

### spell_checker_plan — 맞춤법 사전 연동 (미구현)

| 단계 | 도구 | 목적 |
|------|------|------|
| 1단계 | **kiwi** (kiwipiepy) | 띄어쓰기 교정 |
| 2단계 | **py-hanspell** | 맞춤법 검사 (온라인/네이버 API) |
| 3단계 | **hunspell** | 맞춤법 검사 (오프라인 사전) |

---

## 변경 이력

변경 이력은 `CHANGELOG.md`를 참조하세요.
