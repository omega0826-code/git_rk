# Lovable.dev 최적 프롬프트 — HWPX 파서 로컬 앱

> 작성일: 2026-03-09 | 대상: Lovable.dev 프로젝트 생성용
> 
> **사용법**: 아래 프롬프트를 단계별로 Lovable.dev에 입력하세요.  
> 각 단계가 완료된 후 다음 단계로 진행합니다.

---

## 목차

1. [프로젝트 초기 생성 프롬프트](#1-프로젝트-초기-생성-프롬프트)
2. [단계별 기능 구현 프롬프트](#2-단계별-기능-구현-프롬프트)
3. [수정·업데이트 프롬프트 템플릿](#3-수정업데이트-프롬프트-템플릿)
4. [로컬 실행 가이드](#4-로컬-실행-가이드)
5. [프롬프트 작성 원칙 (Lovable 최적화)](#5-프롬프트-작성-원칙-lovable-최적화)

---

## 1. 프로젝트 초기 생성 프롬프트

> Lovable.dev에서 새 프로젝트 생성 시 아래 프롬프트를 **그대로** 붙여넣기 하세요.

```
프로젝트 이름: HWPX Parser App

## 프로젝트 개요
한컴 HWPX 파일(.hwpx)에서 텍스트, 표, 이미지, 제목 구조를 자동 추출하는
Python 기반 데스크톱 웹앱을 만들어주세요.

코딩 경험이 없는 사용자도 로컬 PC에서 바로 실행할 수 있어야 합니다.

## 기술 스택
- Frontend: React + TypeScript + Tailwind CSS + shadcn/ui
- Backend: Python FastAPI (로컬 서버)
- 파일 처리: Python lxml (HWPX XML 파싱)
- 상태관리: React useState/useReducer
- 빌드: Vite

## 핵심 페이지 구조 (총 4페이지)

### 페이지 1: / (홈 — 파일 업로드)
- 화면 중앙에 드래그앤드롭 영역 (점선 테두리, 파란 배경)
- "HWPX 파일을 여기에 놓거나 클릭하여 선택하세요" 안내 텍스트
- .hwpx 확장자만 허용, 그 외 파일은 에러 토스트 표시
- 파일 선택 후 "파싱 시작" 버튼 활성화
- 파싱 진행 중에는 프로그레스 바와 단계 표시:
  "ZIP 해제 중..." → "텍스트 추출 중..." → "표 추출 중..." → "이미지 추출 중..." → "완료!"
- 완료 시 자동으로 /results 페이지로 이동

### 페이지 2: /results (파싱 결과 대시보드)
- 상단: 파일명, 파싱 소요시간, 파싱 일시
- 요약 카드 4개 (가로 배열):
  - 📄 문단 수 (예: 968개)
  - 📑 제목 수 (예: 56개)
  - 📊 표 수 (예: 125개)
  - 🖼️ 이미지 수 (예: 36개)
- 탭 네비게이션: [텍스트] [표] [이미지] [제목구조] [로그]
- 각 탭 내용:
  - 텍스트 탭: 전체 텍스트 미리보기 (스크롤), Markdown/TXT 다운로드 버튼
  - 표 탭: 표 목록(인덱스, 행×열, 제목), 클릭 시 표 상세보기 모달
  - 이미지 탭: 썸네일 그리드, 클릭 시 원본 보기
  - 제목구조 탭: 들여쓰기된 트리 형태로 제목 계층 표시
  - 로그 탭: 파싱 로그 텍스트 (에러 포함)

### 페이지 3: /results/table/:id (표 상세보기)
- 표 데이터를 HTML 테이블로 렌더링 (셀 병합 시각화)
- CSV 다운로드 버튼
- 이전/다음 표 네비게이션

### 페이지 4: /settings (설정)
- Python 경로 설정 (자동 감지 + 수동 입력)
- 출력 디렉토리 설정
- 출력 형식 체크박스: Markdown, Plain Text, CSV, Excel, JSON

## 공통 UI 규칙
- 전체 레이아웃: 왼쪽 사이드바 네비게이션 + 오른쪽 콘텐츠 영역
- 사이드바: 홈, 결과, 설정 메뉴 (아이콘 + 텍스트)
- 색상 테마: 흰 배경, 파란 계열 액센트 (#2563EB), 회색 보조
- 모든 텍스트는 한국어
- 반응형: 모바일에서는 사이드바가 햄버거 메뉴로 변환
- 에러 발생 시 토스트 알림 (shadcn/ui Toast 컴포넌트)
- 모든 다운로드 버튼은 파일명에 타임스탬프 포함

## 중요: 건드리지 말아야 할 것
- 이 초기 프롬프트에서는 Backend Python 코드를 작성하지 마세요
- Frontend UI만 먼저 완성하세요 (모든 데이터는 목업/더미 데이터 사용)
- 목업 데이터 예시:
  - 문단 수: 968, 제목: 56, 표: 125, 이미지: 36
  - 표 샘플: [{index:1, rows:9, cols:9, title:"지역별 GRDP 현황", grid:[...]}]
  - 텍스트 샘플: "1. 경북지역 산업 현황 분석\n\n경북지역의 산업구조는..."
```

---

## 2. 단계별 기능 구현 프롬프트

> 아래 프롬프트를 **순서대로** 하나씩 입력하세요.  
> 각 단계 완료 → 테스트 → 다음 단계 진행.

---

### STEP 2: 파일 업로드 + Python 백엔드 연동

```
## STEP 2: Python FastAPI 백엔드 연동

이전 단계에서 만든 UI는 변경하지 마세요.

### 백엔드 구조
`/backend` 폴더를 생성하고 다음 파일을 만들어주세요:

1. `backend/main.py` — FastAPI 서버
   - POST /api/parse — HWPX 파일 업로드 및 파싱
   - GET /api/results/{session_id} — 파싱 결과 조회
   - GET /api/download/{session_id}/{file_type} — 파일 다운로드
   - 포트: 8000

2. `backend/hwpx_parser.py` — 핵심 파서 모듈
   아래 클래스 구조를 그대로 구현하세요:

   ```python
   # 네임스페이스
   NS = {
       'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
       'hs': 'http://www.hancom.co.kr/hwpml/2011/section',
       'hc': 'http://www.hancom.co.kr/hwpml/2011/core',
       'hh': 'http://www.hancom.co.kr/hwpml/2011/head',
       'ha': 'http://www.hancom.co.kr/hwpml/2011/app',
   }

   class HwpxReader:
       """HWPX(ZIP) 파일을 열고 내부 XML을 읽는다"""
       - __init__(hwpx_path): 파일 존재 여부, ZIP 유효성 검증
       - read_xml(internal_path): lxml etree로 XML 파싱
       - read_binary(internal_path): 바이너리 파일 읽기
       - get_section_roots(): Contents/section*.xml 목록 반환
       - get_bin_data_list(): BinData/ 파일 목록
       - context manager 지원 (__enter__, __exit__)

   class TextExtractor:
       """section XML에서 본문 텍스트 추출"""
       - extract_paragraph_text(p_elem): hp:p → hp:run → hp:t의 .text 수집
       - is_in_table(p_elem): getparent() 순회로 hp:tbl 내부 여부 확인
       - is_in_header_footer(p_elem): hp:header, hp:footer 내부 여부 확인
       - extract_all(root): 표/머리말 제외한 전체 텍스트 리스트 반환

   class HeadingDetector:
       """hp:titleMark 기반 제목 감지"""
       - STYLE_LEVEL_MAP = {'1':1, '2':2, '3':3, '4':4, '5':5, '6':6}
       - detect(root): titleMark 있는 문단을 제목으로 식별, level/text 반환

   class TableExtractor:
       """표 추출 (셀 병합 처리 포함)"""
       - _is_body_table(tbl): 머리말/꼬리말 내부 표 필터링
       - _get_cell_text(tc): 셀 텍스트 추출
       - extract_all(root):
         - hp:tbl의 rowCnt, colCnt로 2D 그리드 초기화
         - hp:tc > hp:cellAddr로 위치 파악
         - hp:cellSpan으로 병합 범위 처리
         - occupied 배열로 중복 방지

   class ImageExtractor:
       """이미지 참조 추출 + 파일 저장"""
       - extract_image_refs(root): hp:pic > hc:img의 binaryItemIDRef 수집
       - extract_images(reader, refs, output_dir): BinData/에서 파일 추출 저장

   class OutputWriter:
       """결과를 다양한 형식으로 저장"""
       - write_full_text_md(): Markdown 저장
       - write_full_text_txt(): Plain Text 저장
       - write_headings_json(): 제목 구조 JSON
       - write_all_tables_csv(): 개별 CSV 파일
       - write_all_tables_excel(): 통합 Excel (pandas 선택)
       - write_parse_log(): 파싱 로그

   def parse_hwpx(hwpx_path, output_base=None):
       """원스톱 파싱 함수 — 위 클래스들을 조합"""
   ```

3. `backend/requirements.txt`
   ```
   fastapi==0.109.0
   uvicorn==0.27.0
   python-multipart==0.0.6
   lxml==5.1.0
   pandas==2.2.0
   openpyxl==3.1.2
   ```

### Frontend 연동
- 홈페이지의 "파싱 시작" 버튼 클릭 시 POST /api/parse 호출
- FormData로 .hwpx 파일 전송
- 응답의 session_id로 /results 페이지 데이터 로드
- 기존 목업 데이터를 실제 API 응답으로 교체

### 중요
- Frontend의 디자인과 레이아웃을 변경하지 마세요
- 에러 처리: 파일이 유효하지 않으면 400 에러 + 한국어 메시지
- CORS 설정: localhost:5173 허용
```

---

### STEP 3: 다운로드 기능 구현

```
## STEP 3: 다운로드 기능

이전 단계의 UI와 백엔드 로직을 변경하지 마세요.

다음 다운로드 버튼들을 실제 API와 연결해주세요:

1. 텍스트 탭:
   - "Markdown 다운로드" → GET /api/download/{session_id}/md
   - "Plain Text 다운로드" → GET /api/download/{session_id}/txt

2. 표 탭:
   - "CSV 다운로드" (개별 표) → GET /api/download/{session_id}/csv?table={index}
   - "전체 CSV 다운로드" → GET /api/download/{session_id}/csv_all
   - "Excel 다운로드" → GET /api/download/{session_id}/xlsx

3. 이미지 탭:
   - "이미지 ZIP 다운로드" → GET /api/download/{session_id}/images_zip

4. 제목구조 탭:
   - "JSON 다운로드" → GET /api/download/{session_id}/headings_json

5. 로그 탭:
   - "로그 다운로드" → GET /api/download/{session_id}/log

### 파일명 규칙
다운로드 파일명: {원본파일명}_{타입}_{YYYYMMDD_HHmm}.{확장자}
예시: 보고서_full_text_20260309_1430.md

### 중요
- 다운로드 중 로딩 스피너 표시
- 다운로드 완료 시 "다운로드 완료" 토스트 알림
- 네트워크 에러 시 재시도 버튼이 있는 에러 토스트
```

---

### STEP 4: 로컬 실행 원클릭 스크립트

```
## STEP 4: 로컬 실행 자동화 스크립트

초보자가 더블클릭만으로 앱을 실행할 수 있도록 스크립트를 만들어주세요.

### Windows용: start_app.bat
```batch
@echo off
chcp 65001 > nul
echo ========================================
echo   HWPX Parser App 시작 중...
echo ========================================
echo.

REM Python 확인
python --version > nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo https://www.python.org/downloads/ 에서 설치하세요.
    pause
    exit /b 1
)

REM Node.js 확인
node --version > nul 2>&1
if errorlevel 1 (
    echo [오류] Node.js가 설치되어 있지 않습니다.
    echo https://nodejs.org/ 에서 설치하세요.
    pause
    exit /b 1
)

REM Python 가상환경 + 의존성 설치
if not exist "backend\.venv" (
    echo [설정] Python 가상환경 생성 중...
    cd backend
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
    cd ..
) else (
    call backend\.venv\Scripts\activate.bat
)

REM npm 의존성 설치
if not exist "node_modules" (
    echo [설정] npm 패키지 설치 중...
    npm install
)

REM 백엔드 시작 (백그라운드)
echo [시작] 백엔드 서버 시작 (포트 8000)...
start /b cmd /c "cd backend && .venv\Scripts\activate.bat && uvicorn main:app --host 0.0.0.0 --port 8000"

REM 프론트엔드 시작
echo [시작] 프론트엔드 서버 시작 (포트 5173)...
timeout /t 3 > nul
start http://localhost:5173
npm run dev
```

### Mac/Linux용: start_app.sh
```bash
#!/bin/bash
echo "========================================"
echo "  HWPX Parser App 시작 중..."
echo "========================================"

# Python 확인
if ! command -v python3 &> /dev/null; then
    echo "[오류] Python3이 설치되어 있지 않습니다."
    exit 1
fi

# Node.js 확인
if ! command -v node &> /dev/null; then
    echo "[오류] Node.js가 설치되어 있지 않습니다."
    exit 1
fi

# Python 가상환경
if [ ! -d "backend/.venv" ]; then
    echo "[설정] Python 가상환경 생성 중..."
    cd backend
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    source backend/.venv/bin/activate
fi

# npm 의존성
if [ ! -d "node_modules" ]; then
    echo "[설정] npm 패키지 설치 중..."
    npm install
fi

# 백엔드 시작
echo "[시작] 백엔드 서버 시작..."
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 &
cd ..

# 프론트엔드 시작
sleep 3
echo "[시작] 프론트엔드 서버 시작..."
open http://localhost:5173 2>/dev/null || xdg-open http://localhost:5173 2>/dev/null
npm run dev
```

### README.md 작성
루트에 README.md를 만들어주세요:
- 프로젝트 소개 (한국어)
- 필수 설치 요구사항: Python 3.9+, Node.js 18+
- 설치 및 실행 방법 (Windows/Mac/Linux 각각)
- 사용 방법 (스크린샷 위치 표시)
- 자주 묻는 질문 (FAQ)
- 문제 해결 가이드

### 중요
- 기존 코드를 변경하지 마세요
- 실행 스크립트만 추가하세요
```

---

## 3. 수정·업데이트 프롬프트 템플릿

> 앱 완성 후 기능 수정이 필요할 때 아래 템플릿을 활용하세요.

### 3.1 버그 수정 템플릿

```
## 버그 수정 요청

### 어떤 페이지에서 발생하나요?
/results 페이지의 [표] 탭

### 현재 동작 (문제)
표를 클릭했을 때 모달이 열리지 않고 콘솔에
"TypeError: Cannot read property 'grid' of undefined" 에러가 발생합니다.

### 기대 동작
표를 클릭하면 해당 표의 데이터가 HTML 테이블로 렌더링된 모달이 열려야 합니다.

### 재현 방법
1. HWPX 파일 업로드
2. 파싱 완료 후 /results 이동
3. [표] 탭 클릭
4. 첫 번째 표 항목 클릭

### 중요: 건드리지 말 것
- /results 페이지의 다른 탭 (텍스트, 이미지, 제목구조, 로그)
- 사이드바 네비게이션
- 백엔드 API
```

### 3.2 기능 추가 템플릿

```
## 기능 추가 요청

### 추가할 기능
HWPX 파일 일괄 처리 (다중 파일 업로드)

### 변경이 필요한 페이지
/ (홈 페이지) 만 변경

### 상세 요구사항
1. 드래그앤드롭 영역에서 여러 .hwpx 파일을 동시에 선택 가능
2. 선택된 파일 목록을 업로드 영역 아래에 카드 형태로 표시
3. 각 카드에 파일명, 파일 크기, 삭제(X) 버튼
4. "전체 파싱 시작" 버튼 클릭 시 순차 처리
5. 각 파일별 진행 상태 표시 (대기/진행중/완료/에러)
6. 전체 완료 시 /results 대신 /batch-results 페이지로 이동

### 변경하지 말 것
- 기존 단일 파일 파싱 흐름 (파일 1개일 때는 기존과 동일하게)
- /results 페이지
- /settings 페이지
- 사이드바 네비게이션
- 백엔드의 hwpx_parser.py 파서 로직
```

### 3.3 디자인 수정 템플릿

```
## 디자인 수정 요청

### 수정 대상
/results 페이지의 요약 카드 영역

### 현재 상태
4개 카드가 동일한 흰색 배경, 작은 텍스트

### 원하는 변경
1. 각 카드에 고유 배경 색상:
   - 문단: 연파랑 (#EFF6FF)
   - 제목: 연보라 (#F5F3FF)
   - 표: 연초록 (#F0FDF4)
   - 이미지: 연주황 (#FFF7ED)
2. 숫자를 32px 볼드로 크게 표시
3. 아이콘을 각 카드 색상과 맞는 색으로 변경
4. 카드에 hover 시 그림자 효과 추가

### 변경하지 말 것
- 카드 배치 (4개 가로 배열 유지)
- 카드 내 데이터 내용
- 다른 모든 페이지
```

### 3.4 파서 로직 수정 템플릿

```
## 파서 로직 수정

### 수정 대상
backend/hwpx_parser.py의 TableExtractor 클래스

### 현재 동작
표 제목 추측 시 표 바로 위 문단만 확인하여,
위에 문단이 없으면 빈 문자열 반환

### 원하는 변경
표 제목 추측 로직을 다음 순서로 보강:
1. 기존: 표 위 문단에서 제목 탐색 (현재 로직 유지)
2. 추가: hp:caption 요소가 있으면 캡션 텍스트 사용
3. 추가: 위 두 방법 실패 시 표의 첫 행(헤더)을 제목으로 사용

### 변경하지 말 것
- 다른 모든 클래스 (HwpxReader, TextExtractor, HeadingDetector, ImageExtractor, OutputWriter)
- Frontend 코드 전체
- API 응답 형식 (title 필드만 값이 달라짐)
```

---

## 4. 로컬 실행 가이드

> 이 섹션은 Lovable.dev에서 생성한 코드를 로컬로 가져와 실행하는 방법입니다.

### 4.1 사전 준비

| 항목 | 최소 버전 | 설치 링크 |
|------|-----------|-----------|
| Python | 3.9+ | https://www.python.org/downloads/ |
| Node.js | 18+ | https://nodejs.org/ |
| Git | 최신 | https://git-scm.com/ |

### 4.2 코드 다운로드

```bash
# Lovable.dev → GitHub 연동 후
git clone https://github.com/{your-repo}/hwpx-parser-app.git
cd hwpx-parser-app
```

### 4.3 실행

**Windows**: `start_app.bat` 더블클릭  
**Mac/Linux**: 터미널에서 `bash start_app.sh`

브라우저에서 `http://localhost:5173` 자동 오픈

### 4.4 수동 실행 (문제 발생 시)

```bash
# 터미널 1: 백엔드
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --port 8000

# 터미널 2: 프론트엔드
npm install
npm run dev
```

---

## 5. 프롬프트 작성 원칙 (Lovable 최적화)

Lovable.dev에서 최상의 결과를 얻기 위한 핵심 원칙입니다.

### 원칙 1: 한 번에 하나씩
한 프롬프트에 5개 기능을 요청하지 마세요.
1단계씩 나누고, 각 단계를 완료·테스트한 후 다음으로 진행하세요.

### 원칙 2: 구체적으로 명시
"대시보드를 만들어줘" ❌  
"문단/제목/표/이미지 수를 보여주는 요약 카드 4개를 가로 배열로 배치하고,
아래에 5개 탭(텍스트/표/이미지/제목구조/로그)을 추가해줘" ✅

### 원칙 3: "건드리지 말 것" 명시
매 프롬프트에 **변경하면 안 되는 파일/컴포넌트/페이지**를 반드시 적으세요.
Lovable AI가 관련 없는 코드를 건드려 사이드이펙트가 발생하는 것을 방지합니다.

### 원칙 4: Frontend 먼저, Backend 나중에
목업 데이터로 UI를 완성한 후 API를 연결하세요.
Lovable은 DB 스키마 변경 시 롤백이 어렵습니다.

### 원칙 5: 에러 발생 시 상세하게 보고
"안 돼요" ❌  
"어떤 페이지에서, 어떤 동작을 했을 때, 어떤 에러가 발생하고,
기대한 동작은 무엇인지" ✅

### 원칙 6: 반응형은 별도 단계로
기능 구현이 완료된 후 마지막에 반응형을 한 번에 적용하세요:
```
모든 페이지의 모바일 반응형을 최적화해주세요.
shadcn과 Tailwind 기본 브레이크포인트를 사용하세요.
커스텀 브레이크포인트는 사용하지 마세요.
모바일 우선(mobile-first) 접근법을 적용하세요.
기존 데스크톱 디자인과 기능은 변경하지 마세요.
```

### 원칙 7: 정기적으로 리팩토링
기능을 5~6개 추가한 후에는 리팩토링 프롬프트를 실행하세요:
```
현재 코드를 리팩토링해주세요.
UI와 기능은 변경하지 말고, 코드 구조와 유지보수성만 개선하세요.
변경 사항을 문서화해주세요.
```

---

## 부록: HWPX 파서 핵심 기술 참조

> 아래는 Lovable에서 파서 관련 질문이 있을 때 참고할 정보입니다.

### HWPX 파일 구조
HWPX = ZIP 기반 XML 패키지
- `Contents/section0.xml` — 본문 (문단, 표, 이미지)
- `Contents/header.xml` — 스타일 정의
- `BinData/` — 임베디드 이미지 (bmp/png/jpg/wmf)

### XML 네임스페이스
| 접두사 | URI | 용도 |
|--------|-----|------|
| `hp` | `http://www.hancom.co.kr/hwpml/2011/paragraph` | 문단, 표, 이미지 |
| `hs` | `http://www.hancom.co.kr/hwpml/2011/section` | 섹션 루트 |
| `hc` | `http://www.hancom.co.kr/hwpml/2011/core` | 이미지(img) |
| `hh` | `http://www.hancom.co.kr/hwpml/2011/head` | 헤더 메타정보 |

### 핵심 파싱 경로
- 텍스트: `hp:p → hp:run → hp:t.text`
- 표: `hp:tbl[rowCnt,colCnt] → hp:tc → hp:cellAddr + hp:cellSpan`
- 이미지: `hp:pic → hc:img[@binaryItemIDRef]` → `BinData/` 매핑
- 제목: `hp:titleMark` 존재 여부 + `styleIDRef` 레벨 매핑

### 알려진 제한사항
1. 표 제목 추측 실패 가능 (표 위 문단이 없는 경우)
2. `styleIDRef=0`인 소제목이 본문과 구분 어려움
3. BMP 이미지 대용량 (최대 25MB) — 자동 변환 미지원
4. 다중 섹션(section1.xml 등) 테스트 미완
