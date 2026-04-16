# hwp_automation — 변경 이력 (CHANGELOG)

> 이 문서는 `hwp_automation/` 폴더의 변경 사항을 기록합니다.
> 새로운 기능 추가, 버그 수정, 구조 변경 등을 날짜순으로 관리합니다.

---

## [2026-03-25] 리포트 형식 재설계 (Phase 2)

### ✅ 신규 기능

- **3단계 리포트 구조** — `ReportWriter.write()` 전면 리팩토링
  1. **검사 결과 요약** — 심각도별 + 항목별(A/A-2/B단계) + 파싱 정보
  2. **주요 오타 내용** — 확정 오타 → 반복 빈도 높은 이슈(3건+) → 기타 의심 이슈
  3. **페이지별 오타 검사 결과** — 페이지 단위 그룹핑 + 테이블 출력
- **유형 열 추가** — `CATEGORY_LABELS` 딕셔너리로 category → 한글 유형 매핑
  - `text` → 본문, `spell` → 맞춤법, `table` → 표, `cross` → 교차검증
- **비고 열 + 동일패턴 표시** — 같은 페이지 내 동일 description ≥ 2건 시 `동일패턴(N건)` 표시
- **페이지 내 상대 줄 번호** — `page_boundaries` 기반 위치를 페이지 내 N줄로 변환
- **반복 이슈 그룹핑** — Section 2에서 3건+ 반복 이슈를 대표 3건 + 전체 건수로 요약

### 🔄 변경 사항

- `ReportWriter.__init__()`: `page_boundaries` 파라미터 추가
- `_get_location_label()`: "00페이지 00줄" 형태 라벨 생성
- `_get_page_group_key()`: 줄 범위 폴백 제거, 항상 페이지 단위
- `_get_relative_line_label()`: 페이지 경계 기반 상대 줄 번호 계산
- `main()`: PageMapper에서 페이지 경계 정보 구축 후 ReportWriter에 전달
- Section 2-1/2-3/Section 3 테이블에 유형 열 삽입 (위치↔원문 사이)
- `pyhwpx` 의존성 추가 (pip install pyhwpx)

---

## [2026-03-25] kiwi 기반 맞춤법 검사 추가 (Step 2.5)

### ✅ 신규 기능

- **`SpellChecker` 클래스** — kiwi(kiwipiepy) 기반 띄어쓰기 교정 + 미등록어 탐지
  - `kiwi.space()`: 원문 vs 교정문 diff 비교로 띄어쓰기 오류 탐지
  - `kiwi.tokenize()`: UN 태그 토큰으로 미등록어 탐지 (중복 보고 방지)
- **`--no-spell-check` CLI 옵션** — kiwi 검사 건너뛰기
- **UTF-8 출력 래퍼** — Windows cmd 인코딩 오류 방지

### 🔄 변경 사항

- 파이프라인: 5단계 → **6단계** (Step 2.5 추가)
- 기존 검사 항목(TextChecker, TableChecker)에 영향 없음
- kiwipiepy 미설치 환경에서는 자동 건너뛰기 (try/except)

---
## [2026-03-18] 디렉토리 구조 재편

### 🔄 구조 변경

- `typo_checker/` 하위 5개 폴더를 `hwp_automation/` 직속으로 이동 (번호 접두사 제거)
  - `01_hwpx_parser/` → `hwpx_parser/`
  - `02_typo_checker/` → `typo_checker/`
  - `03_md_to_hwpx/` → `md_to_hwpx/`
  - `04_proofreading/` → 기존 `proofreading/`에 병합
  - `99_spell_checker_plan/` → `plan/spell_checker_plan/`
- `typo_checker/` 상위 폴더 삭제 (하위 모듈 독립)
- `README.md`·`CHANGELOG.md`를 `hwp_automation/` 전체 범위로 재작성

### 📁 proofreading 정리

- `docs/` 폴더 생성: 문서류(개발리포트, 검사결과 리포트) 분리
- `output/`에는 실행 산출물만 보관
- 중복 파일 정리 (스크립트_개발리포트.md)
- 테스트용 HWPX 파일(~11.9MB) 삭제

