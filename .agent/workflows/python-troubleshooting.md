---
description: Python 실행 환경 문제 발생 시 대응 절차 (Windows cmd.exe)
---

# Python 실행 환경 트러블슈팅

> Windows cmd.exe 환경에서 Python 실행 문제 발생 시 아래 순서대로 진행합니다.
> 상세 내용은 해당 프로젝트의 `docs/python_troubleshooting_report.md`를 참조하세요.
> Python 경로 중복 문제는 `docs/python_path_duplication_guide.md`를 참조하세요.

## 트러블슈팅 로그 관리

> **필수**: 트러블슈팅 발생 시 로그 파일을 생성하여 별도 관리합니다.

1. 로그 저장 경로: `logs/troubleshooting/`
2. 파일명 규칙: `ts_YYYYMMDD_HHMM_<문제유형>.log`
   - 예시: `ts_20260310_1013_hang.log`, `ts_20260310_1013_encoding.log`
3. 로그 파일에 반드시 포함할 내용:
   ```
   [시각] YYYY-MM-DD HH:MM:SS
   [문제유형] Hang / 고스팅 / 인코딩 / 기타
   [증상] 구체적 오류 메시지 또는 현상
   [환경] Python 버전, 가상환경 여부, 스크립트 경로
   [조치] 수행한 해결 방법
   [결과] 해결 여부, 소요 시간
   ```
4. 스크립트에서 자동 로그 생성 시:
   ```python
   import os, datetime
   log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'troubleshooting')
   os.makedirs(log_dir, exist_ok=True)
   ts = datetime.datetime.now().strftime('%Y%m%d_%H%M')
   log_path = os.path.join(log_dir, f'ts_{ts}_issue.log')
   ```

## 사전 예방 (스크립트 작성 시)

1. 모든 `.py` 파일 상단에 UTF-8 래퍼를 추가합니다:
```python
import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
```

2. 이모지/특수문자 사용을 금지합니다 — ASCII 호환 문자만 사용:
   - `[OK]` / `[FAIL]` / `[WARN]` / `[INFO]`

3. `python -c "..."` 인라인 실행을 금지합니다 — 반드시 `.py` 파일로 저장 후 실행

4. `find_raw_file` 등 파일 검색 함수에는 반드시 확장자(`.csv`) 필터를 포함합니다

5. 대용량 CSV(10MB+) 처리 시 `send_command_input`의 `WaitMs`를 최소 30000 이상으로 설정합니다

6. `run_command`로 직접 python 실행을 시도하여 실패하면 재시도 없이 즉시 표준 절차(빈 터미널 + `send_command_input`)로 전환합니다

7. 스크립트는 `Cwd`를 스크립트 디렉토리로 설정 후 상대 경로로 실행합니다 (절대경로 직접 전달 지양)

## 표준 실행 절차 (모든 Python 스크립트 실행 시)

> **중요**: `run_command`의 `CommandLine` 인수는 터미널 고스팅으로 인해
> 전달되지 않는 경우가 빈번합니다. 아래 절차를 기본으로 사용합니다.
> **필수**: 프로젝트 실행 시 반드시 `.venv\Scripts\activate`를 먼저 실행합니다.

// turbo
1. `run_command`로 빈 터미널을 생성합니다 (CommandLine에는 `cmd`만 지정):
```
CommandLine: "cmd"
Cwd: (스크립트가 있는 디렉토리 또는 프로젝트 루트)
SafeToAutoRun: true
WaitMsBeforeAsync: 500
```

2. `send_command_input`으로 가상환경 활성화 + 환경변수 설정 + 스크립트 실행 명령을 전송합니다:
```
Input: ".venv\\Scripts\\activate && set PYTHONUNBUFFERED=1 && set PYTHONIOENCODING=utf-8 && python -u script.py\n"
WaitMs: 10000  (스크립트 예상 실행 시간에 맞게 조정)
```

3. 출력을 확인하고, 필요 시 `command_status`로 추가 대기합니다.

## 문제 A: Python 실행 Hang

// turbo
1. 좀비 프로세스 정리:
```bat
taskkill /F /IM python.exe /T
timeout /t 2 /nobreak >nul
```

2. 새 터미널에서 동작 확인:
```bat
python --version
```

// turbo
3. 환경변수 설정 후 unbuffered 모드로 실행:
```bat
set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8
set PYTHONDONTWRITEBYTECODE=1
python -u scripts\your_script.py
```

## 문제 B: 터미널 고스팅 (명령이 실행 안 됨)

> run_command의 CommandLine이 터미널에 전달되지 않는 경우

### 증상
- `run_command` 실행 후 프롬프트만 표시되고 명령이 실행되지 않음
- `command_status`로 확인해도 출력이 프롬프트뿐임
- 반복 시도해도 동일한 현상 지속

### 원인
- Windows cmd.exe 환경에서 `run_command`의 `CommandLine` 인수가
  터미널 프로세스에 전달되지 않는 간헐적 문제
- 긴 명령줄, 특수 문자, 인용부호 등이 원인이 될 수 있음

### 해결 절차

// turbo
1. 기존 터미널이 있으면 종료합니다:
```
send_command_input: Terminate=true
```

// turbo
2. `run_command`로 빈 터미널만 생성합니다:
```
CommandLine: "cmd"
SafeToAutoRun: true
WaitMsBeforeAsync: 500
```

3. `send_command_input`으로 실제 명령을 전송합니다:
```
Input: "set PYTHONUNBUFFERED=1 && python -u scripts\your_script.py\n"
```

### 예방 체크리스트
- [ ] `run_command`의 `CommandLine`에 직접 Python 명령을 넣지 않았는가?
- [ ] `python -c "..."` 인라인 실행을 사용하지 않았는가?
- [ ] 표준 실행 절차(빈 터미널 + send_command_input)를 따랐는가?

## 문제 B-2: 승인 대기 알림

> `SafeToAutoRun=false`로 보낸 명령은 사용자가 VS Code에서 "Run" 버튼을 클릭해야 실행됩니다.
> 사용자가 다른 탭을 보고 있으면 승인 프롬프트를 놓칠 수 있습니다.

### 규칙
- `SafeToAutoRun=false` 명령 전송 후 `command_status`로 15초 대기한다
- 15초 경과 후에도 `RUNNING` 상태이고 출력에 변화가 없으면, `notify_user`로 알림을 보낸다:
  ```
  "⚠️ O개의 터미널 명령이 승인 대기 중입니다. VS Code 터미널 탭에서 'Run' 버튼을 클릭해 주세요."
  ```
- **5개 이상** 승인 대기 중에는 **추가 명령을 보내지 않는다** (대기 명령이 쌓이는 것을 방지)


## 문제 C: 인코딩 오류 (UnicodeEncodeError)

1. 스크립트 상단에 UTF-8 래퍼가 있는지 확인
2. 이모지/특수문자 → ASCII 대체 문자로 변경
3. 환경변수 확인: `set PYTHONIOENCODING=utf-8`
4. CSV 저장 시 `encoding='utf-8-sig'` 사용 (Excel 호환)
