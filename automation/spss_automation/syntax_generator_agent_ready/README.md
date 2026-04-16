# SPSS Syntax Generator Agent Bundle

이 폴더는 `AI 에이전트 전달용`으로 분리한 self-contained 실행 폴더입니다.

목표:
- 이 폴더만 전달해도 실행 가능
- 웹 UI 사용자와 AI 에이전트 둘 다 같은 폴더를 사용 가능
- 에이전트는 `agent_runner.py`만 보면 호출 방법을 바로 이해 가능

## 루트 진입점

- `agent_runner.py`
  에이전트 전용 CLI 진입점. 결과를 JSON manifest로 stdout에 출력합니다.
- `app.py`
  Flask 기반 웹 UI 서버
- `start.bat`
  사람용 웹 UI 실행기
- `launch_web_ui.hta`
  Windows HTML 실행기

## 빠른 시작

### 1. 에이전트 실행

```bash
python agent_runner.py guideline-to-sps --csv examples/guideline_sample.csv --job-id demo_label
```

```bash
python agent_runner.py generate-macros --config macros/banner_config_sample.json --job-id demo_macro
```

```bash
python agent_runner.py generate-syntax --config examples/analysis_config_sample.json --label-sps runs/demo_label/label.sps --job-id demo_syntax
```

모든 실행 결과는 `runs/<job_id>/` 아래에 생성됩니다.

### 2. 웹 UI 실행

```bat
start.bat
```

또는 `launch_web_ui.hta`를 더블클릭합니다.

## 폴더 구성

- `scripts/`
  실제 생성/변환 코어 스크립트
- `macros/`
  매크로 템플릿 및 샘플 설정
- `examples/`
  샘플 CSV/JSON
- `web/`
  웹 UI 정적 파일
- `runs/`
  에이전트 작업 결과 폴더
- `web_output/`
  웹 UI 세션 출력 폴더

## 권장 전달 방식

오케스트레이션 에이전트에 이 폴더 루트만 전달하고 아래 순서로 쓰는 것을 권장합니다.

1. `README.md`와 `handoff.json` 확인
2. `python agent_runner.py --help` 확인
3. 원하는 서브커맨드 실행
4. stdout JSON의 `outputs` 경로를 다음 단계 입력으로 연결

## 비고

- 상대경로 의존성은 이 폴더 내부 기준으로 맞춰져 있습니다.
- 원본 개발 폴더와 분리돼 있으므로, 에이전트 작업 중 원본을 덜 건드리게 됩니다.
