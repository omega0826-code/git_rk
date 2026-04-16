# CHANGELOG — SPSS Syntax 자동 생성 도구

전체 변경 이력을 관리합니다. 하위 모듈(매크로)의 변경은 [`macros/CHANGELOG.md`](./macros/CHANGELOG.md)에서 별도 관리합니다.

버전 관리 규칙: [Semantic Versioning](https://semver.org/lang/ko/) 준수  
상세 규칙: [`docs/syntax_generator_guide.md` §2](./docs/syntax_generator_guide.md)

---

## [Unreleased]

### 추가
- `app.py`: 웹 UI 샘플 다운로드 라우트, 파일명 정리, 업로드 용량 초과 응답, 포트 자동 전환 추가
- `web/index.html`: 외부 CDN 없이 동작하는 자체 포함형 웹 UI로 개편
- `launch_web_ui.hta`: Windows에서 HTML 기반으로 웹 UI를 실행하는 런처 추가

### 변경
- `start.bat`: `.venv` / `py -3` / `python` 순으로 Python 탐색, `requirements.txt` 기준 의존성 설치, 오류 종료 처리 추가
- `README.md`: 웹 UI 실행 방법과 HTA 런처 사용법 추가

---

## [1.0.1] - 2026-04-15

### 버그 수정
- **`generate_macros.py`**: `DEFAULT_TEMPLATE` 경로 오류 수정
  - 수정 전: `../Macro/lib/common_macros_template.sps` (대소문자 불일치 + 존재하지 않는 `lib/` 서브폴더)
  - 수정 후: `../macros/common_macros_template.sps`
  - 영향: `--template` 옵션 없이 실행 시 `FileNotFoundError` 발생하던 문제 해결
- **`macros/common_macros_template.sps`**: `cot`, `cst` 매크로 하드코딩 수정
  - `'업체수'` → `'{{VALIDN_LABEL}}'`로 교체 (2곳)
  - 영향: `generate_macros.py`로 생성 시 `validn_label` 설정이 반영되지 않던 문제 해결

### 추가
- `examples/analysis_config_sample.json`: `generate_syntax.py`용 설정 파일 전체 item type 예시 추가
- `examples/guideline_sample.csv`: `guideline_to_sps.py`용 입력 CSV 예시 추가
- `CHANGELOG.md` (이 파일): 루트 변경 이력 파일 신규 생성
- `requirements.txt`: Python 버전 요구사항 및 의존성 명세 추가
- `docs/deployment_log.md`: 배포 작업 이력 기록 추가

### 변경
- `generate_macros.py` 버전 `1.0.0` → `1.0.1`

---

## [1.0.0] - 2026-02-26

### 추가
- `scripts/guideline_to_sps.py`: CSV 가이드라인 → VARIABLE/VALUE LABELS `.sps` 변환 도구 최초 릴리즈
- `scripts/generate_syntax.py`: JSON 설정 → 분석 syntax (`.sps` + `.md`) 자동 생성 도구 최초 릴리즈
- `scripts/generate_macros.py`: JSON + 템플릿 → 프로젝트 맞춤 매크로 `.sps` 생성 도구 최초 릴리즈
- `scripts/sps_to_md.py`: `.sps` → `.md` 변환 도구 (배치 모드 포함) 최초 릴리즈
- `scripts/md_to_sps.py`: `.md` → `.sps` 역변환 도구 (배치 모드 포함) 최초 릴리즈
- `macros/common_macros.sps`: 복사 붙여넣기용 공통 매크로 43개
- `macros/common_macros_template.sps`: `generate_macros.py`용 플레이스홀더 템플릿
- `examples/short_labels_sample.json`: 간략 라벨 JSON 예시
- `docs/`: 사용 가이드, 트러블슈팅 DB, 변환 가이드 등 문서 일체
