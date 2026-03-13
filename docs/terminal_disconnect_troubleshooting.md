# VS Code 터미널 연결 끊김 (프로세스 연결 끊김) 대응 가이드

> **작성일**: 2026-03-10
> **환경**: Windows 10, VS Code, cmd.exe

## 증상

- VS Code 터미널에서 **"프로세스에 대한 연결 끊김"** 메시지가 표시됨
- 터미널 프로세스(cmd.exe / python.exe)가 갑자기 비활성화됨
- 명령 입력이 불가능하고 터미널이 먹통 상태

## 원인

| 원인                   | 설명                                                                    |
| ---------------------- | ----------------------------------------------------------------------- |
| **Persistent Session** | VS Code가 비활성 터미널을 유지하려다 프로세스 응답 실패 시 연결 끊김    |
| **터미널 고스팅**      | `run_command`의 CommandLine이 전달되지 않는 Windows cmd.exe 간헐적 문제 |
| **좀비 프로세스**      | 미종료 python.exe 프로세스가 리소스를 점유하여 새 터미널 불안정         |
| **안티바이러스 간섭**  | Windows Defender 등이 python.exe 프로세스를 스캔/차단                   |

## 즉시 조치

### 1. 끊긴 터미널 정리

끊긴 터미널 탭의 휴지통 아이콘을 클릭하여 닫습니다.

### 2. 좀비 프로세스 정리

```bat
taskkill /F /IM python.exe /T
timeout /t 2 /nobreak >nul
```

### 3. 새 터미널 열기 후 재실행

```bat
.venv\Scripts\activate && set PYTHONUNBUFFERED=1 && set PYTHONIOENCODING=utf-8 && python -u script.py
```

## 예방 설정 (VS Code settings.json)

아래 설정을 `settings.json`에 추가합니다:

```json
{
    "terminal.integrated.enablePersistentSessions": false,
    "terminal.integrated.persistentSessionReviveProcess": "never"
}
```

| 설정                             | 값        | 효과                                                 |
| -------------------------------- | --------- | ---------------------------------------------------- |
| `enablePersistentSessions`       | `false`   | 터미널 세션 유지 비활성화, 끊긴 세션을 잡아두지 않음 |
| `persistentSessionReviveProcess` | `"never"` | VS Code 재시작 시 이전 터미널 복원 시도 안 함        |

## 추가 예방 체크리스트

- [ ] Python 스크립트 실행 시 반드시 `.venv\Scripts\activate` 먼저 실행
- [ ] `run_command`의 CommandLine에 직접 Python 명령을 넣지 않기 (빈 터미널 + `send_command_input` 사용)
- [ ] 스크립트 상단에 UTF-8 래퍼 포함
- [ ] 이모지/특수문자 대신 ASCII 대체 문자 (`[OK]`, `[FAIL]`) 사용

## 관련 문서

- [python-troubleshooting.md](file:///d:/git_rk/.agent/workflows/python-troubleshooting.md) — Python 실행 환경 트러블슈팅 워크플로우
