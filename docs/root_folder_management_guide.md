# 루트 폴더 관리 지침

> **대상**: 데이터분석가 | **저장소**: `d:\git_rk` | **최종 수정**: 2026-03-10

---

## 1. 폴더 구조 원칙

### 1-1. 루트 폴더는 "카테고리 폴더"만 둔다

루트에는 **역할별 폴더**만 배치하고, 개별 스크립트·데이터 파일은 루트에 직접 두지 않는다.

```
d:\git_rk\
├── .agent/              # AI agent 설정 (자동 관리)
├── .venv/               # Python 가상환경
├── .vscode/             # VS Code 설정
│
├── automation/          # 문서 자동화 (HWP, PPT 등)
├── data/                # 대용량 원본 데이터 (git 제외)
├── database/            # DB 관련 프로젝트
├── docs/                # 문서 및 가이드
├── notebook/            # Jupyter Notebook 작업
├── openapi/             # OpenAPI 수집·연동
├── output/              # 분석 결과물 (보고서, 시각화 등)
├── project/             # 개별 프로젝트 (아래 관리방법 참조)
├── reference/           # 참조 자료 (매뉴얼, 가이드 등)
├── src/                 # 공용 소스코드 (재사용 모듈)
├── work_log/            # ★ 작업이력 관리
│
├── .env                 # 환경 변수
└── .gitignore           # Git 제외 규칙
```

### 1-2. 비슷한 작업은 1개 폴더로 묶는다

| 기존 (분산)                          | 통합 후                            | 비고                      |
| ------------------------------------ | ---------------------------------- | ------------------------- |
| `Report/`, `SPSS/`                   | `output/` 하위로 통합              | 분석 결과물               |
| `Hwp Automation/`, `PPT Automation/` | `automation/`                      | 문서 자동화               |
| `notebooks/`, `division/`            | `notebook/`                        | Jupyter 작업              |
| `pdf/`, `vba/`                       | 각각 관련 폴더로 이동              | `automation/` 또는 `src/` |
| `image/`                             | `output/image/` 또는 `data/image/` | 용도에 따라               |

### 1-3. 파일명·폴더명 규칙

- **snake_case** 사용 (영문 소문자, 숫자, `_`만 허용)
- 공백, 대문자, 한글 폴더명 금지
- 프로젝트 폴더: `YY_NNN_프로젝트약어` (예: `25_121_ulsan`)

---

## 2. 대용량 데이터 관리 (`data/`)

### 2-1. 하위 폴더 구성

```
data/
├── raw/                 # 원본 데이터 (수정 금지)
│   ├── csv/
│   ├── excel/
│   ├── shapefile/
│   └── api_response/
├── processed/           # 가공된 데이터
│   ├── cleaned/
│   └── merged/
├── external/            # 외부 제공 데이터
└── archive/             # 더 이상 사용하지 않는 데이터
```

### 2-2. 관리 규칙

| 규칙          | 설명                                                            |
| ------------- | --------------------------------------------------------------- |
| **Git 제외**  | `data/` 전체를 `.gitignore`에 등록                              |
| **원본 보존** | `raw/`의 파일은 절대 수정하지 않음 — 가공은 `processed/`에 저장 |
| **파일 크기** | 100MB 이상 파일은 반드시 `data/`에 보관                         |
| **파일명**    | `데이터설명_YYMMDD.확장자` (예: `factory_company_260307.csv`)   |
| **인코딩**    | CSV는 반드시 UTF-8로 저장                                       |

---

## 3. GitHub 활용 — 대용량 파일 커밋 제외

### 3-1. `.gitignore` 설정

```gitignore
# === 대용량 데이터 ===
data/
*.csv
*.xlsx
*.xls
*.sav
*.shp
*.dbf
*.shx

# === 가상환경 ===
.venv/
__pycache__/
*.pyc

# === 출력물 (필요 시 개별 추가) ===
output/
*.zip

# === 시스템 파일 ===
desktop.ini
Thumbs.db
.DS_Store

# === 환경 변수 ===
.env

# === 임시 파일 ===
tmp_*.py
*.tmp
*.log
```

### 3-2. Git 커밋 대상 vs 제외 대상

| 커밋 대상 (O)                | 제외 대상 (X)                   |
| ---------------------------- | ------------------------------- |
| Python 스크립트 (`.py`)      | 대용량 데이터 (`.csv`, `.xlsx`) |
| 문서 (`.md`)                 | 가상환경 (`.venv/`)             |
| 설정 파일 (`.json`, `.yaml`) | 출력 결과물 (`output/`)         |
| `.gitignore`                 | 환경 변수 (`.env`)              |
| 소스코드 (`src/`)            | 임시 스크립트 (`tmp_*.py`)      |

### 3-3. 대용량 파일이 이미 커밋된 경우

```bash
# 추적에서 제거 (로컬 파일은 유지)
git rm --cached <파일경로>
git commit -m "remove large file from tracking"
```

---

## 4. 프로젝트 폴더(`project/`) 관리 — 연도-번호 기반

