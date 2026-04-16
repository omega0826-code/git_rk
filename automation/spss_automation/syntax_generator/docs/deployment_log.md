# 배포 작업 이력 — SPSS Syntax 자동 생성 도구

배포 준비, 버그 수정, 릴리즈 작업의 이력을 시간순으로 기록합니다.  
코드 변경 이력은 [`../CHANGELOG.md`](../CHANGELOG.md)에서, 오류 이력은 [`troubleshooting.md`](troubleshooting.md)에서 관리합니다.

---

## DEP-002 — v1.0.1 배포 준비 (2026-04-15)

### 작업 개요
v1.0.0 릴리즈 후 배포 검토 과정에서 발견된 버그 수정 및 누락 파일 보완.

### 검토 결과 요약

| 구분 | 파일 | 문제 | 조치 |
|------|------|------|------|
| 버그 | `scripts/generate_macros.py` | `DEFAULT_TEMPLATE` 경로 불일치 (`../Macro/lib/` → 실제 `../macros/`) | 경로 수정 |
| 버그 | `macros/common_macros_template.sps` | `cot`, `cst` 매크로에 `'업체수'` 하드코딩 | `{{VALIDN_LABEL}}` 교체 |
| 누락 | `examples/` | `analysis_config_sample.json` 없음 | 전체 item type 예시 신규 작성 |
| 누락 | `examples/` | `guideline_sample.csv` 없음 | 샘플 설문 CSV 신규 작성 |
| 누락 | 루트 | `CHANGELOG.md` 없음 (README 링크 깨짐) | 루트 CHANGELOG.md 신규 생성, README 링크 수정 |
| 누락 | 루트 | `requirements.txt` 없음 | Python 버전/의존성 명세 신규 작성 |

### 변경 파일 목록

```
수정:
  scripts/generate_macros.py          DEFAULT_TEMPLATE 경로 수정, v1.0.1 버전업
  macros/common_macros_template.sps   cot/cst 하드코딩 교체
  README.md                           CHANGELOG 링크 수정 및 macros/CHANGELOG 링크 추가
  docs/troubleshooting.md             TS-006, TS-007 신규 등록

신규:
  CHANGELOG.md                        루트 변경 이력 파일
  requirements.txt                    의존성 및 Python 버전 명세
  examples/analysis_config_sample.json  generate_syntax.py 설정 예시
  examples/guideline_sample.csv        guideline_to_sps.py 입력 예시
  docs/deployment_log.md              이 파일
```

### 배포 후 권장 검증 절차

```bash
# 1. generate_macros.py 기본 경로 동작 확인 (버그 수정 핵심)
cd scripts
python generate_macros.py ../macros/banner_config_sample.json -o ../logs/test_macro.sps
# → [OK] 매크로 생성 완료: ... 출력 확인
# → 생성 파일에서 '업체수' 잔존 여부 확인
grep "업체수" ../logs/test_macro.sps   # 결과 없어야 정상

# 2. guideline_to_sps.py 샘플 실행
python guideline_to_sps.py ../examples/guideline_sample.csv \
  -o ../logs/test_label.sps --title "샘플테스트"
# → 변수 라벨/값 라벨 개수 확인

# 3. 템플릿 플레이스홀더 미치환 잔존 여부 확인
grep "{{" ../logs/test_macro.sps   # 결과 없어야 정상
```

### 다음 배포 전 체크리스트

- [ ] `scripts/` 내 모든 스크립트 `--version` 출력 확인
- [ ] 회귀 테스트 2케이스 (기업/학생) 재실행 (`docs/syntax_generator_guide.md` §4 참조)
- [ ] `CHANGELOG.md` `[Unreleased]` 섹션 → 버전/날짜 확정
- [ ] `generate_macros.py` 헤더 `Updated` 날짜 갱신
- [ ] ZIP 압축 전 `logs/` 폴더 내 테스트 생성 파일 정리

---

## DEP-001 — v1.0.0 최초 릴리즈 (2026-02-26)

### 작업 개요
SPSS 자동화 도구 전체 구조 설계 및 초도 개발 완료. 스크립트 5종, 매크로 43개, 문서 7종 포함.

### 주요 결정 사항

| 항목 | 결정 내용 | 이유 |
|------|-----------|------|
| 기본 인코딩 | CP949 (EUC-KR) | SPSS 25.0 한국어 Windows 호환 필수 |
| 파일 I/O | 바이너리 모드 | CRLF 줄바꿈 보존 (TS-003 참조) |
| 매크로 제공 방식 | 템플릿(방식B) + 수동(방식A) 병행 | 자동화 가능하면서 레거시 호환 |
| 설정 형식 | JSON | 계층 구조 표현, 사람이 읽기 편함 |
| 문서 형식 | Markdown | git 관리, VS Code 미리보기 |

### 포함 파일

```
scripts/
  guideline_to_sps.py    CSV → VARIABLE/VALUE LABELS .sps
  generate_syntax.py     JSON → 분석 syntax .sps + .md
  generate_macros.py     JSON + template → 매크로 .sps
  sps_to_md.py           .sps → .md 변환 (배치 포함)
  md_to_sps.py           .md → .sps 역변환 (배치 포함)

macros/
  common_macros.sps           복사 붙여넣기용 매크로 43개
  common_macros_template.sps  자동 생성용 플레이스홀더 템플릿
  common_macros_reference.md  매크로 레퍼런스 문서
  macro_user_guide.md         매크로 사용 가이드
  banner_config_sample.json   배너 설정 샘플
  CHANGELOG.md                매크로 전용 변경 이력

examples/
  short_labels_sample.json    간략 라벨 JSON 예시

docs/
  syntax_generator_guide.md   개발 가이드라인 + 업데이트 절차
  syntax_generator_report_20260226.md  개발 보고서
  error_report_roundtrip_20260226.md   왕복 변환 검증 보고서
  sps_md_conversion_guide.md  변환 도구 사용 가이드
  report.md                   프로젝트 요약 보고서
  troubleshooting.md          트러블슈팅 DB (TS-001 ~ TS-005)
```
