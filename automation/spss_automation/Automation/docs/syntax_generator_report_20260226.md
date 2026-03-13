# SPSS 범용 Syntax 자동 생성기 — 구현 결과 리포트

> **작성일**: 2026-02-26 | **Version**: 1.1.0

---

## 1. 구현 개요

JSON 설정 파일을 기반으로 SPSS 분석 syntax(`.md` + `.sps`)를 자동 생성하는 **범용 도구**를 구축했습니다.

**참조 케이스**: 대구한의대 기업체조사(Company) + 재학생조사(Student)

---

## 2. 생성/수정된 파일

| 상태 | 파일                                                                                                 | 크기  | 역할                          |
| ---- | ---------------------------------------------------------------------------------------------------- | ----- | ----------------------------- |
| NEW  | [generate_syntax.py](file:///d:/git_rk/SPSS/Automation/generate_syntax.py)                           | 380줄 | **핵심 생성기**               |
| NEW  | [syntax_generator_guide.md](file:///d:/git_rk/SPSS/Automation/docs/syntax_generator_guide.md)        | —     | 개발 가이드라인               |
| NEW  | [troubleshooting.md](file:///d:/git_rk/SPSS/Automation/docs/troubleshooting.md)                      | —     | 트러블슈팅 DB (5건)           |
| NEW  | [company/analysis_config.json](file:///d:/git_rk/SPSS/Syntax/Daegu_UKM/company/analysis_config.json) | —     | 기업체 분석 설정              |
| NEW  | [student/analysis_config.json](file:///d:/git_rk/SPSS/Syntax/Daegu_UKM/student/analysis_config.json) | —     | 재학생 분석 설정              |
| MOD  | [CHANGELOG.md](file:///d:/git_rk/SPSS/Automation/CHANGELOG.md)                                       | —     | v1.1.0 이력 추가              |
| MOD  | [md_to_sps.py](file:///d:/git_rk/SPSS/Automation/md_to_sps.py)                                       | —     | CP949 대체 + DEFINE 빈줄 제거 |
| MOD  | [macro_user_guide.md](file:///d:/git_rk/SPSS/Macro/lib/macro_user_guide.md)                          | —     | FAQ 보강                      |

---

## 3. 검증 결과

### 3.1 기업체조사 (Company)

```
$ python generate_syntax.py analysis_config.json
[OK] MD  생성: company_analysis.md
[OK] SPS 생성: company_analysis.sps
     Size: 18,042 bytes
```

| 항목            | 결과                                     |
| --------------- | ---------------------------------------- |
| SPS 파일 생성   | ✅ 18,042 bytes                           |
| CP949 인코딩    | ✅ 에러 없음                              |
| 배너            | SQ1 + A1 + A2                            |
| item types 사용 | freq(6), freq_each(2), mean(1), multi(4) |

### 3.2 재학생조사 (Student)

```
$ python generate_syntax.py analysis_config.json
[OK] MD  생성: student_analysis.md
[OK] SPS 생성: student_analysis.sps
     Size: 23,068 bytes
```

| 항목            | 결과                                       |
| --------------- | ------------------------------------------ |
| SPS 파일 생성   | ✅ 23,068 bytes                             |
| CP949 인코딩    | ✅ 에러 없음                                |
| 배너            | SQ1 + SQ2 + SQ3                            |
| item types 사용 | freq(14), freq_each(1), mean(1), multi(22) |

---

## 4. 산출물 디렉토리 구조

```
d:\git_rk\SPSS\
├── Automation\
│   ├── generate_syntax.py        ← 핵심 생성기 [NEW]
│   ├── generate_macros.py
│   ├── guideline_to_sps.py
│   ├── md_to_sps.py              ← CP949/DEFINE 개선 [MOD]
│   ├── sps_to_md.py
│   ├── CHANGELOG.md              ← v1.1.0 [MOD]
│   └── docs\
│       ├── syntax_generator_guide.md   [NEW]
│       ├── troubleshooting.md          [NEW]
│       └── error_report_roundtrip_*.md
├── Syntax\
│   └── Daegu_UKM\
│       ├── company\
│       │   ├── analysis_config.json    [NEW]
│       │   ├── company_analysis.md     [생성됨]
│       │   └── company_analysis.sps    [생성됨]
│       └── student\
│           ├── analysis_config.json    [NEW]
│           ├── student_analysis.md     [생성됨]
│           └── student_analysis.sps    [생성됨]
└── Macro\lib\
    ├── common_macros.sps         ← DEFINE 빈줄 제거 [MOD]
    └── macro_user_guide.md       ← FAQ 보강 [MOD]
```

---

## 5. 사용법 요약

```bash
# 1. analysis_config.json 작성 (기존 예시 복사 후 수정)
# 2. 생성기 실행
python generate_syntax.py analysis_config.json

# 3. 출력 디렉토리 지정
python generate_syntax.py config.json --output-dir d:\SPSS\Syntax\NewProject
```

---

## 6. 향후 확장 포인트

| 우선순위 | 항목                | 설명                               |
| -------- | ------------------- | ---------------------------------- |
| 높음     | `recode` 실전 적용  | A4R→A4Rr 같은 리코딩을 JSON에 정의 |
| 중간     | `scale` 실전 적용   | freqm2t 매크로 활용                |
| 낮음     | 복합 필터           | `AND`/`OR` 조건 지원               |
| 낮음     | 템플릿 커스터마이징 | 매크로 세트를 프로젝트별로 선택    |
