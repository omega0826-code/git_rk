# Python 경로 중복 해결 가이드

> **작성일**: 2026-03-10
> **환경**: Windows 10/11, Python 3.14.x

---

## 1. 문제 현상

`where python` 실행 시 **2개 이상의 경로**가 표시됩니다:

```
C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe   ← 실제 Python
C:\Users\user\AppData\Local\Microsoft\WindowsApps\python.exe       ← Microsoft Store 별칭
```

**영향**:
- 잘못된 Python이 실행될 수 있음
- 가상환경 내 패키지가 인식되지 않는 문제 발생
- 스크립트 실행 시 예기치 않은 오류 가능

---

## 2. 원인

Windows 10/11에는 Microsoft Store로 Python 설치를 유도하는 **앱 실행 별칭(App Execution Alias)**이 기본 활성화되어 있습니다. 이 별칭은 실제 Python이 아니라 Store 설치 페이지로 리디렉션하는 더미 실행 파일입니다.

---

## 3. 해결 방법

### 방법 A: 설정 UI에서 비활성화 (권장)

1. **작업표시줄 검색창**에 `앱 실행 별칭` 입력
2. **"앱 실행 별칭 관리"** 클릭
3. 목록에서 아래 항목을 **끔(Off)**으로 전환:
   - `python.exe` → Off
   - `python3.exe` → Off

> **경로**: 설정 > 앱 > 앱 및 기능 > **앱 실행 별칭** (파란색 링크)

### 방법 B: 명령줄에서 확인 및 조치

```bat
:: 1. 현재 Python 경로 확인
where python

:: 2. WindowsApps 경로가 포함되어 있으면 PATH에서 제거
:: 시스템 환경변수 편집: Win+R > sysdm.cpl > 고급 > 환경 변수
:: PATH에서 아래 경로가 있으면 제거:
:: C:\Users\<사용자>\AppData\Local\Microsoft\WindowsApps
```

> [!CAUTION]
> `WindowsApps` 경로를 PATH에서 완전히 제거하면 다른 Store 앱에 영향을 줄 수 있습니다.
> **방법 A(별칭 비활성화)가 더 안전합니다.**

---

## 4. 확인

조치 후 새 터미널(cmd)을 열고 확인:

```bat
:: Python 경로가 1개만 나와야 정상
where python
:: 기대 결과: C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe

:: 버전 확인
python --version
:: 기대 결과: Python 3.14.2
```

---

## 5. 추가: 가상환경 사용 시

프로젝트별로 `.venv`를 사용하면 경로 충돌 문제를 근본적으로 방지할 수 있습니다:

```bat
:: 가상환경 활성화 후에는 .venv 내부의 Python만 사용됨
.venv\Scripts\activate

:: 확인
where python
:: 기대 결과: d:\git_rk\.venv\Scripts\python.exe (가상환경 내부)
```
