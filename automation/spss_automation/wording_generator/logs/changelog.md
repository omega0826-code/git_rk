# Changelog

## [1.2.1] - 2026-03-17 22:01

### 변경
- **'~의 경우' 쉼표 제거**: `~의 경우,` → `~의 경우` (쉼표 없이)
  - Before: `IT/SW의 경우, 정보가 없어서 비율이`
  - After: `IT/SW의 경우 정보가 없어서 비율이`
- 프롬프트(`survey_wording_prompt.md`) 패턴/규칙/샘플 동기화

→ [Troubleshooting #5](../docs/troubleshooting.md#5-특성별-문장-형식-변경)

---

## [1.2.0] - 2026-03-17 21:55

### 변경
- **특성별 문장 형식 규칙 적용**: 프롬프트 및 스크립트 동시 반영
  - 분석 기준 뒤 쉼표: `RISE 사업별로는,`
  - 대상 뒤 `~의 경우` 분리: `미참여의 경우`
  - `~ 비율이 00%로` 명확 표현: `예 비율이 35.7%인`
- **프롬프트 업데이트**: `survey_wording_prompt.md`에 문장 형식 규칙 섹션 추가

→ [Troubleshooting #5](../docs/troubleshooting.md#5-특성별-문장-형식-변경)

---

## [1.1.0] - 2026-03-17 21:40

### 변경
- **한글 조사 자동 선택**: `이(가)`, `과(와)`, `을(를)`, `은(는)`, `으로/로` → 받침 기반 자동

### 추가
- `_has_batchim()`, `_josa()` 함수

### 버그 수정
- 조사 이중 표기 해결 → [Error Report #2](error_report.md#2-조사-이중-표기)

---

## [1.0.0] - 2026-03-17 21:33

### 추가
- `generate_wording.py` 초기 릴리즈
- 교차표 MD 파싱 → 보고서 워딩 자동 생성
- `config.py`, `run_now.py`

### 알려진 이슈
- 한글 파일명 인코딩 → `run_now.py` 우회 | [Error Report #1](error_report.md#1-한글-파일명-인코딩-실패)
- 조사 이중 표기 → v1.1.0 수정 | [Error Report #2](error_report.md#2-조사-이중-표기)
