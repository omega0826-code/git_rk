# 트러블슈팅 가이드

## 일반 오류

| 에러 | 원인 | 해결 |
|---|---|---|
| `ModuleNotFoundError: parser` | sys.path 미등록 | chart 폴더에서 직접 실행하거나 run_ppt.py 사용 |
| `UnicodeDecodeError` | 인코딩 문제 | 입력 파일이 UTF-8인지 확인 |
| `FileNotFoundError` | 경로 문제 | 절대경로 사용 권장 |

## 파서 오류

| 에러 | 원인 | 해결 |
|---|---|---|
| `ImportError: xlrd` | xlrd 미설치 | `pip install xlrd>=2.0.1` |
| 빈 데이터 추출 | SPSS 표 구조 불일치 | 로그에서 SKIP된 표 확인 |
| MD 파싱 실패 | `## 번호. 제목` 패턴 불일치 | 마크다운 헤딩 형식 확인 |

## 차트 오류

| 에러 | 원인 | 해결 |
|---|---|---|
| `json.JSONDecodeError` | 테마 JSON 문법 | JSON 유효성 검사기로 확인 |
| 파이 항목 10개 초과 | 팔레트 색상 자동 순환 | 필요시 팔레트에 색상 추가 |
| 레이더 데이터 부족 | 3개 미만 항목 | rule 수정하여 최소 3항목 체크 |

## 환경 오류

| 에러 | 원인 | 해결 |
|---|---|---|
| Python 3.8 미만 | f-string 등 미지원 | Python 3.9+ 사용 |
| 터미널 고스팅 | cmd/PowerShell 충돌 | `taskkill /F /IM python.exe /T` 실행 |

## 로그 확인 방법
```bash
# 최근 로그 확인
dir ppt_automation\logs\

# 특정 날짜 로그 보기
type ppt_automation\logs\260311_2100_chart.log
```

- `[OK]` — 정상 생성
- `[SKIP]` — 데이터 없거나 패턴 제외
- `[ERROR]` — 오류 발생 (상세 메시지 확인)
