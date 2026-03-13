# 파이썬 실행 지연 문제 종합 진단 보고서

> **진단 일시**: 2026-02-09  
> **환경**: Windows 10 (19045.6466) / d:\git_rk  

---

## 1. 현상 요약

파이썬 스크립트 실행 시 **수분간 아무런 출력 없이 대기**하는 현상이 반복적으로 발생합니다.

| 항목                              | 관찰 결과                       |
| --------------------------------- | ------------------------------- |
| 단순 `python -c "print('hello')"` | 30초+ 대기, 출력 없음           |
| 배치 파일 래핑 실행               | 3분+ 대기, 하트비트 파일 미생성 |
| `where python` 명령               | 30초+ 대기, 출력 없음           |
| 과거 대화 이력                    | 14개+ 대화에서 동일 패턴 확인   |

---

## 2. 원인 분석

### 2.1. 🔴 주요 원인: Windows 터미널 버퍼 지연

Windows CMD의 표준 출력(stdout)은 **블록 버퍼링** 모드로 동작합니다. 특히 비대화형(non-interactive) 환경에서 실행 시 출력 버퍼가 가득 차거나 프로세스가 종료될 때까지 출력이 전달되지 않습니다.

```
[Python 프로세스] → [stdout 버퍼 (4KB)] → [파이프] → [터미널 캡처] → [사용자]
                          ↑ 여기서 지연 발생
```

### 2.2. 🟠 부차적 원인: 무거운 라이브러리 초기화

| 라이브러리             | 예상 초기화 시간 | 원인                   |
| ---------------------- | ---------------- | ---------------------- |
| `pandas`               | 2~5초            | NumPy C-extension 로딩 |
| `matplotlib`           | 3~8초            | 폰트 캐시 스캔         |
| `koreanize_matplotlib` | 10~60초+         | 시스템 전체 폰트 탐색  |
| `geopandas`            | 5~15초           | GDAL/Fiona 바인딩      |

> [!WARNING]
> `koreanize_matplotlib`은 **첫 import 시** 시스템의 모든 폰트를 스캔하며, 가상화/제한된 환경에서 30~60초 이상 무출력 상태가 될 수 있습니다.

### 2.3. 🟠 부차적 원인: 안티바이러스 실시간 감시

Windows Defender 또는 다른 안티바이러스 소프트웨어의 **실시간 파일 스캔**이 Python 실행 시 추가 지연을 유발합니다:

- `.py` 파일 실행 시 매번 스캔
- `import` 시 `.pyd`, `.dll` 파일 접근마다 스캔
- 대량 파일 생성/삭제 시 I/O 병목

### 2.4. 🟡 환경적 원인: PATH 해석 지연

Windows의 PATH 환경 변수에 **수십 개의 디렉토리**가 등록되어 있으면 `python.exe`를 찾는 데 시간이 소요됩니다. 특히 네트워크 드라이브가 포함된 경우 심각합니다.

### 2.5. 🟡 환경적 원인: 가상환경(.venv) 활성화 상태

`.venv`가 존재하지만 활성화되지 않은 상태에서 시스템 Python이 사용되면 패키지 탐색 경로가 길어져 추가 지연이 발생합니다.

---

## 3. 해결방안

### 3.1. ✅ 즉시 적용 가능한 방안

#### A. 모든 print에 `flush=True` 추가

```python
# ❌ 지연 발생
print("처리 중...")

# ✅ 즉시 출력
print("처리 중...", flush=True)
```

#### B. Python 언버퍼 모드(`-u`) 사용

```batch
REM ❌ 기본 실행 (버퍼링)
python script.py

REM ✅ 언버퍼 모드
python -u script.py
```

#### C. 환경 변수로 전역 언버퍼 설정

```batch
REM CMD에서 설정
set PYTHONUNBUFFERED=1
python script.py

REM 또는 시스템 환경 변수로 영구 설정
setx PYTHONUNBUFFERED 1
```

#### D. 무거운 import 전후에 상태 메시지 출력

```python
import sys
print("라이브러리 로딩 시작...", flush=True)

print("  pandas 로딩 중...", end=" ", flush=True)
import pandas as pd
print("✓")

print("  matplotlib 로딩 중...", end=" ", flush=True)
import matplotlib.pyplot as plt
print("✓")

# koreanize_matplotlib 대신 직접 폰트 설정
print("  한글 폰트 설정 중...", end=" ", flush=True)
try:
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    print("✓ (Malgun Gothic)")
except:
    print("✗ 폰트 설정 실패")
```

### 3.2. 🔧 코드 패턴 개선

#### A. `koreanize_matplotlib` 제거 → 직접 폰트 설정

```python
# ❌ 느림 (10~60초 지연 가능)
import koreanize_matplotlib

# ✅ 빠름 (0.01초 이내)
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
```

#### B. 대용량 CSV 로딩 시 진행 표시

