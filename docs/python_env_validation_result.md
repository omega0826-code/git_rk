# Python 실행환경 검증 결과

> **검증 일시**: 2026-03-10 09:48:33
> **Python**: 3.14.2 (tags/v3.14.2:df79316, Dec  5 2025, 17:18:21) [MSC v.1944 64 bit (AMD64)]
> **실행 파일**: `C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe`

## 요약

| 판정 | 건수 | 비율 |
|------|------|------|
| PASS | 22 | 85% |
| WARN | 4 | 15% |
| FAIL | 0 | 0% |
| **합계** | **26** | **100%** |

> [!NOTE]
> FAIL 항목은 없지만 WARN 4건을 확인해 주세요.

---

## Phase 1: 시스템 환경 기본 점검

| 항목 | 판정 | 상세 |
|------|------|------|
| Python 버전 | PASS | 3.14.2 |
| Python 실행 파일 | PASS | C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe |
| Python 경로 수 | WARN | 2개 발견 (충돌 가능성) -> ['C:\\Users\\user\\AppData\\Local\\Programs\\Python\\Python314\\python.exe', 'C:\\Users\\user\\AppData\\Local\\Microsoft\\WindowsApps\\python.exe'] |
| 가상환경 활성 | WARN | 가상환경 미활성 (시스템 Python 사용 중) |
| .venv 디렉토리 | PASS | 존재 (python.exe 확인됨) |
| sys.path 항목 수 | PASS | 10개 |
| 설치 패키지 수 | WARN | 확인 불가: No module named 'pkg_resources' |
## Phase 2: 인코딩 환경 점검

| 항목 | 판정 | 상세 |
|------|------|------|
| 기본 인코딩 | PASS | utf-8 |
| stdout 인코딩 | PASS | utf-8 |
| PYTHONIOENCODING | PASS | utf-8  |
| PYTHONUNBUFFERED | PASS | 1  |
| 한글 출력 | PASS | 정상 |
| ASCII 대체 문자 | PASS | cp949 호환 확인 |
| 이모지 cp949 호환 | WARN | 이모지는 cp949에서 출력 불가 -> ASCII 대체([OK]/[FAIL]) 사용 필수 |
## Phase 3: 핵심 라이브러리 Import 벤치마크

| 항목 | 판정 | 상세 |
|------|------|------|
| import numpy | PASS | 0.181s |
| import pandas | PASS | 0.698s |
| import matplotlib | PASS | 0.221s |
| import openpyxl | PASS | 0.352s |
| import geopandas | PASS | 0.300s |
| 한글 폰트 검색 | PASS | ['Jalnan Gothic', 'Franklin Gothic Medium Cond', 'Franklin Gothic Medium'] (0.000s) |
| Matplotlib 렌더링 | PASS | 0.024s |
| Pandas CSV I/O | PASS | 1000행 read/write 0.016s |
## Phase 4: 좀비 프로세스 및 리소스 점검

| 항목 | 판정 | 상세 |
|------|------|------|
| 좀비 python.exe | PASS | 현재 프로세스 외 없음 (총 1개) |
| 파일 I/O 지연 (100 파일) | PASS | 생성 0.030s / 삭제 0.048s |
| 파일 R/W (10,000줄) | PASS | 쓰기 0.007s / 읽기 0.001s |
| PATH 항목 수 | PASS | 24개 |

---

## 조치 가이드

### [WARN] Python 경로 수
- **상세**: 2개 발견 (충돌 가능성) -> ['C:\\Users\\user\\AppData\\Local\\Programs\\Python\\Python314\\python.exe', 'C:\\Users\\user\\AppData\\Local\\Microsoft\\WindowsApps\\python.exe']
- **조치**: PATH에서 불필요한 Python 경로 제거

### [WARN] 가상환경 활성
- **상세**: 가상환경 미활성 (시스템 Python 사용 중)
- **조치**: `.venv\Scripts\activate` 실행 후 다시 검증

### [WARN] 설치 패키지 수
- **상세**: 확인 불가: No module named 'pkg_resources'
- **조치**: 상세 내용을 확인하고 필요시 수동 점검

### [WARN] 이모지 cp949 호환
- **상세**: 이모지는 cp949에서 출력 불가 -> ASCII 대체([OK]/[FAIL]) 사용 필수
- **조치**: 상세 내용을 확인하고 필요시 수동 점검