### 🔧 스크립트 수정

- `proofreading/run_typo_check.py`: PARSER_DIR 경로 → `hwpx_parser/`
- `typo_checker/run_parse.py`: sys.path → `hwpx_parser/`
- `proofreading/docs/스크립트_개발리포트.md`: 경로 참조 업데이트

---

## [2026-02-24 v2.1] 오타 검사 노이즈 감소 (개선안 1, 2)

### 🔄 변경 사항

- **숫자 불일치 검사 고도화** (`_check_number_inconsistency`)
  - 정수부 2자리 → **3자리 이상**(100 이상)으로 필터 강화
  - **연도(1900~2099)** 자동 제외
  - **반올림 차이(±0.5)** 자동 제외
  - 인접 줄(±5) 내 충돌만 보고 (멀리 떨어진 다른 통계는 무시)
  - **결과**: 132건 → ~19건 (86% 감소)

- **괄호 검사 스택 기반 전환** (`_check_bracket_pairs`)
  - 줄 단위 카운트 비교 → **스택 기반 전체 문서 매칭**
  - 실제 짝이 없는 괄호만 보고 (줄이 다를 뿐인 매칭은 자동 처리)
  - **표 데이터 줄** (숫자·쉼표 위주) 자동 건너뛰기
  - **결과**: 34건 → 31건 (9% 감소)

### 📊 전체 효과

| 항목             | v2.0  | v2.1     | 감소     |
| ---------------- | ----- | -------- | -------- |
| 전체 이슈        | 210건 | **94건** | **-55%** |
| 의심 (확인 필요) | 139건 | **26건** | **-81%** |
| 정보 (참고)      | 34건  | **31건** | -9%      |

---

### ✅ 신규 기능

- **`proofreading/run_typo_check.py`** (770줄) 추가
  - `hwpx_parser` + `typo_checker`를 통합한 범용 HWPX 오타 검사 스크립트
  - 5단계 파이프라인: HWPX 파싱 → 페이지 매핑 → 텍스트 검사 → 표 검증 → 리포트/CSV 생성
  - `--no-page-map` 옵션으로 한글 미설치 환경 지원

- **pyhwpx COM 기반 페이지 매핑** (`PageMapper` 클래스)
  - `goto_page()` 역방향 매핑 방식으로 문단→페이지 매핑
  - pyhwpx 미설치 시 XML `pageBreak` 방식으로 자동 폴백

- **CSV 출력** (`write_issues_csv()`)
  - 검사 결과를 UTF-8-BOM CSV로 저장 (Excel 호환)
  - 컬럼: 번호, 페이지, 심각도, 카테고리, 위치, 원문, 설명, 수정제안

### 🐛 해결된 문제

| 문제                          | 원인                                  | 해결                               |
| ----------------------------- | ------------------------------------- | ---------------------------------- |
| CMD 경로 공백 오류            | 공백 포함 경로가 인수에서 분리됨      | `subprocess.run()` 래퍼 사용       |
| CP949 인코딩 오류             | em dash(`—`) 등 유니코드 문자         | `PYTHONIOENCODING=utf-8` 설정      |
| `KeyIndicator()[0]` 오류      | 인덱스 0은 bool(성공여부), 1이 페이지 | 인덱스를 1로 수정                  |
| `visible=False` 페이지 1 고정 | 비표시 모드에서 렌더링 미수행         | `goto_page()` 역방향 매핑으로 전환 |

---

## [2026-02-19] 초기 구조 생성

### ✅ 폴더 정리

- `hwpx_parser/` — HWPX 파서 (출처: 울산 프로젝트)
- `typo_checker/` — 오타 검사기 (출처: 문경 프로젝트)
- `md_to_hwpx/` — 마크다운→HWPX 변환기 (출처: 전통식재료 프로젝트)

<!--
## [YYYY-MM-DD] 변경 제목

### ✅ 신규 기능
- 기능 설명

### 🔄 변경 사항
- 변경 내용

### 🐛 해결된 문제
| 문제 | 원인 | 해결 |
| ---- | ---- | ---- |

### 📋 추가 문서
- 문서 목록
-->