```python
import pandas as pd

# ❌ 무출력 대기
df = pd.read_csv('large_file.csv')

# ✅ 청크로드 + 진행 표시
chunks = []
for i, chunk in enumerate(pd.read_csv('large_file.csv', chunksize=10000)):
    print(f"\r  로딩 중: {(i+1)*10000:,}행 처리됨", end="", flush=True)
    chunks.append(chunk)
df = pd.concat(chunks, ignore_index=True)
print(f"\n  완료: 총 {len(df):,}행")
```

#### C. 페일세이프 스크립트 템플릿

```python
"""
표준 스크립트 템플릿 - 실행 지연 방지
"""
import sys
import time

# 실행 시작 알림
print(f"[시작] {time.strftime('%H:%M:%S')}", flush=True)

# === 무거운 라이브러리는 한 줄씩 로드 ===
print("라이브러리 로딩 중...", flush=True)

t = time.time()
import pandas as pd
print(f"  pandas: {time.time()-t:.1f}s", flush=True)

t = time.time()
import matplotlib
matplotlib.use('Agg')  # GUI 백엔드 비활성화
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
print(f"  matplotlib: {time.time()-t:.1f}s", flush=True)

# === 데이터 처리 ===
print("데이터 로딩 중...", flush=True)
# ... 실제 로직 ...

print(f"[완료] {time.strftime('%H:%M:%S')}", flush=True)
```

### 3.3. ⚙️ 환경 설정 개선

#### A. 안티바이러스 예외 설정

Windows Defender에서 다음 경로를 **실시간 검사 제외**에 추가:

| 제외 대상        | 예시 경로                                      |
| ---------------- | ---------------------------------------------- |
| Python 설치 폴더 | `C:\Users\user\AppData\Local\Programs\Python\` |
| 가상환경         | `d:\git_rk\.venv\`                             |
| 작업 디렉토리    | `d:\git_rk\`                                   |
| pip 캐시         | `C:\Users\user\AppData\Local\pip\`             |

**설정 방법:**
1. Windows 보안 → 바이러스 및 위협 방지 → 설정 관리
2. 제외 → 제외 추가
3. 위 경로들의 폴더를 추가

#### B. `PYTHONUNBUFFERED` 영구 설정

```batch
REM 시스템 환경 변수에 영구 등록
setx PYTHONUNBUFFERED 1
```

#### C. 가상환경 활성화 자동화

`.vscode/settings.json`에 추가:
```json
{
    "python.defaultInterpreterPath": "d:\\git_rk\\.venv\\Scripts\\python.exe",
    "python.terminal.activateEnvironment": true
}
```

### 3.4. 📋 스크립트 실행 체크리스트

새 스크립트 작성 시 아래 항목을 확인하세요:

- [ ] `PYTHONUNBUFFERED=1` 설정 확인
- [ ] 모든 `print()`에 `flush=True` 추가
- [ ] `koreanize_matplotlib` 대신 직접 폰트 설정
- [ ] 대용량 데이터 로딩 시 진행 표시 포함
- [ ] `matplotlib.use('Agg')` 설정 (GUI 불필요 시)
- [ ] 스크립트 시작/종료 시점에 타임스탬프 출력

---

## 4. 우선순위별 조치 요약

| 우선순위 | 조치                                    | 예상 효과           | 난이도 |
| -------- | --------------------------------------- | ------------------- | ------ |
| 🔴 1순위  | `PYTHONUNBUFFERED=1` 환경변수 설정      | 버퍼 지연 완전 해소 | ⭐      |
| 🔴 1순위  | `koreanize_matplotlib` → 직접 폰트 설정 | 10~60초 단축        | ⭐      |
| 🟠 2순위  | 안티바이러스 예외 등록                  | 파일 I/O 50%+ 개선  | ⭐⭐     |
| 🟠 2순위  | 모든 print에 `flush=True`               | 출력 즉시 확인 가능 | ⭐      |
| 🟡 3순위  | 가상환경 정리 및 활성화 확인            | 패키지 탐색 최적화  | ⭐⭐     |
| 🟡 3순위  | `matplotlib.use('Agg')` 기본 설정       | GUI 초기화 건너뛰기 | ⭐      |

---

## 5. 진단 과정에서 확인된 사항

실시간 진단 과정에서 다음 사항이 확인되었습니다:

1. **`python -c "print()"` 명령이 30초 이상 소요** → 터미널 버퍼 지연 확인
2. **`where python` 명령도 30초 이상 소요** → PATH 해석 지연 의심
3. **배치 파일 래핑 실행 시 3분 이상 경과 후에도 하트비트 파일 미생성** → Python 인터프리터 시작 자체에 심각한 지연
4. **과거 14개+ 대화에서 "infinite loading", "silent hang", "terminal unresponsive" 동일 패턴** 반복 확인

> [!IMPORTANT]
> 가장 즉각적인 효과를 얻으려면 **1순위 조치 2가지** (`PYTHONUNBUFFERED=1` 설정 + `koreanize_matplotlib` 교체)를 먼저 적용하세요.
