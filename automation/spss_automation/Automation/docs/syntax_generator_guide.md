# SPSS 범용 Syntax 자동 생성기 — 개발 가이드라인

> **Version**: 1.0.0 | **최종 수정**: 2026-02-26

---

## 1. 개요

`generate_syntax.py`는 JSON 설정 파일을 기반으로 SPSS 분석 syntax(`.md` + `.sps`)를 자동 생성하는 범용 도구입니다.

---

## 2. 버전 관리 규칙 (Semantic Versioning)

| 변경 유형                 | 버전 증가      | 예시                                        |
| ------------------------- | -------------- | ------------------------------------------- |
| 버그 수정                 | PATCH (0.0.+1) | CP949 문자 대체 추가, 필터 연산자 오류 수정 |
| 신규 item type 추가       | MINOR (0.+1.0) | `scale`, `recode` type 추가                 |
| JSON 스키마 변경 (비호환) | MAJOR (+1.0.0) | `sections` 구조 변경                        |

### 파일 헤더 규칙

```python
"""
generate_syntax.py - SPSS 범용 분석 Syntax 자동 생성기
Version: 1.0.0
Created: 2026-02-26
Updated: 2026-02-26
"""
```

---

## 3. 업데이트 절차

1. **이슈 등록**: 버그 또는 기능 요청 확인
2. **CHANGELOG.md에 기록**: `## [Unreleased]` 섹션에 추가
3. **코드 수정**: 관련 함수 수정 또는 신규 함수 추가
4. **회귀 테스트**: Company + Student 2개 케이스 재실행
5. **troubleshooting.md 업데이트**: 발생한 오류 상세 기록
6. **CHANGELOG.md 완료**: 버전 번호와 날짜 확정
7. **파일 헤더 업데이트**: Version, Updated 필드 수정

---

## 4. 회귀 테스트 방법

```bash
# 기업체조사
python generate_syntax.py "Syntax/Daegu_UKM/company/analysis_config.json"

# 재학생조사
python generate_syntax.py "Syntax/Daegu_UKM/student/analysis_config.json"
```

**검증 항목:**
- [ ] 두 케이스 모두 에러 없이 생성 완료
- [ ] SPS 파일 CP949 인코딩 정상
- [ ] SPSS에서 한글 정상 표시
- [ ] 매크로 실행 시 통계표 정상 출력

---

## 5. 신규 item type 추가 방법

1. `render_item()` 함수에 새로운 `elif item_type == "새유형":` 분기 추가
2. JSON 설정 예시를 `analysis_config.json`에 추가
3. 이 문서의 "지원 item type" 섹션의 표에 추가
4. `troubleshooting.md`에 관련 주의사항 기록

### 현재 지원 item type

| type        | 매크로    | 설명                |
| ----------- | --------- | ------------------- |
| `freq`      | freqt     | 단수응답 빈도+비율  |
| `freq_each` | freqt × N | 다수 변수 각각 빈도 |
| `mean`      | cm1t      | 다수 변수 평균      |
| `multi`     | PRT       | 복수응답            |
| `scale`     | freqm2t   | 척도(빈도+평균)     |
| `recode`    | RECODE    | 변수 리코딩         |

---

## 6. 코딩 규칙

- **Type Hinting**: 함수 인자/반환값에 타입 힌트 필수
- **Docstring**: Google Style
- **상수**: 대문자 CONSTANT_CASE
- **인코딩**: UTF-8 기본, CP949 출력 시 `CP949_REPLACE_MAP` 자동 적용