프로젝트마다 `YY_NNN_이름` 형식으로 폴더를 생성한다.

```
project/
├── 25_044_traditional_ingredient/
├── 25_121_ulsan/
├── 25_124_interview/
├── 25_n33_munkyung/
└── 26_001_new_project/
```

### 명명 규칙

- `YY` : 연도 2자리
- `NNN` : 프로젝트 번호 (3자리, 비순번일 경우 `n` 접두사 사용)
- `이름` : 프로젝트 약어 (snake_case, 영문)

### 내부 구조 (표준 템플릿)

```
25_121_ulsan/
├── data/           # 프로젝트 전용 데이터
├── scripts/        # 분석 스크립트
├── output/         # 결과물
├── docs/           # 프로젝트 문서
└── README.md       # 프로젝트 개요
```

---

## 5. 작업이력 관리 (`work_log/`)

프로젝트 횡단적인 **작업 기록·의사결정·회고**를 관리하는 폴더.

### 5-1. 폴더 구조

```
work_log/
├── daily/               # 일일 작업 로그
│   ├── 260310.md
│   ├── 260311.md
│   └── ...
├── decisions/           # 주요 의사결정 기록
│   └── 260307_address_cleaning_rule.md
├── retrospective/       # 회고·개선사항
│   └── 260310_folder_cleanup.md
└── README.md            # work_log 사용법
```

### 5-2. 일일 로그 템플릿 (`daily/YYMMDD.md`)

```markdown
# 260310 작업 로그

## 오늘 한 일
- [ ] 루트 폴더 정리 (54건 삭제, 3건 이동)
- [ ] 폴더 관리 지침 작성

## 이슈·발견사항
- 터미널 승인 대기 문제 발견 → workflow 업데이트

## 내일 할 일
- data/ 폴더 하위 구조 정리
```

### 5-3. 의사결정 로그 템플릿 (`decisions/YYMMDD_제목.md`)

```markdown
# 주소 클리닝 규칙 변경

- **일자**: 2026-03-07
- **배경**: 시도/시군구 미추출 건이 다수 발견
- **결정**: 추출 불가 시 `[삭제:주소결함]` 태그 부여
- **영향 범위**: `02_clean_address.py`, `run_pipeline.py`
- **관련 프로젝트**: database/company_database
```

---

## 6. 현재 폴더 → 정리 액션 요약

| 현재 폴더      | 액션           | 이동 위치                     |
| -------------- | -------------- | ----------------------------- |
| `Report/`      | 이동           | `docs/report/`                |
| `SPSS/`        | 이름 변경+이동 | `automation/spss_automation/` |
| `division/`    | 이동           | `notebook/division/`          |
| `notebooks/`   | 이동           | `notebook/` (통합)            |
| `vba/`         | 이동           | `automation/vba/`             |
| `.test/`       | 검토 후 결정   | `data/test/` 또는 삭제        |
| `application/` | 유지           | —                             |
| `work_log/`    | **신규 생성**  | —                             |

---

### `pdf/` 폴더 상세 검토

**현재 내용**: `pdf_master_extractor.py` (16KB) — PDF 텍스트 추출 범용 스크립트 1개

| 안    | 이동 위치              | 이유                                  |
| ----- | ---------------------- | ------------------------------------- |
| **A** | `src/pdf_extractor/`   | 범용 추출 도구 → 공용 소스코드에 배치 |
| **B** | `automation/pdf/`      | 자동화 도구 계열로 분류               |
| **C** | 삭제 후 필요 시 재작성 | 단일 파일이므로 폴더 유지 비용이 높음 |

> **추천**: **안 A** (`src/pdf_extractor/`) — 다른 프로젝트에서도 재사용 가능한 도구이므로 `src/`가 적합

---

### `image/` 폴더 상세 검토

**현재 내용**: `image/test/` 하위에 수식 이미지 PPT 생성 관련 파일 11개
- 스크립트 5개: `create_ppt.py`, `explore_pdf.py`, `extract_and_ppt.py`, `extract_formulas.py`, `generate_formula_images.py`
- 결과물 3개: `U-Mismatch_Model_수식.pptx`, `울산_미스매치_수식_PPT.pptx`, `울산 일자리 미스매치 모델_PPT test.pdf`
- 문서 1개: `test.md`
- 하위폴더 2개: `formula_images/`, `images/`

| 안    | 이동 위치                    | 이유                                               |
| ----- | ---------------------------- | -------------------------------------------------- |
| **A** | `project/25_121_ulsan/` 하위 | 울산 프로젝트 관련 작업이므로 해당 프로젝트로 통합 |
| **B** | `automation/formula_ppt/`    | 수식→PPT 변환 자동화 도구로 분류                   |
| **C** | 삭제                         | 테스트 용도로 만든 것이라 더 이상 불필요           |

> **추천**: **안 A** (`project/25_121_ulsan/`) — 울산 미스매치 모델 관련 작업물이므로 프로젝트 폴더로 통합
